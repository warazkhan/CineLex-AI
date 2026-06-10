"""
RAGAS evaluation harness for the CineLex RAG pipeline.

Judge = Groq (free tier) via langchain-groq; embeddings = the same HF
all-MiniLM-L6-v2 the app uses. No paid API required.

The Groq generator (system-under-test) and the Groq judge share the free-tier
quota, so evaluation runs single-threaded with a small question set.

Usage:
    python evaluation/run_ragas.py                  # baseline, k=3
    python evaluation/run_ragas.py --k 5            # single run at k=5
    python evaluation/run_ragas.py --experiment     # baseline (k=3) vs improved (k=5)
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

from cinellex_rag.retrieval.rag import handle_rag
from cinellex_rag.retrieval.vector_store import embedding_model

# Groq's chat API only allows n=1. answer_relevancy defaults to strictness=3
# (which asks the judge for n=3 generations per call) → 400 error. Force n=1.
answer_relevancy.strictness = 1

GT_PATH = PROJECT_ROOT / "evaluation" / "ground_truth.json"
RESULTS_DIR = PROJECT_ROOT / "evaluation" / "results"

METRICS = [faithfulness, answer_relevancy, context_precision, context_recall]
INPUT_COLS = {"user_input", "response", "retrieved_contexts", "reference"}


def build_samples(questions, k):
    """Run the RAG pipeline for each question, capturing answer + contexts.

    Fuzzy short-circuit is disabled so RAGAS evaluates the real retriever.
    """
    samples = []
    for i, item in enumerate(questions, 1):
        q = item["question"]
        print(f"  [{i}/{len(questions)}] generating: {q[:60]}...")
        res = handle_rag(q, k=k, use_fuzzy=False)
        samples.append({
            "user_input": q,
            "response": res["answer"],
            "retrieved_contexts": res["metadata"].get("contexts", []),
            "reference": item["ground_truth"],
        })
    return samples


def get_judge():
    model = os.environ.get("RAGAS_JUDGE_MODEL", "llama-3.1-8b-instant")
    llm = ChatGroq(
        model=model,
        api_key=os.environ.get("GROQ_API_KEY"),
        temperature=0,
    )
    return LangchainLLMWrapper(llm)


def run_eval(questions, k, judge, embeddings, run_config):
    samples = build_samples(questions, k)
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
    args = parser.parse_args()

    questions = json.loads(GT_PATH.read_text(encoding="utf-8"))
    if args.limit:
        questions = questions[:args.limit]

    judge = get_judge()
    embeddings = LangchainEmbeddingsWrapper(embedding_model)
    run_config = RunConfig(max_workers=1, timeout=180, max_retries=5)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    configs = [("baseline", 3), ("improved", 5)] if args.experiment else [("baseline", args.k)]

    runs = {}
    for name, k in configs:
        print(f"\n=== {name} (k={k}) on {len(questions)} questions ===")
        scores = run_eval(questions, k, judge, embeddings, run_config)
        runs[name] = {"k": k, "num_questions": len(questions), "scores": scores}
        print_table(f"{name} scores (k={k})", scores)

    if args.experiment and "baseline" in runs and "improved" in runs:
        print("\n=== improvement: improved(k=5) - baseline(k=3) ===")
        print("-" * 48)
        base, imp = runs["baseline"]["scores"], runs["improved"]["scores"]
        for name in base:
            if name in imp:
                delta = imp[name] - base[name]
                arrow = "up" if delta > 0 else ("down" if delta < 0 else "same")
                print(f"  {name:<34} {delta:+.4f} {arrow}")

    out = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "runs": runs}
    out_path = RESULTS_DIR / ("experiment.json" if args.experiment else "baseline.json")
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nSaved -> {out_path}")


if __name__ == "__main__":
    main()
