import json
import os
from pathlib import Path
import re
import shutil

import project


def property_value(value):
    return value.replace("\\", "\\\\").replace("\r", "\\r").replace("\n", "\\n")


def main():
    name = (os.environ.get("NAME") or input("Plugin name: ")).strip()
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9 _-]*", name):
        raise ValueError("Use a name starting with a letter, followed by letters, numbers, spaces, - or _")
    author = (os.environ.get("AUTHOR") or "").strip()
    while not author:
        author = input("Author: ").strip()
    description = os.environ.get("DESCRIPTION")
    if description is None:
        description = input("Description (optional): ")
    tags = os.environ.get("TAGS")
    if tags is None:
        tags = input("Tags (comma-separated, optional): ")
    words = re.findall(r"[A-Za-z0-9]+", name)
    slug = "-".join(word.lower() for word in words)
    base = "".join(word[0].upper() + word[1:] for word in words)
    package_name = slug.replace("-", "")
    java_keywords = """
        abstract assert boolean break byte case catch char class const continue default do
        double else enum extends final finally float for goto if implements import
        instanceof int interface long native new package private protected public return
        short static strictfp super switch synchronized this throw throws transient try
        void volatile while true false null _
    """.split()
    if package_name in java_keywords:
        package_name += "plugin"
    package = "com.plugins." + package_name
    parent = Path(os.environ.get("DIRECTORY") or project.ROOT.parent).expanduser().resolve()
    destination = parent / slug

    files = json.loads(project.PLUGIN_FILES.read_text(encoding="utf-8"))
    for relative, source in files.items():
        target = Path(relative)
        if target.is_absolute() or ".." in target.parts:
            raise ValueError(f"Destination must be relative to the new plugin: {relative}")
        if not (project.ROOT / source).is_file():
            raise FileNotFoundError(f"Source file not found: {source}")

    replacements = {
        "@@NAME@@": name,
        "@@ID@@": slug,
        "@@BASE@@": base,
        "@@CLASS@@": base + "Plugin",
        "@@PACKAGE@@": package,
        "@@AUTHOR@@": property_value(author),
        "@@DESCRIPTION@@": property_value(description.strip()),
        "@@TAGS@@": property_value(tags.strip()),
    }
    package_path = package.replace(".", "/")
    template_destinations = {
        "src/main/java/Plugin.java": f"src/main/java/{package_path}/{base}Plugin.java",
        "src/main/java/Config.java": f"src/main/java/{package_path}/{base}Config.java",
        "src/test/java/PluginTest.java": f"src/test/java/{package_path}/{base}PluginTest.java",
    }
    templates = {}
    for template in sorted(project.TEMPLATES.rglob("*.tmpl")):
        relative = str(template.relative_to(project.TEMPLATES).with_suffix(""))
        relative = template_destinations.get(relative, relative)
        content = template.read_text(encoding="utf-8")
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        templates[relative] = content

    destination.mkdir(parents=True, exist_ok=False)
    for relative, source in files.items():
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(project.ROOT / source, target)

    for relative, content in templates.items():
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    print(f"Created {destination}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        raise SystemExit(str(error))
    except (EOFError, KeyboardInterrupt):
        raise SystemExit("Cancelled.")
