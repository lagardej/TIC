"""Unit tests for the extract_gamestates script."""

import importlib.util
import json
from pathlib import Path
from types import ModuleType


def load_module_from_path(path: str) -> ModuleType:
    """Load a module from a file path and return the module object."""
    spec = importlib.util.spec_from_file_location("extract_gamestates", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module from path: {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_template_name_fallback(tmp_path: Path) -> None:
    """Ensure templateName is used when displayName is missing."""
    # Prepare a minimal save JSON where a gamestate entry is a list containing
    # an element that has no displayName but includes templateName under Value.
    src = tmp_path / "save.json"
    outdir = tmp_path / "out"
    outdir.mkdir()

    content = {
        "gamestates": {
            "PavonisInteractive.TerraInvicta.TestKey": [
                {"Value": {"templateName": "Foo Bar"}}
            ]
        }
    }

    src.write_text(json.dumps(content, ensure_ascii=False))

    script_path = (
        Path(__file__).parent / ".." / "scripts" / "extract_gamestates.py"
    ).resolve()
    mod = load_module_from_path(str(script_path))

    _manifest_path, manifest = mod.extract_gamestates(str(src), str(outdir))

    # Expect that the manifest contains the top-level key and the exploded sub-item
    assert "TestKey" in manifest
    # The sub-entry key should be TestKey.item_0
    assert "TestKey.item_0" in manifest

    rel = manifest["TestKey.item_0"]
    # Filename is written under a subdir named after the short key; expect
    # 'TestKey/item_0__Foo_Bar.json' (forward slashes)
    assert rel == "TestKey/item_0__Foo_Bar.json"
