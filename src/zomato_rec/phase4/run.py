from __future__ import annotations

from dotenv import load_dotenv

load_dotenv()

import argparse
import logging

from zomato_rec.config import Settings
from zomato_rec.logging_config import configure_logging
from zomato_rec.phase4.recommend import run_phase4


logger = logging.getLogger("zomato_rec.phase4")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Phase 4: LLM ranking + explanations (Groq)")
    p.add_argument("--shortlist", default="storage/shortlist.json", help="Phase 3 shortlist JSON path.")
    p.add_argument("--prefs", default="storage/preferences.json", help="Phase 2 preferences JSON path.")
    p.add_argument("--out", default="storage/recommendations.json", help="Output recommendations JSON path.")
    p.add_argument("--report", default="storage/phase4_report.json", help="Output report JSON path.")
    p.add_argument("--top-k", type=int, default=5, help="Number of recommendations to generate.")
    p.add_argument("--temperature", type=float, default=0.2, help="Groq temperature.")
    p.add_argument("--max-tokens", type=int, default=900, help="Max tokens for response.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = Settings()
    configure_logging(settings.log_level)

    rep = run_phase4(
        shortlist_path=args.shortlist,
        preferences_path=args.prefs,
        out_path=args.out,
        report_path=args.report,
        top_k=args.top_k,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )
    logger.info("Phase 4 complete: model=%s out=%s", rep.model, rep.output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

