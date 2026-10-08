import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pi-config.py"
SPEC = importlib.util.spec_from_file_location("pi_config", SCRIPT)
pi_config = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(pi_config)


def namespace(**overrides):
    args = {
        "catalog": None,
        "config": None,
        "providers": ["lmstudio"],
        "dry_run": False,
        "label": None,
        "update_base_url": False,
        "replace": False,
    }
    args.update(overrides)

    class Args:
        pass

    parsed = Args()
    for key, value in args.items():
        setattr(parsed, key, value)
    return parsed


CATALOG = {
    "providers": {
        "lmstudio": {
            "baseUrl": "http://localhost:11440/v1",
            "models": [
                {"id": "openai/gpt-oss-20b"},
                {"id": "gemma4", "name": "gemma4 [lmlink]"},
            ],
        }
    }
}


class MergeModelsTests(unittest.TestCase):
    def run_merge(self, config, *, replace=False):
        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "catalog.json"
            config_path = Path(temp_dir) / "models.json"
            catalog_path.write_text(json.dumps(CATALOG), encoding="utf-8")
            config_path.write_text(json.dumps(config), encoding="utf-8")
            args = namespace(catalog=catalog_path, config=config_path, replace=replace)
            self.assertEqual(pi_config.merge_models(args), 0)
            return json.loads(config_path.read_text(encoding="utf-8"))

    def test_merge_keeps_existing_models_and_fills_display_names(self):
        updated = self.run_merge(
            {
                "providers": {
                    "lmstudio": {
                        "baseUrl": "http://localhost:11440/v1",
                        "models": [{"id": "stale-model"}, {"id": "gemma4"}],
                    }
                }
            }
        )

        models = updated["providers"]["lmstudio"]["models"]
        self.assertIn({"id": "stale-model"}, models)
        self.assertIn({"id": "gemma4", "name": "gemma4 [lmlink]"}, models)
        self.assertIn({"id": "openai/gpt-oss-20b"}, models)

    def test_replace_drops_stale_models(self):
        updated = self.run_merge(
            {
                "providers": {
                    "lmstudio": {
                        "baseUrl": "http://localhost:11440/v1",
                        "apiKey": "keep-me",
                        "models": [{"id": "stale-model"}],
                    }
                }
            },
            replace=True,
        )

        provider = updated["providers"]["lmstudio"]
        self.assertEqual(provider["apiKey"], "keep-me")
        self.assertEqual(
            provider["models"],
            [{"id": "openai/gpt-oss-20b"}, {"id": "gemma4", "name": "gemma4 [lmlink]"}],
        )


if __name__ == "__main__":
    unittest.main()
