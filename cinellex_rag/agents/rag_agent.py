import json
from cinellex_rag.graph.graph import run_graph

COMMANDS = ["cls", "clear"]
EXIT_COMMANDS = ["exit", "quit", "q"]


def format_answer(result):
    if not isinstance(result, dict):
        return str(result)

    answer = result.get("answer", "")

    # Strip set-style braces the LLM sometimes returns: { "item1", "item2" }
    stripped = answer.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        stripped = stripped[1:-1]
        lines = [
            l.strip().strip('"').strip(",")
            for l in stripped.split("\n") if l.strip()
        ]
        return "\n".join(f"{i+1}. {l}" for i, l in enumerate(lines) if l)

    # Try valid JSON dict (e.g. {"title": {"rating": 9.3}})
    try:
        parsed = json.loads(answer)
        if isinstance(parsed, dict):
            lines = []
            for i, (title, info) in enumerate(parsed.items(), 1):
                if isinstance(info, dict) and "rating" in info:
                    lines.append(f"{i}. {title} — Rating: {info['rating']}")
                else:
                    lines.append(f"{i}. {title}")
            return "\n".join(lines)
    except (json.JSONDecodeError, TypeError):
        pass

    return answer


def is_valid_query(query: str) -> bool:
    q = query.lower().strip()

    if len(q) < 4:
        return False

    movie_keywords = [
        "movie", "film", "tell", "about", "top", "worst", "best",
        "list", "director", "actor", "plot", "story", "cast", "who",
        "what", "when", "how", "latest", "recent", "highest", "rating",
        "recommend", "suggest", "similar", "like"
    ]

    has_keyword = any(word in q for word in movie_keywords)
    has_space = " " in q

    if not has_keyword and not has_space:
        return False

    return True


def main():
    print("🎬 CineLex AI (LangGraph Mode). Type 'exit' to quit.\n")

    while True:
        query = input("Enter your question: ").strip()

        if not query:
            continue

        if query.lower() in EXIT_COMMANDS:
            print("Goodbye!")
            break

        if query.lower() in COMMANDS:
            print("\033c", end="")
            continue

        if not is_valid_query(query):
            print("❌ Please ask a movie-related question (e.g. 'top 5 movies', 'tell me about Inception').\n")
            continue

        response = run_graph(query)
        print("\nAnswer:")
        print(format_answer(response.get("result")))
        print("\n")


if __name__ == "__main__":
    main()