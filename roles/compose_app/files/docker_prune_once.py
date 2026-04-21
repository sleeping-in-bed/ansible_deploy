#!/usr/bin/env python3
"""Run Docker prune safely with a per-host file lock so that concurrent
invocations on the same machine only execute once.

The prune policy keeps hot build cache available for fast rebuilds:
- Prune dangling images older than the retention window
- Prune old build cache while preserving a reserved cache budget and
  a minimum amount of free disk space

Exit codes:
- 0: success or skipped because another prune is in progress
- non-zero: unexpected error
"""

import errno
import fcntl
import os
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from typing import TextIO

LOCK_FILE_PATH = os.environ.get("DOCKER_PRUNE_LOCK_FILE", "/tmp/docker_prune.lock")
IMAGE_PRUNE_UNTIL = os.environ.get("DOCKER_PRUNE_IMAGE_UNTIL", "168h")
BUILDER_PRUNE_UNTIL = os.environ.get("DOCKER_PRUNE_BUILDER_UNTIL", "168h")
BUILDER_RESERVED_SPACE = os.environ.get(
    "DOCKER_PRUNE_BUILDER_RESERVED_SPACE",
    "8gb",
)
BUILDER_MAX_USED_SPACE = os.environ.get(
    "DOCKER_PRUNE_BUILDER_MAX_USED_SPACE",
    "15gb",
)
BUILDER_MIN_FREE_SPACE = os.environ.get(
    "DOCKER_PRUNE_BUILDER_MIN_FREE_SPACE",
    "30gb",
)


@contextmanager
def exclusive_lock(lock_file_path: str) -> Iterator[TextIO]:
    os.makedirs(os.path.dirname(lock_file_path), exist_ok=True)
    with open(lock_file_path, "w", encoding="utf-8") as lock_file:
        try:
            fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            lock_file.write(f"pid={os.getpid()}\n")
            lock_file.flush()
            yield lock_file
        except OSError as exc:
            if exc.errno in (errno.EACCES, errno.EAGAIN):
                print(
                    "[docker-prune-once] Skip: another prune is running on this host.",
                )
                sys.exit(0)
            raise
        finally:
            try:
                fcntl.lockf(lock_file, fcntl.LOCK_UN)
            except Exception:
                pass


def run_command(command: list[str]) -> None:
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ},
        check=False,
    )
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.returncode != 0:
        if completed.stderr:
            print(completed.stderr, file=sys.stderr, end="")
        raise subprocess.CalledProcessError(
            completed.returncode,
            command,
            completed.stdout,
            completed.stderr,
        )


def get_builder_prune_command() -> list[str]:
    command = [
        "docker",
        "buildx",
        "prune",
        "-f",
        "--reserved-space",
        BUILDER_RESERVED_SPACE,
        "--max-used-space",
        BUILDER_MAX_USED_SPACE,
        "--min-free-space",
        BUILDER_MIN_FREE_SPACE,
    ]
    if BUILDER_PRUNE_UNTIL:
        command.extend(["--filter", f"until={BUILDER_PRUNE_UNTIL}"])
    return command


def main() -> int:
    try:
        with exclusive_lock(LOCK_FILE_PATH):
            print("[docker-prune-once] Acquired lock, running docker prune steps...")
            print(
                "[docker-prune-once] Policy: "
                f"image_until={IMAGE_PRUNE_UNTIL}, "
                f"builder_until={BUILDER_PRUNE_UNTIL}, "
                f"builder_reserved_space={BUILDER_RESERVED_SPACE}, "
                f"builder_max_used_space={BUILDER_MAX_USED_SPACE}, "
                f"builder_min_free_space={BUILDER_MIN_FREE_SPACE}",
            )
            # Prune dangling images older than the retention window.
            run_command(
                [
                    "docker",
                    "image",
                    "prune",
                    "-f",
                    "--filter",
                    f"until={IMAGE_PRUNE_UNTIL}",
                ],
            )
            # Prune only cold build cache and keep enough space for hot layers.
            run_command(get_builder_prune_command())
            print("[docker-prune-once] Completed successfully.")
        return 0
    except FileNotFoundError as exc:
        print(f"Required binary not found: {exc}", file=sys.stderr)
        return 2
    except subprocess.CalledProcessError as exc:
        print(
            f"Command failed with exit code {exc.returncode}: {' '.join(exc.cmd)}",
            file=sys.stderr,
        )
        return exc.returncode or 1
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
