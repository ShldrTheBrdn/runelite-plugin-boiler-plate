#!/usr/bin/env python3
"""Update plugin Nix files using the shared project's environment defaults."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from project import STATE, digest, read_json, run, safe_path, write_json


def update(settings):
    project = settings.path
    state_path = project / STATE
    if state_path.is_symlink():
        raise ValueError(f"Refusing symlink: {state_path}")
    if not state_path.is_file():
        raise ValueError("Run update in a generated plugin or set PROJECT=/path/to/plugin")
    state = read_json(state_path)
    if state.get("version") != 1 or not isinstance(state.get("files"), dict):
        raise ValueError("Unsupported boilerplate state file")
    for relative in settings.update_files:
        safe_path(project, relative)
    # Clone outside the plugin so repository-local URL rewrites are not inherited.
    with tempfile.TemporaryDirectory(prefix="runelite-boilerplate-update-") as directory:
        temporary_root = Path(directory)
        source = temporary_root / "upstream"
        print(f"Fetching {settings.repository}", flush=True)
        result = subprocess.run(
            ["git", "clone", "--depth", "1", "--single-branch", "--quiet", "--",
             settings.repository, str(source)],
            cwd=temporary_root, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode:
            raise ValueError("Could not fetch the upstream boilerplate; nothing changed:\n"
                             + result.stderr.strip())
        # Validate both files before backing up or replacing anything in the plugin.
        for relative in settings.update_files:
            if not safe_path(source, relative).is_file():
                raise ValueError(f"Upstream repository is missing {relative}; nothing changed")
        if not isinstance(read_json(source / "flake.lock"), dict):
            raise ValueError("Upstream flake.lock must be a JSON object; nothing changed")
        revision = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=source, text=True,
        ).strip()
        update_flakes(project, state, source, revision, settings)


def update_flakes(project, state, source, revision, settings):
    changes, conflicts = [], []
    for relative in settings.update_files:
        destination = safe_path(project, relative)
        incoming = digest(source / relative)
        current = digest(destination)
        previous = state["files"].get(relative)
        if current == incoming:
            continue
        # An upstream file unchanged since the last sync does not overwrite a local edit.
        if incoming == previous and not settings.force:
            continue
        if current != previous:
            conflicts.append(relative)
        changes.append(relative)
    if conflicts and not settings.force:
        raise ValueError("Local/upstream conflicts; nothing changed:\n  " + "\n  ".join(conflicts)
                         + "\nReview the files, or use FORCE=1 to replace them with backups.")

    backup = None
    # Back up all files to be replaced before writing any shared file.
    for relative in changes:
        destination = project / relative
        if destination.exists():
            backup_root = project / ".boilerplate-backups"
            if backup_root.is_symlink():
                raise ValueError(f"Refusing symlink: {backup_root}")
            if backup is None:
                backup_root.mkdir(exist_ok=True)
                backup = Path(tempfile.mkdtemp(prefix="update-", dir=backup_root))
            saved = backup / relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, saved)
    for relative in changes:
        destination = project / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Replace each complete file atomically.
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as stream:
            temporary = Path(stream.name)
        try:
            shutil.copy2(source / relative, temporary)
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)
        print(f"Updated {relative}")
    state["files"].update({relative: digest(source / relative) for relative in settings.update_files})
    state["upstream"] = {"repository": settings.repository, "revision": revision}
    write_json(project / STATE, state)
    if not changes:
        print("Nix environment files are up to date.")
    if backup:
        print(f"Backups: {backup}")
    if changes:
        print("If using nix develop, exit and re-enter it to load the updated environment.")


if __name__ == "__main__":
    raise SystemExit(run(update))
