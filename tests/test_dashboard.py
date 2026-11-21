"""Streamlit application-level smoke tests for the published analytics view."""
from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_streamlit_dashboard_renders_historical_catalogue():
    script = Path(__file__).resolve().parents[1] / "app.py"
    at = AppTest.from_file(str(script), default_timeout=45).run()
    assert len(at.exception) == 0, [str(e.message) for e in at.exception]
    assert len(at.tabs) == 4
    assert len(at.metric) == 0  # The dashboard renders its branded KPI cards with HTML.


def test_streamlit_filters_can_select_tv_shows():
    script = Path(__file__).resolve().parents[1] / "app.py"
    at = AppTest.from_file(str(script), default_timeout=45).run()
    assert len(at.exception) == 0, [str(e.message) for e in at.exception]
    at.multiselect[0].set_value(["TV Show"]).run()
    assert len(at.exception) == 0, [str(e.message) for e in at.exception]
