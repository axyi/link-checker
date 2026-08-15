import http.server
import socket
import threading
import time

import pytest

import linckchecker as lc


class Handler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.handle_request()

    def do_GET(self):
        self.handle_request()

    def handle_request(self):
        if self.path == "/redirect":
            self.send_response(301)
            self.send_header("Location", "/ok")
        elif self.path == "/redirect-loop":
            self.send_response(302)
            self.send_header("Location", "/redirect-loop")
        elif self.path == "/missing":
            self.send_response(404)
        elif self.path == "/error":
            self.send_response(500)
        else:
            self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, format, *args):
        pass


@pytest.fixture(scope="module")
def http_server():
    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()


def server_url(http_server, path):
    return f"http://127.0.0.1:{http_server.server_address[1]}{path}"


def test_scan_md_files_finds_nested_files(tmp_path):
    (tmp_path / "a.md").write_text("")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.md").write_text("")
    (tmp_path / "notes.txt").write_text("")
    files = lc.scan_md_files(str(tmp_path))
    assert [f.name for f in files] == ["a.md", "b.md"]


def test_scan_md_files_missing_dir_returns_empty():
    assert lc.scan_md_files("/nonexistent/dir") == []


def test_extract_links_finds_markdown_links():
    text = (
        "see [docs](guide.md) and [site] (https://example.com/page) and ![img](pic.png)"
    )
    links = lc.extract_links(text)
    assert [(t, u) for t, u, _, _ in links] == [
        ("docs", "guide.md"),
        ("site", "https://example.com/page"),
        ("img", "pic.png"),
    ]


def test_extract_links_finds_file_urls():
    text = "open file:///etc/hosts now or file:///tmp/x.md"
    links = lc.extract_links(text)
    assert [(t, u) for t, u, _, _ in links] == [
        ("file:///etc/hosts", "file:///etc/hosts"),
        ("file:///tmp/x.md", "file:///tmp/x.md"),
    ]


def test_extract_links_file_url_inside_markdown_link_not_duplicated():
    text = "[notes](file:///tmp/notes.md)"
    links = lc.extract_links(text)
    assert [(t, u) for t, u, _, _ in links] == [("notes", "file:///tmp/notes.md")]


def test_extract_links_strips_trailing_punctuation_from_file_urls():
    text = "see file:///tmp/a.md, done."
    links = lc.extract_links(text)
    assert [(t, u) for t, u, _, _ in links] == [
        ("file:///tmp/a.md", "file:///tmp/a.md")
    ]


def test_extract_links_from_file_reports_line_numbers(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text(
        "line one\n[broken](missing.md)\nfile:///etc/hosts\n", encoding="utf-8"
    )
    links = lc.extract_links_from_file(md)
    assert links == [
        ("broken", "missing.md", 2),
        ("file:///etc/hosts", "file:///etc/hosts", 3),
    ]


def test_resolve_file_path_absolute_file_url():
    path = lc.resolve_file_path("file:///etc/hosts", "/src/doc.md")
    assert str(path) == "/etc/hosts"


def test_resolve_file_path_relative_to_source(tmp_path):
    source = tmp_path / "docs" / "page.md"
    source.parent.mkdir()
    path = lc.resolve_file_path("../img/x.png", str(source))
    assert path == (tmp_path / "img" / "x.png")


def test_resolve_file_path_unquotes_and_strips_fragment(tmp_path):
    source = tmp_path / "doc.md"
    path = lc.resolve_file_path(
        "file://" + str(tmp_path / "My%20File.md") + "#sec", str(source)
    )
    assert path == (tmp_path / "My File.md")


def test_check_file_exists(tmp_path):
    target = tmp_path / "x.md"
    target.write_text("x")
    assert lc.check_file(target) == ("ok", True)


def test_check_file_missing_returns_na(tmp_path):
    assert lc.check_file(tmp_path / "nope.md") == ("n/a", False)


def test_check_file_follows_symlink(tmp_path):
    target = tmp_path / "real.md"
    target.write_text("x")
    link = tmp_path / "alias.md"
    link.symlink_to(target)
    assert lc.check_file(link) == ("ok", True)


def test_check_http_ok(http_server):
    status, ok = lc.check_http(server_url(http_server, "/ok"), 5)
    assert (status, ok) == ("200", True)


def test_check_http_follows_redirect(http_server):
    status, ok = lc.check_http(server_url(http_server, "/redirect"), 5)
    assert (status, ok) == ("200", True)


def test_check_http_not_found(http_server):
    status, ok = lc.check_http(server_url(http_server, "/missing"), 5)
    assert (status, ok) == ("404", False)


def test_check_http_server_error(http_server):
    status, ok = lc.check_http(server_url(http_server, "/error"), 5)
    assert (status, ok) == ("500", False)


def test_check_http_redirect_loop(http_server):
    status, ok = lc.check_http(server_url(http_server, "/redirect-loop"), 5)
    assert ok is False
    assert status == "302"


def test_check_http_connection_error():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    status, ok = lc.check_http(f"http://127.0.0.1:{port}/x", 5)
    assert ok is False
    assert status.startswith("error")


def test_check_http_invalid_url():
    status, ok = lc.check_http("not-a-url", 5)
    assert ok is False
    assert status.startswith("error")


def test_check_http_timeout():
    server = socket.socket()
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]

    def serve():
        conn, _ = server.accept()
        time.sleep(2)
        conn.close()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    status, ok = lc.check_http(f"http://127.0.0.1:{port}/slow", 0.3)
    server.close()
    assert ok is False
    assert status.startswith("error")


