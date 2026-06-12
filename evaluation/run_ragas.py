"""
RAGAS evaluation harness for the CineLex RAG pipeline.

Judge = Groq (free tier) via langchain-groq; embeddings = HF all-MiniLM-L6-v2.
These are *eval-only* dependencies (the app itself is now fully live on TMDB and
uses no embeddings) — install them with ``pip install -r requirements-eval.txt``.
No paid API required.

The Groq generator (system-under-test) and the Groq judge share the free-tier
quota, so evaluation runs single-threaded with a small question set.

Usage:
    python evaluation/run_ragas.py                  # baseline, k=3
    python evaluation/run_ragas.py --k 5            # single run at k=5
    python evaluation/run_ragas.py --experiment     # baseline (k=3) vs improved (k=5)
    python evaluation/run_ragas.py --ablation       # facets OFF vs ON (the concept-retrieval upgrade)
    python evaluation/run_ragas.py --retrieval      # fast title hit-rate@k, no judge/embeddings
    python evaluation/run_ragas.py --limit 3        # smoke test on 3 questions
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv()

from ragas import evaluate, EvaluationDataset
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from ragas.run_config import RunConfig
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

from cinellex_rag.retrieval.rag import handle_rag

# Eval-only embedding model. The app no longer builds a vector store, so RAGAS
# brings its own embeddings purely to score its similarity-based metrics.
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Groq's chat API only allows n=1. answer_relevancy defaults to strictness=3
# (which asks the judge for n=3 generations per call) → 400 error. Force n=1.
answer_relevancy.strictness = 1

GT_PATH = PROJECT_ROOT / "evaluation" / "ground_truth.json"
RESULTS_DIR = PROJECT_ROOT / "evaluation" / "results"

METRICS = [faithfulness, answer_relevancy, context_precision, context_recall]
INPUT_COLS = {"user_input", "response", "retrieved_contexts", "reference"}


def build_samples(questions, k, use_facets=True):
    """Run the RAG pipeline for each question, capturing answer + contexts.

    Fuzzy short-circuit is disabled so RAGAS evaluates the real retriever.
    ``use_facets`` toggles the concept (keyword/genre) retrieval upgrade.
    """
    samples = []
    for i, item in enumerate(questions, 1):
        q = item["question"]
        print(f"  [{i}/{len(questions)}] generating: {q[:60]}...")
        res = handle_rag(q, k=k, use_fuzzy=False, use_facets=use_facets)
        samples.append({
            "user_input": q,
            "response": res["answer"],
            "retrieved_contexts": res["metadata"].get("contexts", []),
            "reference": item["ground_truth"],
        })
    return samples


def _expected_title(ground_truth: str) -> str:
    """The film title at the head of a ground-truth string, e.g.
    'The Godfather, directed by ...' → 'The Godfather'."""
    head = ground_truth.split(", directed")[0]
    head = head.split(",")[0].split(".")[0]
    return head.strip().lower()


def retrieval_hitrate(questions, k, use_facets):
    """Judge-free metric: fraction of questions whose expected film appears in
    the top-k retrieved cards. Directly measures the concept-retrieval upgrade
    without spending RAGAS judge quota."""
    hits = 0
    for i, item in enumerate(questions, 1):
        q = item["question"]
        want = _expected_title(item["ground_truth"])
        res = handle_rag(q, k=k, use_fuzzy=False, use_facets=use_facets)
        titles = [(m.get("title") or "").lower() for m in res.get("movies", [])]
        hit = any(want and (want in t or t in want) for t in titles)
        hits += hit
        mark = "HIT " if hit else "miss"
        print(f"  [{i}/{len(questions)}] {mark} want={want!r:35} got={titles}")
    return round(hits / len(questions), 4) if questions else 0.0


def get_judge():
    model = os.environ.get("RAGAS_JUDGE_MODEL", "llama-3.1-8b-instant")
    llm = ChatGroq(
        model=model,
        api_key=os.environ.get("GROQ_API_KEY"),
        temperature=0,
    )
    return LangchainLLMWrapper(llm)


def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def run_eval(questions, k, judge, embeddings, run_config, use_facets=True):
    samples = build_samples(questions, k, use_facets=use_facets)
    dataset = EvaluationDataset.from_list(samples)

    result = evaluate(
        dataset=dataset,
        metrics=METRICS,
        llm=judge,
        embeddings=embeddings,
        run_config=run_config,
    )

    # Aggregate to mean per metric (robust to RAGAS metric naming).
    df = result.to_pandas()
    metric_cols = [c for c in df.columns if c not in INPUT_COLS]
    return {c: round(float(df[c].mean()), 4) for c in metric_cols}


def print_table(title, scores):
    print(f"\n{title}")
    print("-" * 48)
    for name, val in scores.items():
        print(f"  {name:<34} {val:.4f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="limit number of questions (smoke test)")
    parser.add_argument("--k", type=int, default=3, help="retriever top-k")
    parser.add_argument("--experiment", action="store_true", help="run baseline (k=3) vs improved (k=5)")
    parser.add_argument("--ablation", action="store_true", help="RAGAS: facets OFF vs ON at --k")
    parser.add_argument("--retrieval", action="store_true", help="fast title hit-rate@k, facets OFF vs ON (no judge)")
    args = parser.parse_args()

    questions = json.loads(GT_PATH.read_text(encoding="utf-8"))
    if args.limit:
        questions = questions[:args.limit]

    # Fast, judge-free retrieval ablation — measures the concept-retrieval fix
    # directly (does the right film get retrieved?) without RAGAS/embeddings.
    if args.retrieval:
        print(f"\n=== retrieval hit-rate@{args.k} on {len(questions)} questions ===")
        print("\n-- facets OFF (legacy title search) --")
        off = retrieval_hitrate(questions, args.k, use_facets=False)
        print("\n-- facets ON (concept retrieval) --")
        on = retrieval_hitrate(questions, args.k, use_facets=True)
        print("\n" + "-" * 48)
        print(f"  hit-rate facets OFF: {off:.4f}")
        print(f"  hit-rate facets ON : {on:.4f}")
        print(f"  delta              : {on - off:+.4f}")
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        out_path = RESULTS_DIR / "retrieval_hitrate.json"
        out_path.write_text(json.dumps(
            {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "k": args.k,
             "num_questions": len(questions), "facets_off": off, "facets_on": on},
            indent=2), encoding="utf-8")
        print(f"\nSaved -> {out_path}")
        return

    judge = get_judge()
    embeddings = LangchainEmbeddingsWrapper(get_embeddings())
    run_config = RunConfig(max_workers=1, timeout=180, max_retries=5)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # (name, k, use_facets)
    if args.ablation:
        configs = [("facets_off", args.k, False), ("facets_on", args.k, True)]
    elif args.experiment:
        configs = [("baseline", 3, True), ("improved", 5, True)]
    else:
        configs = [("baseline", args.k, True)]

    runs = {}
    for name, k, use_facets in configs:
        print(f"\n=== {name} (k={k}, facets={use_facets}) on {len(questions)} questions ===")
        scores = run_eval(questions, k, judge, embeddings, run_config, use_facets=use_facets)
        runs[name] = {"k": k, "facets": use_facets, "num_questions": len(questions), "scores": scores}
        print_table(f"{name} scores (k={k})", scores)

    pair = (("baseline", "improved") if args.experiment
            else ("facets_off", "facets_on") if args.ablation else None)
    if pair and pair[0] in runs and pair[1] in runs:
        lo, hi = pair
        print(f"\n=== improvement: {hi} - {lo} ===")
        print("-" * 48)
        base, imp = runs[lo]["scores"], runs[hi]["scores"]
        for name in base:
            if name in imp:
                delta = imp[name] - base[name]
                arrow = "up" if delta > 0 else ("down" if delta < 0 else "same")
                print(f"  {name:<34} {delta:+.4f} {arrow}")

    out = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "runs": runs}
    fname = "ablation.json" if args.ablation else "experiment.json" if args.experiment else "baseline.json"
    out_path = RESULTS_DIR / fname
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nSaved -> {out_path}")


if __name__ == "__main__":
    main()
