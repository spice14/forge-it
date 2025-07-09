import argparse
from forge_it.agent import TestGenerationAgent

def main():
    """CLI entry point for Forge-It test generation tool."""
    parser = argparse.ArgumentParser(
        prog="forge-it",
        description="Generate unit tests for a project with >80% coverage using an agentic AI."
    )
    parser.add_argument("target", help="Path to the target project or file for which to generate tests")
    parser.add_argument("--model", default="codestral", help="Name of the local LLM model to use via Ollama")
    parser.add_argument("--max_iter", type=int, default=5, help="Max iterations for test refinement")
    parser.add_argument("--coverage_target", type=float, default=0.8, help="Target coverage (between 0 and 1)")
    args = parser.parse_args()

    agent = TestGenerationAgent(model_name=args.model, coverage_target=args.coverage_target, max_iterations=args.max_iter)
    # Run the generation process
    agent.generate_tests_for_target(args.target)

if __name__ == "__main__":
    main()
