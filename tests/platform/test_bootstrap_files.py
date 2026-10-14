from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_windows_batch_files_use_crlf_and_call_npm_subscripts():
    for name in ("setup.bat", "start.bat"):
        data = (ROOT / name).read_bytes()
        assert b"\n" in data
        assert data.count(b"\r\n") == data.count(b"\n")
    assert "call npm.cmd ci" in (ROOT / "setup.bat").read_text(encoding="ascii")
    assert (ROOT / "setup.bat").read_text(encoding="ascii").rstrip().endswith("exit /b 0")
    assert "call npm.cmd run build" in (ROOT / "start.bat").read_text(encoding="ascii")
