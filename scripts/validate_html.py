#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate a generated HTML document against the html-doc-style design system.

Usage:
    python validate_html.py <file.html> [more.html ...]
    python validate_html.py --strict <file.html>     # warnings also fail

Exit code: 0 = all checks passed, 1 = at least one failure.
Pure standard library, no external dependencies.
"""

import argparse
import html.parser
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (ValueError, OSError):
        pass

VOID = {"meta", "link", "br", "img", "input", "hr", "source", "area", "base",
        "col", "embed", "param", "track", "wbr"}


class Structure(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # (tag, attrs dict)
        self.mismatches = []
        self.unclosed = []
        self.pre_bad = []        # pre not directly inside .codewrap
        self.external = []       # remote link/script/img
        self.ids = set()
        self.anchors = []
        self.sections = []
        self.callouts = 0
        self.ttls = 0
        self.pre_count = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "section" and "id" in a:
            self.sections.append(a["id"])
        if tag == "a" and (a.get("href") or "").startswith("#"):
            self.anchors.append(a["href"][1:])
        if "callout" in classes:
            self.callouts += 1
        if "ttl" in classes:
            self.ttls += 1
        if tag == "pre":
            self.pre_count += 1
            parent = self.stack[-1] if self.stack else ("", {})
            pcls = (parent[1].get("class") or "").split()
            if parent[0] != "div" or "codewrap" not in pcls:
                self.pre_bad.append(a.get("class", "") or "(no class)")
        if tag in ("link", "script", "img"):
            url = a.get("src") or a.get("href") or ""
            if url.startswith(("http://", "https://", "//")):
                self.external.append("<%s %s>" % (tag, url[:70]))
        if tag not in VOID:
            self.stack.append((tag, a))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            top = self.stack[-1][0] if self.stack else "(empty)"
            self.mismatches.append("</%s> while <%s> open" % (tag, top))


def check(path, strict=False):
    errors, warnings = [], []
    p = pathlib.Path(path)
    if not p.exists():
        return ["file not found: %s" % path], [], "FAIL"
    try:
        s = p.read_text("utf-8")
    except UnicodeDecodeError:
        return ["file is not valid UTF-8"], [], "FAIL"

    # --- document head ---
    if not s.lstrip().lower().startswith("<!doctype html"):
        errors.append("missing <!DOCTYPE html>")
    for label, pattern in [
        ("charset", r'<meta\s+charset="utf-8"'),
        ("lang", r'<html[^>]+lang="zh-CN"'),
        ("viewport", r'<meta[^>]+name="viewport"'),
    ]:
        if not re.search(pattern, s, re.I):
            errors.append("missing %s declaration" % label)

    # --- css source ---
    styles = re.findall(r"<style[^>]*>(.*?)</style>", s, re.S | re.I)
    links = re.findall(r'<link[^>]*href="([^"]+)"', s, re.S | re.I)
    css = "\n".join(styles)
    for href in links:
        if href.startswith(("http://", "https://", "//")):
            continue
        target = (p.parent / href).resolve()
        if target.exists():
            css += "\n" + target.read_text("utf-8", errors="replace")
        else:
            errors.append("linked stylesheet missing: %s" % href)
    if not css.strip():
        errors.append("no stylesheet found (inline <style> or linked css)")
    else:
        for label, pattern in [
            (":root variables", r":root\s*\{"),
            ("accent token", r"--accent\s*:\s*#0d8060"),
            ("920px breakpoint", r"@media\s*\(max-width:\s*920px\)"),
            ("print rules", r"@media\s+print"),
            ("print block protection", r"break-inside:\s*avoid"),
        ]:
            if not re.search(pattern, css, re.I):
                errors.append("stylesheet missing %s" % label)

    # --- structure ---
    st = Structure()
    st.feed(s)
    st.close()
    if st.mismatches:
        errors.append("tag mismatches: " + "; ".join(st.mismatches[:4]))
    if st.stack:
        errors.append("unclosed tags: " + ", ".join(t for t, _ in st.stack[:6]))

    missing = sorted(set(st.anchors) - set(st.sections))
    orphan = sorted(set(st.sections) - set(st.anchors))
    if missing:
        errors.append("TOC links without section: " + ", ".join(missing))
    if orphan:
        warnings.append("sections without TOC link: " + ", ".join(orphan))
    if not st.sections:
        errors.append("no <section id=...> found")

    if st.pre_bad:
        errors.append("%d <pre> not directly inside .codewrap" % len(st.pre_bad))
    if st.external:
        errors.append("external resources break offline use: " + "; ".join(st.external[:3]))
    if st.callouts and st.ttls < st.callouts:
        warnings.append("%d callout(s) but only %d .ttl title(s)" % (st.callouts, st.ttls))

    # --- content conventions ---
    for m in re.finditer(r'<pre[^>]*>(.*?)</pre>', s, re.S | re.I):
        body = re.sub(r"<[^>]+>", "", m.group(1))
        if re.search(r"\\[ \t]*\r?\n", body):
            warnings.append("backslash line-continuation inside a command block (PowerShell cannot parse it)")
            break
    if re.search(r'style="[^"]*#[0-9a-fA-F]{3,8}\b', s):
        warnings.append("hard-coded hex color inside a style attribute (color-swatch demos are fine)")
    allowed_fs = {32, 25, 21, 15, 14.5, 14, 13.5, 13, 12.5, 12, 11.5, 11, 10.5}
    bad_fs = sorted({v for v in re.findall(r"font-size\s*:\s*(\d+(?:\.\d+)?)px", s)
                     if float(v) not in allowed_fs})
    if bad_fs:
        warnings.append("font-size outside the fixed 12-value scale: " + ", ".join(bad_fs))
    if "IntersectionObserver" not in s:
        warnings.append("missing TOC scroll-highlight script")
    if "clipboard" not in s and "execCommand" not in s:
        warnings.append("missing code-block copy script")
    if "<blockquote" in s:
        warnings.append("use .callout instead of <blockquote> for quotations")
    if "<table" in s and "border-collapse" not in css:
        warnings.append("table present but no border-collapse rule found")

    status = "FAIL" if errors else ("WARN" if warnings else "PASS")
    if strict and warnings:
        status = "FAIL"
    return errors, warnings, status


def main():
    ap = argparse.ArgumentParser(description="Validate HTML against the html-doc-style design system")
    ap.add_argument("files", nargs="+", help="HTML file(s) to validate")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = ap.parse_args()

    failed = False
    for f in args.files:
        errors, warnings, status = check(f, args.strict)
        print("[%s] %s" % (status, f))
        for e in errors:
            print("   ERROR  " + e)
        for w in warnings:
            print("   WARN   " + w)
        if not errors and not warnings:
            print("   all checks passed")
        if status == "FAIL":
            failed = True
    print("\n%d file(s) checked, %s" % (len(args.files), "FAILED" if failed else "OK"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
