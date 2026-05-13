"""
Streamlit Community Cloud entrypoint.

Set **Main file path** to `streamlit_app.py` (repo root). This delegates to the
full Phase 9 app at `src/zomato_rec/web_ui/app.py`.
"""

from __future__ import annotations

import runpy
from pathlib import Path

_APP = Path(__file__).resolve().parent / "src" / "zomato_rec" / "web_ui" / "app.py"
runpy.run_path(str(_APP), run_name="__main__")
