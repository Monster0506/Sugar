"""
Sugar Language Test Runner

This script automatically runs a Sugar interpreter against Sugar source files.
It can test individual files or run comprehensive tests against all example files.

USAGE:
    uv run test_runner.py <interpreter_filename> [options]

ARGUMENTS:
    interpreter_filename    Required. The uv run file containing the Sugar interpreter
                           (e.g., "interpreter.py")

OPTIONS:
    -f, --file FILE        Run interpreter against a specific .sugar file
    -d, --directory DIR    Run interpreter against all .sugar files in a directory
    --examples-only        Run only against files in examples/ directory (default behavior)
    --tests-only           Run only against files in examples/interpreting_tests/ directory
    --all                  Run against both examples/ and examples/interpreting_tests/ directories
    -v, --verbose          Enable verbose output showing interpreter stdout/stderr
    -q, --quiet            Suppress progress output, show only summary
    --stop-on-error        Stop execution on first error instead of continuing
    --timeout SECONDS      Set timeout for each interpreter run (default: 30 seconds)

EXAMPLES:
    # Run interpreter.py against all example files (default behavior)
    uv run test_runner.py interpreter.py

    # Run against a specific file
    uv run test_runner.py interpreter.py -f examples/hello.sugar

    # Run against all files in interpreting_tests with verbose output
    uv run test_runner.py interpreter.py --tests-only -v

    # Run against all files with timeout and stop on first error
    uv run test_runner.py interpreter.py --all --timeout 60 --stop-on-error

DEFAULT BEHAVIOR:
    When no file or directory is specified, the script runs the interpreter against:
    - All .sugar files in examples/ directory
    - All .sugar files in examples/interpreting_tests/ directory

OUTPUT:
    The script shows progress for each file tested and provides a summary at the end
    showing successful runs, failures, and any files that timed out.

EXIT CODES:
    0 - All tests passed
    1 - Some tests failed
    2 - Invalid arguments or interpreter not found
"""

import argparse
import glob
import os
import subprocess
import sys
import time
from typing import List


class RunResult:
    """Represents the result of running the interpreter on a single file."""

    def __init__(
        self,
        filename: str,
        success: bool,
        runtime: float,
        stdout: str = "",
        stderr: str = "",
        error_msg: str = "",
    ):
        self.filename = filename
        self.success = success
        self.runtime = runtime
        self.stdout = stdout
        self.stderr = stderr
        self.error_msg = error_msg


