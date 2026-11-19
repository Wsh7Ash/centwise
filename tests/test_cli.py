import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(args):
    return subprocess.run(
        [sys.executable, "-m", "centwise", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONPATH": str(ROOT / "src"), "PYTHONIOENCODING": "utf-8"},
    )


def test_split_text_output():
    proc = run(["split", "100.00", "3"])
    assert proc.returncode == 0, proc.stderr
    assert "USD 100.00 split" in proc.stdout
    assert "33.34" in proc.stdout
    assert "3334 minor" in proc.stdout
    assert "(exact)" in proc.stdout


def test_split_json_output():
    proc = run(["split", "100.00", "3", "--json"])
    data = json.loads(proc.stdout)
    assert data["currency"] == "USD"
    assert data["total"] == "100.00"
    assert data["total_minor"] == 10000
    assert [part["minor"] for part in data["parts"]] == [3334, 3333, 3333]
    assert sum(part["minor"] for part in data["parts"]) == data["total_minor"]
    assert data["exact"] is True


def test_allocate_by_weights():
    proc = run(["allocate", "10.00", "--weights", "1,2,3"])
    assert proc.returncode == 0, proc.stderr
    assert "1.67" in proc.stdout
    assert "3.33" in proc.stdout
    assert "5.00" in proc.stdout
    assert "(exact)" in proc.stdout


def test_allocate_json_includes_weights():
    proc = run(["allocate", "10.00", "--weights", "0.5,0.5", "--json"])
    data = json.loads(proc.stdout)
    assert data["weights"] == ["0.5", "0.5"]
    assert [part["amount"] for part in data["parts"]] == ["5.00", "5.00"]


def test_currency_scales_in_cli():
    usd = run(["split", "1.00", "3", "--currency", "usd"])
    assert "0.34" in usd.stdout
    kwd = run(["split", "1.000", "3", "--currency", "KWD", "--json"])
    assert [part["amount"] for part in json.loads(kwd.stdout)["parts"]] == [
        "0.334",
        "0.333",
        "0.333",
    ]
    jpy = run(["split", "1000", "3", "--currency", "JPY"])
    assert "334" in jpy.stdout
    assert "scale 0" in jpy.stdout


def test_negative_total():
    proc = run(["split", "-100.00", "3", "--json"])
    data = json.loads(proc.stdout)
    assert data["parts"][0]["amount"] == "-33.34"
    assert data["exact"] is True


def test_currencies():
    proc = run(["currencies"])
    assert proc.returncode == 0
    assert "code  scale" in proc.stdout
    assert "JPY  0" in proc.stdout
    data = json.loads(run(["currencies", "--json"]).stdout)
    assert {"code": "KWD", "scale": 3} in data


def test_invalid_inputs_exit_two():
    cases = [
        ["split", "100.00", "0"],
        ["split", "abc", "3"],
        ["split", "1.00", "3", "--currency", "ZZZ"],
        ["allocate", "1.00", "--weights", "1,-2"],
        ["allocate", "1.00", "--weights", "1,,2"],
        ["allocate", "1.00", "--weights", "0,0"],
        ["allocate", "1.00", "--weights", "one,two"],
    ]
    for args in cases:
        proc = run(args)
        assert proc.returncode == 2, (args, proc.stdout, proc.stderr)
        assert "centwise:" in proc.stderr, args
