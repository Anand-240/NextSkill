"""Phase H6: first-load and repeat-interaction timings on three saved pairs (offline, no key)."""
import time
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from views import common

APP = str(Path(__file__).resolve().parents[1] / "app.py")
PAIRS = ["frontend-developer-bengaluru", "data-analyst-jaipur", "accountant-mumbai"]

def main():
    with patch("engine.optional_serpapi_key", return_value=None), patch("engine._request", side_effect=AssertionError("network")):
        app = AppTest.from_file(APP, default_timeout=120).run()
        app = app.switch_page("views/find.py").run()
        for pair_id in PAIRS:
            label = common.pair_label(common.pair_by_id(pair_id))
            start = time.perf_counter(); app.selectbox[0].select(label).run(); first = time.perf_counter() - start
            start = time.perf_counter(); app.text_input[0].set_value("SQL").run(); changed = time.perf_counter() - start
            start = time.perf_counter(); app.text_input[0].set_value("").run(); repeat = time.perf_counter() - start
            print(f"{pair_id}: first load {first:.2f}s, new skill added {changed:.2f}s, repeat (cached) {repeat:.2f}s")

if __name__ == "__main__":
    main()
