"""Public MEB school pages -> source-backed, grade-grouped JSON. stdlib only."""
import argparse
import concurrent.futures
import datetime
import hashlib
import html
import json
import pathlib
import re
import urllib.parse
import urllib.request


SCHOOL_GRADES = {
    "anaokulu",
    "ilkokul",
    "ortaokul",
    "imam_hatip_ortaokulu",
    "lise",
    "mesem",
    "ozel_egitim",
}


def plain(s):
    s = re.sub(r"<script[^>]*>.*?</script>", "", s, flags=re.I | re.S)
    s = re.sub(r"<style[^>]*>.*?</style>", "", s, flags=re.I | re.S)
    stripped = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return " ".join(stripped.split()).strip()


def grade(name):
    n = (name or "").casefold().replace("i̇", "i")
    if "özel eğitim" in n:
        return "ozel_egitim"
    if "anaokul" in n:
        return "anaokulu"
    if "imam hatip" in n and "ortaokul" in n:
        return "imam_hatip_ortaokulu"
    if "ortaokul" in n:
        return "ortaokul"
    if "ilkokul" in n:
        return "ilkokul"
    if "lisesi" in n or "lise" in n:
        return "lise"
    if "mesleki eğitim merkezi" in n:
        return "mesem"
    if "rehberlik ve araştırma" in n:
        return "ram"
    return "diger_kurum"


def fetch(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": "PDRNormResearch/2.0 (public school statistics)"}
    )
    with urllib.request.urlopen(req, timeout=2) as response:
        hostname = urllib.parse.urlparse(response.url).hostname or ""
        if not hostname.endswith(".meb.k12.tr"):
            raise ValueError("Unexpected host")
        body = response.read(3 * 1024 * 1024)
        return (
            response.url,
            body.decode("utf-8", "replace"),
            hashlib.sha256(body).hexdigest(),
        )


def identity_pattern(province, districts):
    province_part = re.escape(province)
    district_part = "|".join(
        sorted((re.escape(x) for x in districts), key=len, reverse=True)
    )
    if not district_part:
        district_part = r"[^/|<]{2,80}"
    return re.compile(
        rf"{province_part} */ *({district_part}) *(?:/|-) *([^|<]{{3,180}})",
        re.I,
    )


def province_district_pattern(province, districts):
    province_part = re.escape(province)
    district_part = "|".join(
        sorted((re.escape(x) for x in districts), key=len, reverse=True)
    )
    if not district_part:
        district_part = r"[^/|<]{2,80}"
    return re.compile(rf"{province_part} */ *({district_part})", re.I)


def collect(url, province, districts, overrides=None):
    host = urllib.parse.urlparse(url).hostname
    if not host:
        raise ValueError(f"Invalid seed URL: {url}")

    out = {
        "id": host.split(".")[0],
        "source_url": url,
        "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "year": None,
        "source_date": None,
        "students": None,
        "grade": None,
        "attempts": [],
    }

    if overrides and out["id"] in overrides:
        out.update(overrides[out["id"]])
        out["grade"] = grade(out.get("name"))
        out["identity_source"] = "override"

    full_identity = identity_pattern(province, districts)
    province_district = province_district_pattern(province, districts)

    paths = [""] if out["id"].isdigit() else ["", "tema/okulumuz_hakkinda.php", "okulumuz_hakkinda.html"]
    for path in paths:
        requested = "https://" + host + "/" + path
        try:
            actual, source, digest = fetch(requested)
            text = plain(source)

            headings = [
                plain(x)
                for x in re.findall(r"<h1[^>]*>(.*?)</h1>", source, re.I | re.S)
            ]
            titles = [
                plain(x)
                for x in re.findall(r"<title[^>]*>(.*?)</title>", source, re.I | re.S)
            ]

            identity = None
            for candidate in headings + titles + [text[:3000]]:
                match = full_identity.search(candidate)
                if match:
                    identity = match
                    break

            if identity and out.get("identity_source") != "override":
                district = identity[1].strip().replace("i̇", "i").title()
                school = re.split(
                    r"  +|(?:T[.]?C[.]? *)?M[İI]LL[ÎİI] +EĞ[İI]T[İI]M",
                    identity[2],
                )[0].strip(" -–|")
                out.update(province=province, district=district, name=school)
            elif not out.get("province"):
                match = province_district.search(text)
                if match:
                    out.update(
                        province=province,
                        district=match[1].strip().replace("i̇", "i").title(),
                    )

            if out.get("name"):
                out["grade"] = grade(out["name"])

            hits = list(
                re.finditer(
                    r"Öğrenci *(?:Sayısı)? *[:|]? *([0-9][0-9.,]*)(?![0-9])",
                    text,
                    re.I,
                )
            )
            nums = list(
                dict.fromkeys(
                    int(match[1].replace(".", "").replace(",", "")) for match in hits
                )
            )
            out["attempts"].append(
                {
                    "url": actual,
                    "page": path or "homepage",
                    "status": "fetched",
                    "sha256": digest,
                    "student_candidates": nums,
                }
            )

            if (
                nums
                and out.get("province") == province
                and out.get("name")
                and (len(nums) == 1 or path == "")
            ):
                out.update(
                    students=nums[0],
                    source_url=actual,
                    evidence=text[max(0, hits[0].start() - 20) : hits[0].end() + 30],
                    status="source_snapshot_homepage" if path == "" else "source_snapshot",
                )
                if len(nums) > 1:
                    out["alternate_student_candidates"] = nums[1:]
                break

            if len(nums) > 1:
                out["status"] = "conflicting_counts"

        except Exception as exc:
            out["attempts"].append(
                {
                    "url": requested,
                    "status": "failed",
                    "error": type(exc).__name__,
                }
            )

    out.setdefault(
        "status",
        "students_not_found"
        if out.get("province") == province
        else "identity_unverified",
    )
    return out


