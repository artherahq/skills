"""asset_lint 测试: emoji-as-icon / 无来源长 SVG path / 混用图标库
三条可机械核对的 Quality gate 规则。"""

import tempfile
from pathlib import Path

from asset_lint import demo, lint_file, lint_paths


def test_demo_trips_all_three_checkable_rules():
    assert demo() == 0


def _write(tmp: Path, name: str, content: str) -> Path:
    p = tmp / name
    p.write_text(content, encoding="utf-8")
    return p


# ───────────────────────────── emoji_icon ──────────────────────────────────

def test_emoji_in_code_flagged():
    with tempfile.TemporaryDirectory() as td:
        f = _write(Path(td), "a.tsx", 'const icon = "\U0001F680";\n')
        violations = lint_file(f)
        assert any(v["rule"] == "emoji_icon" and v["severity"] == "error" for v in violations)


def test_no_emoji_no_violation():
    with tempfile.TemporaryDirectory() as td:
        f = _write(Path(td), "a.tsx", 'import { Home } from "lucide-react";\n')
        violations = lint_file(f)
        assert not any(v["rule"] == "emoji_icon" for v in violations)


# ───────────────────────────── invented_svg_path ───────────────────────────

def test_long_uncited_svg_path_flagged():
    with tempfile.TemporaryDirectory() as td:
        content = ('const logo = <svg><path d="M83.4 12.1c-5.2-3.1-11.9-3.1-17.1 0-14.2 '
                    '8.5-22.9 24.1-22.9 40.9v55c0 16.8" /></svg>;\n')
        f = _write(Path(td), "a.tsx", content)
        violations = lint_file(f)
        assert any(v["rule"] == "invented_svg_path" for v in violations)


def test_short_svg_path_not_flagged():
    with tempfile.TemporaryDirectory() as td:
        f = _write(Path(td), "a.tsx", '<path d="M4 4L8 8" />\n')
        violations = lint_file(f)
        assert not any(v["rule"] == "invented_svg_path" for v in violations)


def test_long_svg_path_with_source_citation_not_flagged():
    with tempfile.TemporaryDirectory() as td:
        content = (
            "// source: simple-icons, verified\n"
            'const logo = <svg><path d="M83.4 12.1c-5.2-3.1-11.9-3.1-17.1 0-14.2 '
            '8.5-22.9 24.1-22.9 40.9v55c0 16.8" /></svg>;\n'
        )
        f = _write(Path(td), "a.tsx", content)
        violations = lint_file(f)
        assert not any(v["rule"] == "invented_svg_path" for v in violations)


# ───────────────────────────── mixed_icon_set ──────────────────────────────

def test_single_icon_library_not_flagged():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        _write(tmp, "a.tsx", 'import { Home } from "lucide-react";\n')
        _write(tmp, "b.tsx", 'import { ArrowRight } from "lucide-react";\n')
        result = lint_paths([str(tmp)])
        assert not any(v["rule"] == "mixed_icon_set" for v in result["violations"])


def test_two_icon_libraries_flagged():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        _write(tmp, "a.tsx", 'import { Home } from "lucide-react";\n')
        _write(tmp, "b.tsx", 'import { Bell } from "@heroicons/react/24/outline";\n')
        result = lint_paths([str(tmp)])
        assert any(v["rule"] == "mixed_icon_set" for v in result["violations"])
        assert result["icon_libraries_seen"].keys() == {"lucide", "heroicons"}


# ───────────────────────────── verdict ─────────────────────────────────────

def test_verdict_fail_only_on_error_severity():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        # only a warn-severity finding (mixed set), no emoji -> WARN not FAIL
        _write(tmp, "a.tsx", 'import { Home } from "lucide-react";\n')
        _write(tmp, "b.tsx", 'import { Bell } from "@heroicons/react/24/outline";\n')
        result = lint_paths([str(tmp)])
        assert result["verdict"] == "WARN"


def test_verdict_pass_on_clean_paths():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        _write(tmp, "a.tsx", 'import { Home } from "lucide-react";\nconst x = <Home size={16} />;\n')
        result = lint_paths([str(tmp)])
        assert result["verdict"] == "PASS"
        assert result["violations"] == []
