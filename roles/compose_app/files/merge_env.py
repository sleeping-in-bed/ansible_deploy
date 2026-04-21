#!/usr/bin/env python3
"""Merge multiple .env files and output to a single file."""

import argparse
from pathlib import Path


def merge_env_files(merged_env_file: str, env_file_paths: list[str]) -> None:
    """Merge env files by reading each file and writing to output file."""
    merged_file = Path(merged_env_file)
    merged_file.parent.mkdir(parents=True, exist_ok=True)

    missing_files: list[str] = []
    wrote_any: bool = False

    with merged_file.open("w", encoding="utf-8") as output:
        for env_path in env_file_paths:
            env_file = Path(env_path)
            if not env_file.exists():
                missing_files.append(env_path)
                continue

            content = env_file.read_text(encoding="utf-8")
            if content:
                wrote_any = True
            output.write(content)
            if not content.endswith("\n"):
                output.write("\n")

    if missing_files:
        missing_str = ", ".join(missing_files)
        msg = f"Missing env files: {missing_str}"
        raise FileNotFoundError(msg)

    if not wrote_any:
        msg = f"No content written from env files: {env_file_paths}"
        raise ValueError(msg)

    # Ensure readable permissions for the merged file
    merged_file.chmod(0o644)


def main() -> None:
    """Execute the main function to merge environment files."""
    parser = argparse.ArgumentParser(description="Merge multiple .env files")
    parser.add_argument("merged_env_file", type=str, help="Output merged env file path")
    parser.add_argument("env_file_paths", nargs="+", help="Input env file paths")

    args = parser.parse_args()

    merge_env_files(args.merged_env_file, args.env_file_paths)


if __name__ == "__main__":
    main()