def slugify(value):
    table = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    value = (value or "").translate(table).casefold().replace("ı", "i")
    return "".join(ch for ch in value if ch.isalnum())


def secondary_candidates(record, province):
    base = slugify(record.get("name"))
    district = slugify(record.get("district"))
    province_slug = slugify(province)
    stems = {base}
    for suffix in (
        "ilkokulu", "ortaokulu", "anaokulu", "lisesi",
        "meslekiveteknikanadolulisesi", "anadolulisesi"
    ):
        if base.endswith(suffix):
            stems.add(base[:-len(suffix)])
    if base.startswith("merkez"):
        stems.add(base[len("merkez"):])
    candidates = []
    for stem in stems:
        for slug in (stem, district + stem, province_slug + stem):
            if slug and slug not in candidates:
                candidates.append(slug)
    return candidates


def secondary_lookup(record, province):
    if record.get("students") is not None:
        return record
    expected_name = slugify(record.get("name"))
    expected_district = slugify(record.get("district"))
    for slug in secondary_candidates(record, province)[:3]:
        url = f"https://www.okullarhakkinda.com/{slug}.html"
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "PDRNormResearch/2.0 (public school statistics)"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                body = response.read(1024 * 1024).decode("utf-8", "replace")
            text = plain(body)
            compact = slugify(text[:8000])
            if slugify(province) not in compact or expected_district not in compact:
                continue
            if expected_name not in compact:
                continue
            match = re.search(r"Öğrenci Sayısı *: *([0-9]+)", text, re.I)
            if not match:
                continue
            out = dict(record)
            out["students"] = int(match.group(1))
            out["status"] = "secondary_snapshot_auto"
            out["source_quality"] = "secondary_meb_derived_directory"
            out["secondary_source_url"] = url
            out["evidence"] = match.group(0)
            return out
        except Exception:
            continue
    return record


