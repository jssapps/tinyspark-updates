#!/usr/bin/env python3
"""Checks announcements.json before it goes live (Inbox plan M3, T3.5).

Same rules as platform/news/announcement_feed.gd: schema 1, unique ids,
known kinds, title <= 60 and body <= 600 characters, YYYY-MM-DD dates
(start <= end), integer versions (min <= max), buttons with exactly one of
url / route / action, links only https:// or market://details?id=, images
that exist next to the file (PNG/JPG, <= 300 KB) or are https, and the file
<= 64 KB. Exit code 1 on any error.

    python3 check_announcements.py [path/to/announcements.json]
"""
import json, os, re, sys

KINDS = {"new_app", "critical", "new_levels", "event", "info"}
ROUTES = {"home", "level", "daily", "wallet", "shop", "achievements", "continue"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MAX_FILE = 64 * 1024
MAX_IMG = 300 * 1024


def link_ok(u):
    return u.startswith("https://") or u.startswith("market://details?id=")


def check(path):
    errs, warns = [], []
    size = os.path.getsize(path)
    if size > MAX_FILE:
        errs.append("file is %d bytes (max %d)" % (size, MAX_FILE))
    try:
        d = json.load(open(path, encoding="utf-8"))
    except ValueError as e:
        return ["not valid JSON: %s" % e], warns
    if not isinstance(d, dict) or d.get("schema") != 1 or not isinstance(d.get("announcements"), list):
        return ["top level must be {\"schema\": 1, \"announcements\": [...]}"], warns
    base = os.path.dirname(os.path.abspath(path))
    ids = set()
    for i, e in enumerate(d["announcements"]):
        where = "entry %d" % i
        if not isinstance(e, dict):
            errs.append("%s: not an object" % where)
            continue
        aid = e.get("id")
        where = "entry %d (%s)" % (i, aid)
        if not isinstance(aid, str) or not aid:
            errs.append("%s: missing id" % where)
        elif aid in ids:
            errs.append("%s: duplicate id" % where)
        ids.add(aid)
        if e.get("kind") not in KINDS:
            errs.append("%s: kind must be one of %s" % (where, sorted(KINDS)))
        title, body = e.get("title", ""), e.get("body", "")
        if not isinstance(title, str) or not title or not isinstance(body, str) or not body:
            errs.append("%s: needs title and body" % where)
        else:
            if len(title) > 60:
                errs.append("%s: title is %d characters (max 60)" % (where, len(title)))
            if len(body) > 600:
                errs.append("%s: body is %d characters (max 600)" % (where, len(body)))
            if "<" in title + body:
                warns.append("%s: '<' found - text is shown as plain text, HTML is not supported" % where)
        for k in ("start", "end", "date"):
            if k in e and not (isinstance(e[k], str) and DATE.match(e[k])):
                errs.append("%s: %s must be YYYY-MM-DD" % (where, k))
        if isinstance(e.get("start"), str) and isinstance(e.get("end"), str) and e["start"] > e["end"]:
            errs.append("%s: start is after end" % where)
        for k in ("min_version", "max_version"):
            if k in e and not isinstance(e[k], int):
                errs.append("%s: %s must be a whole number (version code, e.g. 10200)" % (where, k))
        if isinstance(e.get("min_version"), int) and isinstance(e.get("max_version"), int) and e["min_version"] > e["max_version"]:
            errs.append("%s: min_version is above max_version" % where)
        b = e.get("button")
        if b is not None:
            if not isinstance(b, dict) or not b.get("label"):
                errs.append("%s: button needs a label" % where)
            else:
                n = sum(k in b for k in ("url", "route", "action"))
                if n != 1:
                    errs.append("%s: button needs exactly one of url / route / action" % where)
                if "url" in b and not link_ok(str(b["url"])):
                    errs.append("%s: link must start with https:// or market://details?id=" % where)
                if "route" in b and str(b["route"]).split(":")[0] not in ROUTES:
                    errs.append("%s: unknown route %r" % (where, b["route"]))
                if "action" in b and b["action"] != "update":
                    errs.append("%s: action must be \"update\"" % where)
        img = e.get("image")
        if img is not None:
            if not isinstance(img, str) or ".." in img:
                errs.append("%s: bad image path" % where)
            elif img.startswith("https://"):
                pass
            elif "://" in img:
                errs.append("%s: image must be a path in this repo or an https URL" % where)
            else:
                p = os.path.join(base, img.lstrip("/"))
                if not os.path.isfile(p):
                    errs.append("%s: image %s not found" % (where, img))
                else:
                    head = open(p, "rb").read(4)
                    if not (head.startswith(b"\x89PNG") or head.startswith(b"\xff\xd8")):
                        errs.append("%s: image must be PNG or JPG" % where)
                    if os.path.getsize(p) > MAX_IMG:
                        errs.append("%s: image is over 300 KB" % where)
    if len(d["announcements"]) > 20:
        warns.append("%d announcements - only the first 20 that apply are shown" % len(d["announcements"]))
    return errs, warns


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "announcements.json"
    errs, warns = check(path)
    for w in warns:
        print("WARN ", w)
    for e in errs:
        print("ERROR", e)
    print("OK" if not errs else "%d error(s)" % len(errs))
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
