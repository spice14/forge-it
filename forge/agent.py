import os
import shutil
import importlib.util
from forge_it import model, runner, coverage_util

class TestGenerationAgent:
    """Agent that generates and iteratively refines unit tests for a given target codebase."""
    def __init__(self, model_name: str = "codestral", coverage_target: float = 0.8, max_iterations: int = 5):
        self.model_name = model_name
        self.coverage_target = coverage_target
        self.max_iterations = max_iterations
        # Directory to store generated test files
        self.gen_test_dir = "__generated_tests__"
        os.makedirs(self.gen_test_dir, exist_ok=True)
        # Counter for test file versions
        self.test_file_index = 1

    def generate_tests_for_target(self, target_path: str):
        """Main entry to generate tests for a target file or all python files in a directory."""
        # Determine files to generate tests for
        target_files = []
        if os.path.isdir(target_path):
            # Collect all .py files in the directory (could be improved to exclude certain files)
            for root, _, files in os.walk(target_path):
                for f in files:
                    if f.endswith(".py") and not f.startswith("test_"):
                        target_files.append(os.path.join(root, f))
        else:
            target_files.append(target_path)
        if not target_files:
            print(f"No target Python files found in {target_path}")
            return

        print(f"Found {len(target_files)} target files. Generating tests...")
        for file_path in target_files:
            try:
                self._generate_tests_for_file(file_path)
            except Exception as e:
                print(f"Error generating tests for {file_path}: {e}")

    def _generate_tests_for_file(self, file_path: str):
        """Generate tests for a single file, iterating until coverage target is met or max iterations reached."""
        # Read the source code to supply to the model
        with open(file_path, "r") as f:
            code_content = f.read()
        file_name = os.path.basename(file_path)
        # Prepare initial prompt for zero-shot test generation
        prompt = self._build_initial_prompt(code_content, file_name)
        print(f"\n[Agent] Generating initial tests for {file_name} using model '{self.model_name}'...")
        test_code = model.generate_tests(prompt, self.model_name)
        test_file_path = self._save_test_file(test_code, file_name)

        iteration = 1
        best_coverage = 0.0
        while iteration <= self.max_iterations:
            # Run tests and gather coverage for the target file
            print(f"[Agent] Running tests (iteration {iteration})...")
            result = runner.run_tests_and_collect(file_path, test_file_path)
            passed = result["all_passed"]
            coverage = result["coverage"]
            best_coverage = max(best_coverage, coverage)
            print(f"[Agent] Iteration {iteration} - coverage: {coverage:.2%}, tests passed: {passed}")
            if passed and coverage >= self.coverage_target:
                print(f"[Agent] Coverage target reached for {file_name}! ({coverage:.2%} coverage)\n")
                break  # success, stop iterating

            # Build feedback prompt for the model
            feedback_prompt = self._build_feedback_prompt(code_content, file_name, result)
            print(f"[Agent] Refining tests for {file_name} (iteration {iteration})...")
            new_test_code = model.generate_tests(feedback_prompt, self.model_name)
            # Overwrite or create new test file with refined tests
            test_file_path = self._save_test_file(new_test_code, file_name, overwrite=True)
            iteration += 1

        if best_coverage < self.coverage_target:
            print(f"[Agent] Finished iterations for {file_name}, but coverage is {best_coverage:.2%} (below target).")
        # Optionally, we could merge or report the generated tests somewhere persistent.

    def _build_initial_prompt(self, code: str, filename: str) -> str:
        """Create the initial prompt for the model to generate tests."""
        return (
            f"You are an AI unit test generator. I will give you a Python source file `{filename}`. "
            f"Generate a comprehensive pytest test suite for it. Aim for readable, logically thorough tests. "
            f"Ensure tests cover as many branches and lines as possible (target > {int(self.coverage_target*100)}% coverage). "
            f"Do not import or use any external libraries not already used in the code. \n\n"
            f"```python\n{code}\n```"
        )

    def _build_feedback_prompt(self, code: str, filename: str, result: dict) -> str:
        """Create a prompt with feedback (coverage gaps or errors) for refining tests."""
        prompt = (
            f"You generated tests for `{filename}`. Some improvements are needed based on feedback:\n"
        )
        # If tests failed, include the error information
        if not result["all_passed"]:
            prompt += f"- Some tests failed with errors or assertions. Here are the failure details:\n```\n{result['error_message']}\n```\n"
            prompt += "Fix any bugs in the tests or assumptions that caused these failures.\n"
        # Include uncovered lines information
        uncovered = result.get("uncovered_lines", [])
        if uncovered:
            prompt += "- The following lines of the code are still not covered by tests:\n"
            for line_no, line_code in uncovered:
                prompt += f"  Line {line_no}: {line_code}\n"
            prompt += "Write new test cases to cover these lines (or related functionality) if possible.\n"
        # Final instruction
        prompt += (
            "Now, provide an updated test file (pytest format) incorporating the above feedback. "
            "Only output the revised test code."
        )
        # Include the original code again for reference (could truncate if very large)
        prompt += f"\n\n```python\n{code}\n```"
        return prompt

    def _save_test_file(self, test_code: str, src_filename: str, overwrite=False) -> str:
        """Save the generated test code to a file. Returns the file path."""
        test_filename = f"test_{src_filename}".replace(".py", "_gen.py")
        if overwrite:
            # Overwrite the same test file (for refinement) 
            file_path = os.path.join(self.gen_test_dir, test_filename)
        else:
            # Save with an index to keep versions (optional)
            file_path = os.path.join(self.gen_test_dir, f"{self.test_file_index}_{test_filename}")
            self.test_file_index += 1
        with open(file_path, "w") as f:
            f.write(test_code)
        # Ensure the generated tests can import the target module:
        # If target is in a package, copy an __init__.py to generated test dir to make it a package, etc.
        # (For simplicity, just ensure sys.path or working dir will allow imports in runner.)
        return file_path