def load_json(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def resolve_args(args):
    if args.config:
        config_path = pathlib.Path(args.config)
        config = json.loads(config_path.read_text())
        root = config_path.parent
        province = config["province"]
        districts = config.get("districts", [])
        seeds = root / config.get("seeds", "seeds.json")
        output = root / config.get("output", ".")
        return config, province, districts, seeds, output

    if not args.seeds or not args.output or not args.province:
        raise SystemExit(
            "Use --config research/<province>/config.json, or provide "
            "--province, --seeds and --output."
        )

    config = {
        "province": args.province,
        "districts": args.district or [],
    }
    return (
        config,
        args.province,
        args.district or [],
        pathlib.Path(args.seeds),
        pathlib.Path(args.output),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config")
    parser.add_argument("--province")
    parser.add_argument("--district", action="append")
    parser.add_argument("--seeds")
    parser.add_argument("--output")
    args = parser.parse_args()

    config, province, districts, seed_path, root = resolve_args(args)
    urls = json.loads(seed_path.read_text())
    root.mkdir(parents=True, exist_ok=True)

    overrides = load_json(seed_path.with_name("site-overrides.json"), {})
    fallback_doc = load_json(seed_path.with_name("fallback-students.json"), {"records": {}})
    manual_docs = [
        load_json(path, {"records": []})
        for path in sorted(seed_path.parent.glob("inventory-manual*.json"))
    ]
    manual_records = [
        record
        for doc in manual_docs
        for record in doc.get("records", [])
    ]
    exclusion_doc = load_json(seed_path.with_name("inventory-exclusions.json"), {"ids": []})
    target_doc = load_json(seed_path.with_name("inventory-target.json"), {})

    fallbacks = fallback_doc.get("records", {})
    excluded_ids = set(exclusion_doc.get("ids", []))

    results = []
    max_workers = int(config.get("max_workers", 8))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        jobs = pool.map(
            lambda url: collect(url, province, districts, overrides),
            urls,
        )
        for result in jobs:
            results.append(result)
            (root / "checkpoint.json").write_text(
                json.dumps(results, ensure_ascii=False, indent=2)
            )

    for result in results:
        fallback = fallbacks.get(result["id"])
        if (
            result.get("students") is None
            and fallback
            and result.get("province") == province
        ):
            result["students"] = fallback["students"]
            result["institution_code"] = fallback.get(
                "institution_code", result.get("institution_code")
            )
            result["status"] = "secondary_snapshot"
            result["secondary_source_url"] = fallback.get("source_url")
            result["source_quality"] = fallback.get("source_quality", "secondary")

    results = [result for result in results if result.get("id") not in excluded_ids]

    if config.get("roster_authoritative") and manual_records:
        def roster_key(record):
            district = (record.get("district") or "").casefold().replace("i̇", "i").replace("ı", "i")
            name = (record.get("name") or "").casefold().replace("i̇", "i").replace("ı", "i")
            name = "".join(ch for ch in name if ch.isalnum())
            return district, name

        roster = {roster_key(record): dict(record) for record in manual_records}
        non_school_live = []
        for live in results:
            key = roster_key(live)
            if live.get("grade") in SCHOOL_GRADES and key in roster:
                base = roster[key]
                for field in (
                    "students", "source_url", "observed_at", "year", "source_date",
                    "evidence", "status", "attempts", "institution_code",
                    "secondary_source_url", "source_quality"
                ):
                    if live.get(field) is not None:
                        base[field] = live[field]
                base["id"] = live["id"]
                base["grade"] = base.get("grade") or live.get("grade")
                roster[key] = base
            elif live.get("grade") not in SCHOOL_GRADES:
                non_school_live.append(live)

        results = list(roster.values()) + non_school_live
        manual_records = []

    if config.get("secondary_auto_fallback"):
        unresolved_indexes = [
            i for i, record in enumerate(results)
            if record.get("grade") in SCHOOL_GRADES and record.get("students") is None
        ]
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            refreshed = pool.map(
                lambda i: secondary_lookup(results[i], province),
                unresolved_indexes,
            )
            for i, record in zip(unresolved_indexes, refreshed):
                results[i] = record

    known_codes = {
        str(result.get("institution_code"))
        for result in results
        if result.get("institution_code")
    }
    known_names = {result.get("name") for result in results if result.get("name")}
    for index, record in enumerate(manual_records, start=1):
        code = record.get("institution_code")
        if (
            (not code or str(code) not in known_codes)
            and record.get("name") not in known_names
        ):
            manual_id = str(code) if code else f"{record.get('district','unknown')}-{index}"
            results.append(
                dict(
                    record,
                    id="manual-" + manual_id,
                    observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    year=None,
                    source_date=None,
                    attempts=[],
                )
            )

    grouped = {}
    for result in results:
        grouped.setdefault(result.get("grade") or "siniflandirilamayan", []).append(result)

    school_rows = [r for r in results if r.get("grade") in SCHOOL_GRADES]
    unresolved_schools = [r for r in school_rows if r.get("students") is None]
    expected_school_records = target_doc.get("expected_school_records")
    inventory_matches_target = (
        expected_school_records is not None
        and len(school_rows) == expected_school_records
    )

    summary = {
        "province": province,
        "candidate_sites": len(urls),
        "expected_school_records": expected_school_records,
        "inventory_matches_target": inventory_matches_target,
        "inventory_records": len(results),
        "student_count_found": sum(r.get("students") is not None for r in results),
        "unresolved": sum(r.get("students") is None for r in results),
        "school_records": len(school_rows),
        "school_student_count_found": sum(
            r.get("students") is not None for r in school_rows
        ),
        "school_unresolved": len(unresolved_schools),
        "unresolved_school_names": [r.get("name") for r in unresolved_schools],
        "complete_province_inventory": inventory_matches_target,
        "unknown_academic_year": True,
        "note": (
            "Primary values are labelled public MEB school-page snapshots. "
            "Explicit fallback values are marked secondary_snapshot. "
            "Manual roster-only schools remain null until a count is verified."
        ),
        "grades": {
            key: {
                "records": len(rows),
                "count_found": sum(r.get("students") is not None for r in rows),
            }
            for key, rows in grouped.items()
        },
    }

    (root / "students-by-grade.json").write_text(
        json.dumps({"summary": summary, "grades": grouped}, ensure_ascii=False, indent=2)
        + "\n"
    )
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
