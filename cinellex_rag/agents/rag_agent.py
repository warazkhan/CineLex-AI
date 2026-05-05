from cinellex_rag.graph.graph import run_graph

def main():
    print("🎬 CineLex AI (LangGraph Mode). Type 'exit' to quit.\n")

    while True:
        query = input("Enter your question: ")

        if query.lower() == "exit":
            break

        response = run_graph(query)

        print("\nAnswer:")
        print(response["result"]["answer"] if isinstance(response["result"], dict) else response["result"])
        print("\n")
        

if __name__ == "__main__":
    main()