def test_check_link_http(http_server):
    status, ok = lc.check_link(server_url(http_server, "/missing"), "/src/doc.md", 5)
    assert (status, ok) == ("404", False)


def test_check_link_relative_file(tmp_path):
    source = tmp_path / "doc.md"
    target = tmp_path / "exists.md"
    target.write_text("x")
    assert lc.check_link("exists.md", str(source), 5) == ("ok", True)
    assert lc.check_link("missing.md", str(source), 5) == ("n/a", False)


def test_check_link_file_url(tmp_path):
    target = tmp_path / "t.md"
    target.write_text("x")
    assert lc.check_link("file://" + str(target), str(tmp_path / "d.md"), 5) == (
        "ok",
        True,
    )


def test_check_link_anchor_is_ok(tmp_path):
    assert lc.check_link("#section", str(tmp_path / "d.md"), 5) == ("ok", True)


def test_check_link_unknown_scheme_is_ok(tmp_path):
    assert lc.check_link("mailto:user@example.com", str(tmp_path / "d.md"), 5) == (
        "ok",
        True,
    )


def test_run_collects_statuses(tmp_path, http_server):
    port = http_server.server_address[1]
    md = tmp_path / "doc.md"
    md.write_text(
        f"[good](http://127.0.0.1:{port}/ok)\n"
        f"[bad](http://127.0.0.1:{port}/missing)\n"
        "[local](present.md)\n"
        "[gone](../nope.md)\n"
    )
    (tmp_path / "present.md").write_text("x")
    results, files = lc.run(str(tmp_path), 5, 1)
    assert len(files) == 2
    by_url = {r.url: r for r in results}
    assert by_url[f"http://127.0.0.1:{port}/ok"].status == "200"
    assert by_url[f"http://127.0.0.1:{port}/missing"].status == "404"
    assert by_url["present.md"].ok is True
    assert by_url["../nope.md"].status == "n/a"


def test_run_parallel_matches_sequential(tmp_path, http_server):
    port = http_server.server_address[1]
    md = tmp_path / "doc.md"
    md.write_text(
        f"[a](http://127.0.0.1:{port}/ok)\n"
        f"[b](http://127.0.0.1:{port}/missing)\n"
        "[c](present.md)\n"
    )
    (tmp_path / "present.md").write_text("x")
    sequential, _ = lc.run(str(tmp_path), 5, 1)
    parallel, _ = lc.run(str(tmp_path), 5, 4)
    assert [(r.url, r.status, r.ok) for r in parallel] == [
        (r.url, r.status, r.ok) for r in sequential
    ]


def test_build_table_formats_broken_links():
    broken = [lc.LinkResult("a|b", "http://x", "/s/doc.md", 3, "404", False)]
    table = lc.build_table(broken)
    assert table.splitlines()[0] == "| Link Text | Link | Source File | Status |"
    assert table.splitlines()[1] == "|---|---|---|---|"
    assert "| a\\|b | http://x | /s/doc.md:3 | 404 |" in table


def test_format_stats():
    out = lc.format_stats(10, 7, 3, 2)
    assert "Total links checked: 10" in out
    assert "Total files scanned: 2" in out
    assert "Healthy: 7" in out
    assert "Broken: 3" in out


def test_main_reports_broken_links(tmp_path, http_server, capsys, monkeypatch):
    port = http_server.server_address[1]
    (tmp_path / "readme.md").write_text(
        f"[ok](http://127.0.0.1:{port}/ok)\n"
        f"[broken](http://127.0.0.1:{port}/missing)\n"
        "[file](missing.md)\n"
    )
    monkeypatch.chdir(tmp_path)
    code = lc.main(["--workdir", str(tmp_path), "--timeout", "5", "--workers", "1"])
    out = capsys.readouterr().out
    assert code == 0
    assert "| Link Text | Link | Source File | Status |" in out
    assert f"http://127.0.0.1:{port}/missing" in out
    assert "404" in out
    assert "missing.md" in out
    assert "n/a" in out
    assert "Total links checked: 3" in out
    assert "Healthy: 1" in out
    assert "Broken: 2" in out


def test_main_no_broken_links(tmp_path, capsys, monkeypatch):
    (tmp_path / "readme.md").write_text("[local](present.md)\n")
    (tmp_path / "present.md").write_text("x")
    monkeypatch.chdir(tmp_path)
    code = lc.main(["--workdir", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == 0
    assert "No broken links found." in out
    assert "Broken: 0" in out


def test_main_invalid_workdir(capsys):
    code = lc.main(["--workdir", "/nonexistent/path"])
    assert code == 1
