def normalize(result):
    """
    Converts all node outputs into a consistent schema.
    """

    if isinstance(result, dict):
        return {
            "answer": result.get("answer", ""),
            "source": result.get("source", "unknown"),
            "metadata": result.get("metadata", {})
        }

    return {
        "answer": str(result),
        "source": "unknown",
        "metadata": {}
    }