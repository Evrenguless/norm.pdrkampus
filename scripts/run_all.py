"""Run one or every configured province with the shared collector."""
import argparse
import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
COLLECTOR = ROOT / "scripts" / "collect_students.py"


def configs():
    return sorted(
        path
        for path in RESEARCH.glob("*/config.json")
        if not path.parent.name.startswith("_")
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--province", help="province folder slug, e.g. bayburt")
    args = parser.parse_args()

    selected = configs()
    if args.province:
        selected = [
            path for path in selected if path.parent.name.casefold() == args.province.casefold()
        ]
        if not selected:
            raise SystemExit(f"No config found for province slug: {args.province}")

    summaries = []
    failures = []
    for config_path in selected:
        slug = config_path.parent.name
        print(f"==> {slug}", flush=True)
        proc = subprocess.run(
            [sys.executable, str(COLLECTOR), "--config", str(config_path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if proc.returncode:
            failures.append({"province": slug, "error": proc.stderr.strip()})
            print(proc.stderr, file=sys.stderr)
            continue

        lines = [line for line in proc.stdout.splitlines() if line.strip()]
        try:
            summary = json.loads(lines[-1]) if lines else {}
        except json.JSONDecodeError:
            summary = {"raw_output": proc.stdout.strip()}
        summaries.append(summary)
        print(proc.stdout.strip())

    report = {
        "configured_provinces": len(selected),
        "completed": len(summaries),
        "failed": failures,
        "summaries": summaries,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
