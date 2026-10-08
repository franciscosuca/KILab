import importlib.util
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync-pi-models.py"
SPEC = importlib.util.spec_from_file_location("sync_pi_models", SCRIPT)
sync_pi_models = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(sync_pi_models)

LMSTUDIO = {"baseUrl": "http://localhost:1234/v1"}


def discover(api_payload, catalog, link=("this-mac", None)):
    with patch.object(sync_pi_models, "get_json", return_value=api_payload), patch.object(
        sync_pi_models, "lmstudio_cli_catalog", return_value=catalog
    ), patch.object(sync_pi_models, "lmstudio_link_devices", return_value=link):
        return sync_pi_models.discover_lmstudio(LMSTUDIO, 1)


class RemoteModelDetectionTests(unittest.TestCase):
    def test_explicit_remote_metadata_is_detected(self):
        payload = {
            "data": [
                {"id": "local-model", "type": "llm", "is_downloaded": True},
                {"id": "gemma4", "type": "llm", "is_remote": True},
                {"id": "embed", "type": "embedding", "remote": True},
            ]
        }

        self.assertEqual(sync_pi_models.model_ids(payload), ["local-model", "gemma4"])
        self.assertEqual(sync_pi_models.explicitly_remote_model_ids(payload), {"gemma4"})

    def test_models_without_a_remote_device_are_local(self):
        ids, remote_ids, _ = discover(
            {"data": [{"id": "local-model"}, {"id": "gemma4"}]},
            [("local-model", None), ("gemma4", None)],
        )

        self.assertEqual(ids, ["local-model", "gemma4"])
        self.assertEqual(remote_ids, set())

    def test_remote_only_model_is_tagged(self):
        ids, remote_ids, _ = discover(
            {"data": [{"id": "local-model"}, {"id": "qwen/qwen3.8-27b"}]},
            [("local-model", None), ("qwen/qwen3.8-27b", "mac-studio-id")],
        )

        self.assertEqual(ids, ["local-model", "qwen/qwen3.8-27b"])
        self.assertEqual(remote_ids, {"qwen/qwen3.8-27b"})

    def test_dual_copy_is_remote_when_preferred_device_hosts_it(self):
        _ids, remote_ids, _ = discover(
            {"data": [{"id": "gemma4"}]},
            [("gemma4", None), ("gemma4", "mac-studio-id")],
            link=("this-mac", "mac-studio-id"),
        )

        self.assertEqual(remote_ids, {"gemma4"})

    def test_dual_copy_is_local_when_this_device_is_preferred(self):
        _ids, remote_ids, _ = discover(
            {"data": [{"id": "gemma4"}]},
            [("gemma4", None), ("gemma4", "mac-studio-id")],
            link=("this-mac", "this-mac"),
        )

        self.assertEqual(remote_ids, set())

    def test_entries_from_this_device_are_local(self):
        _ids, remote_ids, _ = discover(
            {"data": [{"id": "gemma4"}]},
            [("gemma4", "this-mac")],
            link=("this-mac", "mac-studio-id"),
        )

        self.assertEqual(remote_ids, set())

    def test_cli_only_remote_models_are_added_to_the_list(self):
        ids, remote_ids, _ = discover(
            {"data": [{"id": "local-model"}]},
            [("local-model", None), ("qwen/qwen3.6-35b-a3b", "mac-studio-id")],
        )

        self.assertEqual(ids, ["local-model", "qwen/qwen3.6-35b-a3b"])
        self.assertEqual(remote_ids, {"qwen/qwen3.6-35b-a3b"})

    def test_api_failure_falls_back_to_the_cli_catalog(self):
        with patch.object(sync_pi_models, "get_json", side_effect=URLError("down")), patch.object(
            sync_pi_models,
            "lmstudio_cli_catalog",
            return_value=[("local-model", None), ("gemma4", "mac-studio-id")],
        ), patch.object(sync_pi_models, "lmstudio_link_devices", return_value=(None, None)):
            ids, remote_ids, source = sync_pi_models.discover_lmstudio(LMSTUDIO, 1)

        self.assertEqual(ids, ["local-model", "gemma4"])
        self.assertEqual(remote_ids, {"gemma4"})
        self.assertIn("fallback", source)

    def test_api_failure_with_require_api_raises(self):
        with patch.object(sync_pi_models, "get_json", side_effect=URLError("down")), patch.object(
            sync_pi_models, "lmstudio_cli_catalog", return_value=[("local-model", None)]
        ):
            with self.assertRaises(RuntimeError):
                sync_pi_models.discover_lmstudio(LMSTUDIO, 1, allow_cli_fallback=False)

    @patch.object(sync_pi_models, "get_json", return_value={"data": [{"id": "gemma4"}]})
    @patch.object(sync_pi_models, "lmstudio_cli_catalog", return_value=[("gemma4", "mac-studio-id")])
    @patch.object(sync_pi_models, "lmstudio_link_devices", return_value=("this-mac", "mac-studio-id"))
    def test_remote_label_is_saved_as_display_name(self, _link, _catalog, _get_json):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "models.json"
            config_path.write_text(
                json.dumps(
                    {
                        "providers": {
                            "lmstudio": {
                                "baseUrl": "http://localhost:1234/v1",
                                "models": [],
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            output = StringIO()
            with patch.object(
                sys,
                "argv",
                [str(SCRIPT), "--config", str(config_path), "--provider", "lmstudio"],
            ), redirect_stdout(output):
                self.assertEqual(sync_pi_models.main(), 0)

            updated = json.loads(config_path.read_text(encoding="utf-8"))
            model = updated["providers"]["lmstudio"]["models"][0]
            self.assertEqual(model, {"id": "gemma4", "name": "gemma4 [lmlink]"})
            self.assertIn("gemma4 [lmlink]", output.getvalue())


if __name__ == "__main__":
    unittest.main()
