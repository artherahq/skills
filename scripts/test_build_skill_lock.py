import json
from pathlib import Path

from build_skill_lock import build_lock, skill_tree_sha256


def test_build_lock_namespaces_and_hashes_marketplace_skills(tmp_path):
    (tmp_path / ".claude-plugin").mkdir()
    skill = tmp_path / "skills" / "sample-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("sample", encoding="utf-8")
    (tmp_path / ".claude-plugin" / "marketplace.json").write_text(
        json.dumps({
            "metadata": {"version": "1.2.3"},
            "plugins": [{
                "name": "sample-plugin",
                "skills": ["./skills/sample-skill"],
            }],
        }),
        encoding="utf-8",
    )

    lock = build_lock(tmp_path)

    entry = lock["skills"]["sample-plugin:sample-skill"]
    assert entry["version"] == "1.2.3"
    assert entry["sha256"] == skill_tree_sha256(skill)
