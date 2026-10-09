"""v1.6 metadata-only moderated community hardware evidence queue."""
import copy
import hashlib
import json
import subprocess
import sys

import pytest

from vacuum_voice_hub.community_inbox import (
    init_inbox, add_report, moderate_report, audit_inbox
)
from vacuum_voice_hub.hardware_acceptance import FIELDS


def report(folder, *, all_steps=False, model="dreame.vacuum.r2209", secret=False):
    value = {
        "schema": "vvh.hardware-acceptance.v1", "model_id": model,
        "firmware": "1.2.3",
        "package": {"sha256": "a" * 64, "size_bytes": 100},
        "observations": {name: {"observed": all_steps,
                                "reference": "https://example.org/" + name if all_steps else None}
                         for name in FIELDS},
    }
    if secret:
        value["device_token"] = "private"
    path = folder / "volunteer.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_intake_is_copy_on_write_and_redacted(tmp_path):
    initial = tmp_path / "initial.json"
    imported = tmp_path / "imported.json"
    src = report(tmp_path, all_steps=True)
    init_inbox(initial)
    before = hashlib.sha256(initial.read_bytes()).hexdigest()
    added = add_report(initial, src, imported)
    assert added["submission_count"] == 1
    assert added["pending_count"] == 1
    assert added["independent_device_verified"] is False
    assert hashlib.sha256(initial.read_bytes()).hexdigest() == before
    contents = imported.read_text()
    assert "https://example.org" not in contents
    assert str(tmp_path) not in contents
    assert "device_token" not in contents
    assert audit_inbox(imported)["submission_count"] == 1
    with pytest.raises(FileExistsError):
        add_report(initial, src, imported)


def test_human_research_decision_does_not_grant_install(tmp_path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    reviewed = tmp_path / "reviewed.json"
    evidence = report(tmp_path, all_steps=True)
    init_inbox(first)
    added = add_report(first, evidence, second)
    item = json.loads(second.read_text())["submissions"][0]["id"]
    decision = moderate_report(second, item, "research-accepted",
                               "Voluntary reviewer", "Report structure checked", reviewed)
    assert decision["decision_counts"]["research-accepted"] == 1
    assert decision["independent_device_verified"] is False
    assert not decision["install_authorized"]
    assert audit_inbox(second)["pending_count"] == 1
    assert audit_inbox(reviewed)["pending_count"] == 0
    with pytest.raises(ValueError, match="already reviewed"):
        moderate_report(reviewed, item, "research-accepted", "Reviewer", "Again",
                        tmp_path / "illegal.json")


def test_secret_and_invalid_model_reports_fail_closed(tmp_path):
    initial = tmp_path / "initial.json"
    init_inbox(initial)
    source = report(tmp_path, secret=True)
    with pytest.raises(ValueError, match="sensitive"):
        add_report(initial, source, tmp_path / "never.json")
    report(tmp_path, model="not.a.real.model")
    with pytest.raises(KeyError):
        add_report(initial, source, tmp_path / "never.json")
    assert not (tmp_path / "never.json").exists()


def test_duplicate_and_symlink_reports_refused(tmp_path):
    initial = tmp_path / "initial.json"
    imported = tmp_path / "imported.json"
    init_inbox(initial)
    source = report(tmp_path)
    add_report(initial, source, imported)
    with pytest.raises(ValueError, match="duplicate"):
        add_report(imported, source, tmp_path / "duplicate.json")
    link = tmp_path / "link.json"
    link.symlink_to(source)
    with pytest.raises(ValueError, match="regular"):
        add_report(initial, link, tmp_path / "linked.json")


def test_no_unattributed_decisions_and_no_silent_overwrite(tmp_path):
    init_inbox(tmp_path / "empty.json")
    assert audit_inbox(tmp_path / "empty.json")["submission_count"] == 0
    with pytest.raises(FileExistsError):
        init_inbox(tmp_path / "empty.json")
    with pytest.raises(ValueError, match="unknown submission"):
        moderate_report(tmp_path / "empty.json", "b" * 64, "rejected",
                        "Reviewer", "Reason", tmp_path / "out.json")
    assert not (tmp_path / "out.json").exists()


def test_modified_snapshot_and_history_rejected(tmp_path):
    p0 = tmp_path / "s0.json"
    p1 = tmp_path / "s1.json"
    p2 = tmp_path / "s2.json"
    init_inbox(p0)
    add_report(p0, report(tmp_path), p1)
    doc = json.loads(p1.read_text())
    item_id = doc["submissions"][0]["id"]
    moderate_report(p1, item_id, "needs-evidence", "Reviewer", "Firmware log needed", p2)
    edited = json.loads(p2.read_text())
    edited["reviews"][0]["decision"] = "research-accepted"
    p2.write_text(json.dumps(edited))
    with pytest.raises(ValueError, match="checksum"):
        audit_inbox(p2)


def test_cli_end_to_end(tmp_path):
    source = report(tmp_path)
    old, nxt, last = (tmp_path / s for s in ("a.json", "b.json", "c.json"))
    cmd = [sys.executable, "-m", "vacuum_voice_hub", "community"]
    def run(*parts):
        return json.loads(subprocess.run(cmd+list(parts), capture_output=True,
                                         text=True, check=True).stdout)
    run("init", "--output", str(old))
    added = run("add", str(old), "--report", str(source), "--output", str(nxt))
    assert added["submission_count"] == 1
    item_id = json.loads(nxt.read_text())["submissions"][0]["id"]
    review = run("moderate", str(nxt), "--submission", item_id,
                 "--decision", "needs-evidence", "--reviewer", "Reviewer",
                 "--note", "More proof required", "--output", str(last))
    assert review["review_count"] == 1
    assert run("audit", str(last))["pending_count"] == 0
