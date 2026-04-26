from __future__ import annotations

import pytest

import frontend.app as app


class _StreamlitStop(RuntimeError):
    pass


class _FakeStreamlit:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.session_state: dict[str, object] = {}

    def error(self, message: object) -> None:
        self.errors.append(str(message))

    def stop(self) -> None:
        raise _StreamlitStop()


@pytest.mark.parametrize(
    ("asset_text", "expected_error"),
    [
        ("{not valid json", "Failed to load demo assets:"),
        ("[]", "JSON object mapping section names to text"),
    ],
)
def test_invalid_demo_section_map_uses_demo_asset_failure_path(
    tmp_path, monkeypatch, asset_text: str, expected_error: str
) -> None:
    section_text_path = tmp_path / "section_text.json"
    section_text_path.write_text(asset_text, encoding="utf-8")
    fake_st = _FakeStreamlit()

    monkeypatch.setattr(app, "DEMO_SECTION_TEXT_PATH", section_text_path)
    monkeypatch.setattr(app, "st", fake_st)
    monkeypatch.setattr(app, "_load_demo_assets", lambda: ({"ok": True}, {"ok": True}))

    with pytest.raises(_StreamlitStop):
        app._load_demo_into_session()

    assert len(fake_st.errors) == 1
    assert "Failed to load demo assets:" in fake_st.errors[0]
    assert expected_error in fake_st.errors[0]
    assert app.SESSION_KEY_POLICY not in fake_st.session_state
    assert app.SESSION_KEY_DISPUTE not in fake_st.session_state
    assert app.SESSION_KEY_SECTION_MAP not in fake_st.session_state
