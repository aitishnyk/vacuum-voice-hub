"""v0.17 offline returned-review import, history and hardware evidence gates."""
import hashlib
import json
import math
import struct
import subprocess
import sys
import wave
import zipfile
from pathlib import Path

import pytest

from vacuum_voice_hub.creator import assign_audio, new_workspace
from vacuum_voice_hub.production_review import (
    create_review, mark_review, audit_review, export_review_bundle
)
from vacuum_voice_hub.review_handoff import import_review
from vacuum_voice_hub.review_history import audit_review_history
from vacuum_voice_hub.hardware_acceptance import assess_hardware_acceptance
from vacuum_voice_hub.transport_evidence import EvidenceError


def _wav(path, hz=440):
    samples = [int(5000*math.sin(2*math.pi*hz*i/16000)) for i in range(16000)]
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes(struct.pack("<"+"h"*len(samples),*samples))


@pytest.fixture
def review_bundle(tmp_path):
    workspace=tmp_path/"workspace"
    new_workspace(workspace,pack_id="handoff",name="Handoff",
                  author="Author",language="ru",license_name="UNLICENSED")
    wavefile=tmp_path/"input.wav"
    _wav(wavefile)
    assign_audio(workspace,"clean.start",wavefile)
    review=tmp_path/"source-review.json"
    create_review(workspace,"ru","dreame.vacuum.r2209",review)
    mark_review(review,"clean.start","recorded")
    mark_review(review,"clean.start","listened",reviewer="External listener")
    mark_review(review,"clean.start","approved",reviewer="External listener",
                language_attested=True,rights_attested=True)
    metadata=tmp_path/"metadata.zip"
    with_audio=tmp_path/"with-audio.zip"
    export_review_bundle(review,metadata)
    export_review_bundle(review,with_audio,include_audio=True)
    return workspace,review,metadata,with_audio


@pytest.mark.parametrize("with_audio", [False, True])
def test_roundtrip_remote_approval_imported_only_as_untrusted_claim(review_bundle,tmp_path,with_audio):
    root,prior,plain,attached=review_bundle
    src=attached if with_audio else plain
    dest=tmp_path/("imported-audio.json" if with_audio else "imported-metadata.json")
    before=(root/"audio"/"clean.start.wav").read_bytes()
    result=import_review(src,root,dest,expected_model="dreame.vacuum.r2209",expected_locale="ru")
    assert result["local_approvals_transferred"]==0
    assert result["claims"]["approved"]==1
    assert result["install_authorized"] is False
    assert result["embedded_audio_checked"]==int(with_audio)
    assert (root/"audio"/"clean.start.wav").read_bytes()==before
    data=json.loads(dest.read_text())
    task=next(t for t in data["tasks"] if t["semantic"]=="clean.start")
    assert task["external_review_claim"]["status"]=="approved"
    assert task["external_review_claim"]["trusted"] is False
    assert task["review"]["status"]=="draft"
    assert audit_review(dest)["approved_with_matching_audio"]==0
    assert audit_review_history(dest)["events"]==1
    mark_review(dest,"clean.start","recorded")
    assert audit_review_history(dest)["events"]==2


def test_import_plain_review_json_with_explicit_workspace_binding(review_bundle,tmp_path):
    root,prior,_,_=review_bundle
    dest=tmp_path/"returned-plain.json"
    report=import_review(prior,root,dest)
    assert report["claims"]["approved"]==1
    assert report["local_approvals_transferred"]==0
    assert audit_review(dest)["valid"]


def test_import_refuses_wrong_project_model_and_locale(review_bundle,tmp_path):
    root,prior,plain,_=review_bundle
    with pytest.raises(ValueError,match="model"):
        import_review(plain,root,tmp_path/"wrong-model.json",expected_model="viomi.vacuum.v60")
    with pytest.raises(ValueError,match="locale"):
        import_review(plain,root,tmp_path/"wrong-locale.json",expected_locale="uk")
    other=tmp_path/"different"
    new_workspace(other,pack_id="different",name="Other",author="QA",language="ru")
    with pytest.raises(ValueError,match="pack ID"):
        import_review(plain,other,tmp_path/"wrong-project.json")
    assert not (tmp_path/"wrong-model.json").exists()


def test_import_blocks_stale_audio_without_mutating_creator(review_bundle,tmp_path):
    root,prior,plain,_=review_bundle
    recorded=root/"audio"/"clean.start.wav"
    _wav(recorded,555)
    bad=tmp_path/"stale.json"
    with pytest.raises(ValueError,match="audio|manifest"):
        import_review(plain,root,bad)
    assert not bad.exists()


