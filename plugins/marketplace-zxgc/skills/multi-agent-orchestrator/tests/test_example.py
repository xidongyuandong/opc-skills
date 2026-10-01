import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("payload", [[], {}, {"workspace": "/"}, {"product_context": []}])
def test_bad_context_returns_blocked(tmp_path, payload):
    context = tmp_path / "context.json"
    context.write_text(json.dumps(payload))
    script = Path(__file__).resolve().parents[1] / "scripts/make_example.py"
    result = subprocess.run([sys.executable, str(script), "--context", str(context),
                             "--model", "example-model"], capture_output=True, text=True)
    assert result.returncode == 2
    assert json.loads(result.stdout)["status"] == "blocked"
    assert "Traceback" not in result.stderr
