import argparse
import os
import subprocess


SUGAR_DIR = "examples\\interpreting_tests"

parser = argparse.ArgumentParser(description="Process .sugar files by number.")
parser.add_argument(
    "number", type=int, help="0-padded number of the file to process", nargs="?"
)
args = parser.parse_args()
run_all = False
number_str = "00000"


if not args.number:
    run_all = True
else:
    number_str = f"{args.number:02d}"


selected_file = None
selected_files = []
for filename in os.listdir(SUGAR_DIR):
    if filename.endswith(".sugar") and (run_all or filename.startswith(number_str)):
        if filename.startswith("53"):
            continue
        selected_file = os.path.join(SUGAR_DIR, filename)
        selected_files.append(selected_file)


errors = {}

if not selected_file:
    print(f"No .sugar file starting with {number_str} found in {SUGAR_DIR}.")
    exit(1)
for selected_file in selected_files:

    print(f"Processing {selected_file}...")
    result = subprocess.run(
        f"sugar {selected_file} -s", shell=True, capture_output=True, text=True
    )
    out = result.stdout.strip().lower()
    if (
        result.returncode != 0
        or "unexpected" in out
        or "out of range" in out
        or "missing" in out
        or "required positional argument" in out
    ):
        print(
            f"Error processing {selected_file}: {result.stderr.strip()}\n{result.stdout.strip()}"
        )
        errors[selected_file] = f"{result.stderr.strip()}\n{result.stdout.strip()}"
    else:
        # print(f"Successfully processed {selected_file}.")
        print(result.stdout.strip())


print(f"Processed {len(selected_files)} files.")
for file in errors:
    print(f"Error in file: {file}")
    print(errors[file])