def test_zip_traversal_extra_entry_and_duplicate_rejected(review_bundle,tmp_path):
    root,prior,plain,_=review_bundle
    with zipfile.ZipFile(plain) as source:
        contents={x:source.read(x) for x in source.namelist()}
    for name,extras in (
        ("traversal",{"../evil.json":b"secret"}),
        ("extra",{"unexpected.bin":b"anything"}),
    ):
        candidate=tmp_path/(name+".zip")
        with zipfile.ZipFile(candidate,"w") as target:
            for part,data in {**contents,**extras}.items():target.writestr(part,data)
        with pytest.raises(ValueError,match="review ZIP|unsafe"):
            import_review(candidate,root,tmp_path/(name+".json"))
    duplicate=tmp_path/"duplicate.zip"
    with zipfile.ZipFile(duplicate,"w") as target:
        for part,data in contents.items():target.writestr(part,data)
        target.writestr("review.json",contents["review.json"])
    with pytest.raises(ValueError,match="duplicate"):
        import_review(duplicate,root,tmp_path/"duplicate.json")


def test_zip_audio_bytes_do_not_get_installed_and_hashes_checked(review_bundle,tmp_path):
    root,prior,_,attached=review_bundle
    corrupted=tmp_path/"corrupted.zip"
    with zipfile.ZipFile(attached) as archive:
        members={n:archive.read(n) for n in archive.namelist()}
    members["audio/audio/clean.start.wav"]=b"evil"
    with zipfile.ZipFile(corrupted,"w") as target:
        for name,data in members.items():target.writestr(name,data)
    with pytest.raises(ValueError,match="audio inside"):
        import_review(corrupted,root,tmp_path/"unsafe.json")
    assert not (tmp_path/"unsafe.json").exists()


def test_import_destination_existing_never_overwritten(review_bundle,tmp_path):
    root,prior,plain,_=review_bundle
    dest=tmp_path/"keep.json"
    dest.write_text("USER DATA")
    with pytest.raises(FileExistsError):
        import_review(plain,root,dest)
    assert dest.read_text()=="USER DATA"


def test_local_history_detects_corrupted_line_and_out_of_band_review(review_bundle,tmp_path):
    root,review,_,_=review_bundle
    baseline=audit_review_history(review)
    assert baseline["events"]==3
    history=Path(baseline["file"])
    history.write_bytes(history.read_bytes().replace(b"review-mark",b"review-fake",1))
    with pytest.raises(ValueError,match="hash chain"):
        audit_review_history(review)
    with pytest.raises(ValueError,match="hash chain"):
        mark_review(review,"clean.start","draft")
    # Independent source proof is NOT created by a local hash chain.
    assert baseline["cryptographically_authenticated"] is False


def test_source_review_modified_without_history_is_detected(review_bundle):
    _,review,_,_=review_bundle
    record=json.loads(review.read_text())
    record["tasks"][0]["review"]["note"]="changed"
    review.write_text(json.dumps(record))
    with pytest.raises(ValueError,match="review file changed"):
        audit_review_history(review)


def test_cli_reviewer_import_and_history(review_bundle,tmp_path):
    root,source,plain,_=review_bundle
    path=tmp_path/"cli-import.json"
    cmd=[sys.executable,"-m","vacuum_voice_hub","creator","review"]
    result=subprocess.run(cmd+["import",str(plain),"--workspace",str(root),"--output",str(path),
                               "--model","dreame.vacuum.r2209","--language","ru"],
                          capture_output=True,text=True,check=True)
    assert json.loads(result.stdout)["local_approvals_transferred"]==0
    history=subprocess.run(cmd+["history",str(path)],
                           capture_output=True,text=True,check=True)
    assert json.loads(history.stdout)["events"]==1


def _hardware():
    return {
        "schema":"vvh.hardware-acceptance.v1",
        "model_id":"roborock.vacuum.a75",
        "firmware":"4.1.0-claimed",
        "package":{"sha256":"a"*64,"size_bytes":10240},
        "observations":{
            key:{"observed":False,"reference":None}
            for key in ("package_signature_reviewed","device_download_observed",
                        "device_playback_heard","reboot_persistence_checked",
                        "stock_rollback_tested")
        },
    }


def test_hardware_acceptance_is_non_authorizing_even_with_five_claims(tmp_path):
    record=_hardware()
    report=assess_hardware_acceptance(record)
    assert len(report["missing_steps"])==5
    assert report["status"]=="incomplete-research-only"
    assert report["install_authorized"] is False
    for field in record["observations"]:
        record["observations"][field]={"observed":True,
                                       "reference":"https://example.org/acceptance/"+field}
    done=assess_hardware_acceptance(record)
    assert done["status"]=="ready-for-independent-hardware-review"
    assert done["install_authorized"] is False
    assert done["transport_policy_changed"] is False
    assert done["evidence_independently_verified"] is False
    assert not done["manufacturer_signature_automatically_verified"]


def test_hardware_acceptance_rejects_secrets_unknown_id_and_forged_structure():
    record=_hardware()
    record["access_token"]="sensitive"
    with pytest.raises(EvidenceError,match="sensitive"):
        assess_hardware_acceptance(record)
    del record["access_token"]
    record["model_id"]="no.vacuum.model"
    with pytest.raises(KeyError):
        assess_hardware_acceptance(record)
    record["model_id"]="roborock.vacuum.a75"
    record["observations"]["device_playback_heard"]["observed"]=True
    with pytest.raises(EvidenceError,match="evidence link"):
        assess_hardware_acceptance(record)
