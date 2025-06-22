def main():
    import argparse
    import logging
    from pathlib import Path
    from forge.agents.test_writer import run_agentic_test_generation

    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser("forge-it agentic test generation")
    parser.add_argument("repo_root", type=str, help="Path to the repo to analyze")
    parser.add_argument("--iterations", type=int, default=3, help="Max revision cycles")
    parser.add_argument("--coverage", type=float, default=90.0, help="Target coverage percentage")

    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()

    logger.info("🚀 Starting agentic test generation")
    logger.info("🔍 Repository root: %s", repo_root)
    logger.info("🔁 Max iterations: %d", args.iterations)
    logger.info("🎯 Target coverage: %.1f%%", args.coverage)

    if not repo_root.exists():
        logger.error("❌ The provided repo path does not exist.")
        return
    if not any(repo_root.rglob("*.py")):
        logger.warning("⚠️ No Python files found in the provided repo path.")
        return

    try:
        run_agentic_test_generation(
            repo_root=repo_root,
            max_iters=args.iterations,
            coverage_target=args.coverage / 100.0
        )
    except Exception as e:
        logger.exception("💥 Unexpected error during test generation: %s", str(e))
    else:
        logger.info("✅ Agentic test generation complete.")