class SugarTestRunner:
    """Main test runner class for Sugar interpreter tests."""

    def __init__(
        self,
        interpreter_file: str,
        timeout: int = 30,
        verbose: bool = False,
        quiet: bool = False,
        stop_on_error: bool = False,
    ):
        self.interpreter_file = interpreter_file
        self.timeout = timeout
        self.verbose = verbose
        self.quiet = quiet
        self.stop_on_error = stop_on_error
        self.results: List[RunResult] = []

        # Verify interpreter file exists
        if not os.path.isfile(interpreter_file):
            raise FileNotFoundError(f"Interpreter file not found: {interpreter_file}")

    def find_sugar_files(self, directory: str) -> List[str]:
        """Find all .sugar files in the given directory."""
        pattern = os.path.join(directory, "**", "*.sugar")
        files = glob.glob(pattern, recursive=True)
        return sorted(files)

    def run_interpreter_on_file(self, sugar_file: str) -> RunResult:
        """Run the interpreter on a single Sugar file and return the result."""
        start_time = time.time()

        try:
            # Build command to run interpreter
            cmd = [sys.executable, self.interpreter_file, sugar_file]

            if self.verbose and not self.quiet:
                print(f"Running: {' '.join(cmd)}")

            # Run interpreter with timeout
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=self.timeout
            )

            runtime = time.time() - start_time
            success = result.returncode == 0

            return RunResult(
                filename=sugar_file,
                success=success,
                runtime=runtime,
                stdout=result.stdout,
                stderr=result.stderr,
                error_msg="" if success else f"Return code: {result.returncode}",
            )

        except subprocess.TimeoutExpired:
            runtime = time.time() - start_time
            return RunResult(
                filename=sugar_file,
                success=False,
                runtime=runtime,
                error_msg=f"Timeout after {self.timeout} seconds",
            )
        except Exception as e:
            runtime = time.time() - start_time
            return RunResult(
                filename=sugar_file, success=False, runtime=runtime, error_msg=str(e)
            )

    def run_tests(self, files: List[str]) -> None:
        """Run tests on a list of Sugar files."""
        if not files:
            print("No .sugar files found to test.")
            return

        if not self.quiet:
            print(f"Running tests on {len(files)} files using {self.interpreter_file}")
            print("=" * 60)

        for i, sugar_file in enumerate(files, 1):
            if not self.quiet:
                print(
                    f"[{i:3d}/{len(files)}] Testing {sugar_file}... ",
                    end="",
                    flush=True,
                )

            result = self.run_interpreter_on_file(sugar_file)
            self.results.append(result)

            if not self.quiet:
                if result.success:
                    print(f"PASS: ({result.runtime:.2f}s)")
                else:
                    print(f"FAIL:  ({result.runtime:.2f}s)")
                    if result.error_msg:
                        print(f"    Error: {result.error_msg}")

            # Show verbose output if requested
            if self.verbose and (result.stdout or result.stderr):
                if result.stdout:
                    print(f"    STDOUT:\n{self._indent_text(result.stdout)}")
                if result.stderr:
                    print(f"    STDERR:\n{self._indent_text(result.stderr)}")

            # Stop on error if requested
            if not result.success and self.stop_on_error:
                print(f"\nStopping due to error in {sugar_file}")
                break

    def _indent_text(self, text: str, indent: str = "        ") -> str:
        """Indent each line of text."""
        return "\n".join(indent + line for line in text.splitlines())

    def print_summary(self) -> None:
        """Print a summary of test results."""
        if not self.results:
            return

        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = total - passed
        total_time = sum(r.runtime for r in self.results)

        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total files:    {total}")
        print(f"Passed:         {passed}")
        print(f"Failed:         {failed}")
        print(f"Success rate:   {passed/total*100:.1f}%")
        print(f"Total time:     {total_time:.2f}s")
        print(f"Average time:   {total_time/total:.2f}s per file")

        # Show failed files
        failed_results = [r for r in self.results if not r.success]
        if failed_results:
            print(f"\nFAILED FILES ({len(failed_results)}):")
            for result in failed_results:
                print(f"  FAIL:  {result.filename}")
                if result.error_msg:
                    print(f"    {result.error_msg}")

        print("=" * 60)

    def get_exit_code(self) -> int:
        """Return appropriate exit code based on test results."""
        if not self.results:
            return 2  # No tests run

        failed_count = sum(1 for r in self.results if not r.success)
        return 1 if failed_count > 0 else 0


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Automated test runner for Sugar language interpreter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run test_runner.py interpreter.py
  uv run test_runner.py interpreter.py -f examples/hello.sugar
  uv run test_runner.py interpreter.py --tests-only -v
  uv run test_runner.py interpreter.py --all --timeout 60
        """,
    )

    parser.add_argument(
        "interpreter",
        help="Python file containing the Sugar interpreter (e.g., interpreter.py)",
    )

    parser.add_argument(
        "-f", "--file", help="Run interpreter against a specific .sugar file"
    )

    parser.add_argument(
        "-d",
        "--directory",
        help="Run interpreter against all .sugar files in a directory",
    )

    parser.add_argument(
        "--examples-only",
        action="store_true",
        help="Run only against files in examples/ directory",
    )

    parser.add_argument(
        "--tests-only",
        action="store_true",
        help="Run only against files in examples/interpreting_tests/ directory",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run against both examples/ and examples/interpreting_tests/ directories",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output showing interpreter stdout/stderr",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress progress output, show only summary",
    )

    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop execution on first error instead of continuing",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Set timeout for each interpreter run in seconds (default: 30)",
    )

    return parser.parse_args()


def main():
    """Main entry point for the test runner."""
    try:
        args = parse_arguments()

        # Create test runner
        runner = SugarTestRunner(
            interpreter_file=args.interpreter,
            timeout=args.timeout,
            verbose=args.verbose,
            quiet=args.quiet,
            stop_on_error=args.stop_on_error,
        )

        # Determine which files to test
        files_to_test = []

        if args.file:
            # Test specific file
            if not os.path.isfile(args.file):
                print(f"Error: File not found: {args.file}")
                sys.exit(2)
            files_to_test = [args.file]
        elif args.directory:
            # Test files in specific directory
            if not os.path.isdir(args.directory):
                print(f"Error: Directory not found: {args.directory}")
                sys.exit(2)
            files_to_test = runner.find_sugar_files(args.directory)
        else:
            # Default behavior: test example files
            if args.tests_only:
                files_to_test = runner.find_sugar_files("examples/interpreting_tests")
            elif args.examples_only:
                files_to_test = runner.find_sugar_files("examples")
            elif args.all:
                files_to_test = runner.find_sugar_files(
                    "examples"
                ) + runner.find_sugar_files("examples/interpreting_tests")
            else:
                # Default: test both directories
                files_to_test = runner.find_sugar_files(
                    "examples"
                ) + runner.find_sugar_files("examples/interpreting_tests")

        # Filter out type_errors directory files unless explicitly requested
        if not (args.directory and "type_errors" in args.directory):
            files_to_test = [f for f in files_to_test if "type_errors" not in f]

        # Run tests
        runner.run_tests(files_to_test)

        # Print summary and exit with appropriate code
        runner.print_summary()
        sys.exit(runner.get_exit_code())

    except KeyboardInterrupt:
        print("\nTest run interrupted by user.")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(2)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
