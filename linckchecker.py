#!/usr/bin/env python3
import argparse
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen

USER_AGENT = "Mozilla/5.0 (compatible; MarkdownLinkChecker/1.0)"
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]*)\]\s*\(([^()\s]+)\s*\)")
FILE_URL_RE = re.compile(r"file://(/[^\s)\]>\"']+)")


@dataclass(frozen=True)
class LinkResult:
    text: str
    url: str
    source: str
    line: int
    status: str
    ok: bool


def scan_md_files(workdir):
    root = Path(workdir)
    if not root.is_dir():
        return []
    return sorted(p for p in root.rglob("*.md") if p.is_file())


def extract_links(text):
    links = []
    markdown_matches = list(MARKDOWN_LINK_RE.finditer(text))
    for match in markdown_matches:
        links.append((match.group(1), match.group(2), match.start(), match.end()))
    for match in FILE_URL_RE.finditer(text):
        if any(m.start() <= match.start() < m.end() for m in markdown_matches):
            continue
        url = "file://" + match.group(1).rstrip(".,;:!?")
        links.append((url, url, match.start(), match.end()))
    return links


def extract_links_from_file(path):
    links = []
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            for lineno, line in enumerate(handle, 1):
                for text, url, _start, _end in extract_links(line):
                    links.append((text, url, lineno))
    except OSError as exc:
        print(f"warning: cannot read {path}: {exc}", file=sys.stderr)
    return links


def resolve_file_path(url, source_file):
    rest = url.removeprefix("file://")
    rest = rest.split("#", 1)[0]
    rest = unquote(rest)
    rest = os.path.expanduser(rest)
    path = Path(rest)
    if not path.is_absolute():
        path = Path(source_file).resolve().parent / path
    return Path(os.path.normpath(path))


def check_file(path):
    if os.path.exists(path):
        return "ok", True
    return "n/a", False


def check_http(url, timeout):
    code = None
    for _ in range(10):
        try:
            request = Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=timeout) as response:
                return str(response.status), response.status == 200
        except HTTPError as exc:
            code = exc.code
            if code not in (301, 302, 303, 307, 308):
                return str(code), False
            location = exc.headers.get("Location")
            if not location:
                return str(code), False
            url = urljoin(url, location)
        except (URLError, OSError, ValueError) as exc:
            return "error: " + str(exc), False
    return str(code), False


def check_link(url, source_file, timeout):
    parsed = urlparse(url)
    if parsed.scheme in ("http", "https"):
        return check_http(url, timeout)
    if url.startswith("#"):
        return "ok", True
    if parsed.scheme in ("", "file"):
        return check_file(resolve_file_path(url, source_file))
    return "ok", True


def run(workdir, timeout, workers):
    md_files = scan_md_files(workdir)
    jobs = []
    for md_file in md_files:
        for text, url, lineno in extract_links_from_file(md_file):
            jobs.append((text, url, str(md_file), lineno))

    def check(job):
        text, url, source, lineno = job
        status, ok = check_link(url, source, timeout)
        return LinkResult(text, url, source, lineno, status, ok)

    if workers > 1:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(check, jobs))
    else:
        results = [check(job) for job in jobs]
    return results, md_files


def build_table(broken):
    def cell(value):
        return str(value).replace("|", "\\|").replace("\n", " ")

    lines = ["| Link Text | Link | Source File | Status |", "|---|---|---|---|"]
    for result in broken:
        lines.append(
            f"| {cell(result.text)} | {cell(result.url)} | {cell(result.source)}:{result.line} | {cell(result.status)} |"
        )
    return "\n".join(lines)


def format_stats(total, healthy, broken, files):
    return (
        f"Total links checked: {total}\n"
        f"Total files scanned: {files}\n"
        f"Healthy: {healthy}\n"
        f"Broken: {broken}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="linckchecker",
        description="Markdown Link & Dead Code Checker",
    )
    parser.add_argument(
        "--workdir",
        default="./",
        help="directory to scan for .md files (default: current directory)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="HTTP request timeout in seconds (default: 10)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="number of parallel link checks (default: 10)",
    )
    args = parser.parse_args(argv)
    if not os.path.isdir(args.workdir):
        print(f"error: workdir does not exist: {args.workdir}", file=sys.stderr)
        return 1
    results, md_files = run(args.workdir, args.timeout, args.workers)
    broken = sorted((r for r in results if not r.ok), key=lambda r: (r.source, r.line))
    if broken:
        print(build_table(broken))
    else:
        print("No broken links found.")
    print()
    print(
        format_stats(
            len(results),
            len(results) - len(broken),
            len(broken),
            len(md_files),
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
