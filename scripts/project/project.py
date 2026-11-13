from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "plugin" / "templates"
PLUGIN_FILES = Path(__file__).resolve().parent / "plugin-files.json"
