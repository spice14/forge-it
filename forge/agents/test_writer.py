from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from pathlib import Path
from typing import List, Tuple

from forge.modules.llm import generate_initial_test, generate_refined_test
from forge.modules.scan import get_function_spans
from forge.modules.utils import (
    get_test_file_path,
    get_module_import_path,
    run_tests_and_get_coverage,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

COVERAGE_TARGET = 0.90

# ──────────────────────────────── AGENTS ────────────────────────────────

class PlannerAgent:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def plan(self) -> List[Tuple[Path, List[str]]]:
        """Return [(file_path, [func names])] to cover."""
        todo = []
        for py in self.repo_root.rglob("*.py"):
            logger.debug("📄 Scanning file: %s", py)
            if "tests" in py.parts or "__pycache__" in py.parts:
                logger.debug("🛑 Skipped (test/__pycache__): %s", py)
                continue
            spans = get_function_spans(py)
            func_names = [s.get("name") for s in spans if s.get("name")]
            if func_names:
                logger.debug("✅ Added for testing: %s (%s)", py.name, func_names)
                todo.append((py, func_names))
            else:
                logger.debug("🧐 No functions found in: %s", py)
        logger.info("Planner found %d source files", len(todo))
        return todo


class TestGeneratorAgent:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def generate(self, file: Path, funcs: List[str]) -> Path:
        code = file.read_text()
        import_path = get_module_import_path(str(file), str(self.repo_root))
        test_code = generate_initial_test(
            source_code=code,
            module_import_path=import_path,
            func_names=funcs,
            repo_root=self.repo_root
        )
        out_path = Path(get_test_file_path(str(file), str(self.repo_root)))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(test_code)
        logger.info("Generated %s", out_path)
        return out_path

class EvaluatorAgent:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def evaluate(self):
        return run_tests_and_get_coverage(str(self.repo_root))

class RefinerAgent:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def refine(self, failing: List[Path], pytest_output: str):
        for path in failing:
            test_code = path.read_text()

            # Try to resolve corresponding source file
            rel_path = path.relative_to(self.repo_root)
            module_name = rel_path.stem.replace("test_", "") + ".py"
            possible_path = self.repo_root / rel_path.parent.parent / module_name

            if possible_path.exists():
                source_code = possible_path.read_text()
            else:
                source_code = ""
                logger.warning("Could not locate source for test: %s", path.name)

            refined = generate_refined_test(
                original_test=test_code,
                pytest_output=pytest_output,
                source_code=source_code
            )
            path.write_text(refined)
            logger.info("Refined %s", path)

# ─────────────────────────────── LOOP ───────────────────────────────────

def run_agentic_test_generation(repo_root: Path, max_iters=3,
                                coverage_target=COVERAGE_TARGET):
    planner   = PlannerAgent(repo_root)
    generator = TestGeneratorAgent(repo_root)
    evaluator = EvaluatorAgent(repo_root)
    refiner   = RefinerAgent(repo_root)

    for file, funcs in planner.plan():
        generator.generate(file, funcs)

    for i in range(1, max_iters + 1):
        logger.info("─ Iteration %d/%d ─", i, max_iters)
        cov, out = evaluator.evaluate()
        logger.info("coverage = %.1f %%", cov * 100)
        if cov >= coverage_target:
            break

        bad = [repo_root / l.split(":")[0]
               for l in out.splitlines()
               if l.startswith("tests/") and ":" in l]

        if not bad:
            bad = list(repo_root.glob("tests/**/*.py"))

        refiner.refine(bad, out)

    final_cov, _ = evaluator.evaluate()
    logger.info("✓ final coverage: %.1f %%", final_cov * 100)
