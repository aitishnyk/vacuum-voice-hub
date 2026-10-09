"""Deterministic offline batch mastering previews with all-or-nothing output.

Batch results are audition candidates only, never source-file replacements,
copyright verification or robot custom-voice installation authorization.
"""
import json
import shutil
from pathlib import Path

from .audio_advanced import SOURCE_SUFFIXES
from .audio_mastering import master_preview


def master_batch(input_dir, output_dir, *, max_files=64, target_peak_dbfs=-3.0,
                 silence_dbfs=-45.0, padding_ms=80, fade_ms=8,
                 trim_silence=True):
    """Process immediate audio children into a NEW folder, rollback on failure.

    Reject ambiguous stems (also casefolded for Windows/macOS portability) and
    any symlinked input. No traversal or automatic network fetching.
    """
    if type(max_files) is not int or not 1 <= max_files <= 256:
        raise ValueError("max_files must be an integer from 1 to 256")
    root_input = Path(input_dir).expanduser().absolute()
    if root_input.is_symlink() or not root_input.is_dir():
        raise ValueError("input must be an existing non-symlink directory")
    source_root = root_input.resolve(strict=True)
    dest = Path(output_dir).expanduser().absolute()
    if dest.exists() or dest.is_symlink():
        raise FileExistsError(f"batch output must be a new directory: {dest}")
    if dest.resolve() == source_root:
        raise ValueError("batch output must be different from input directory")
    sources = []
    for path in source_root.iterdir():
        if path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"symlink or unsupported audio entry: {path.name}")
        sources.append(path)
    sources.sort(key=lambda p: (p.name.casefold(), p.name))
    if not 1 <= len(sources) <= max_files:
        raise ValueError(f"batch must contain 1..{max_files} audio files")
    names = [(p.stem + ".wav") for p in sources]
    folded = [n.casefold() for n in names]
    if len(set(folded)) != len(folded) or "batch-mastering.json" in folded:
        raise ValueError("batch output filenames collide after WAV conversion")
    # All argument bounds and individual source checks take place before a
    # finished manifest is published. A partial new output is always removed.
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.mkdir(exist_ok=False)
    try:
        rows = []
        for source, name in zip(sources, names):
            result = master_preview(
                source, dest / name, target_peak_dbfs=target_peak_dbfs,
                silence_dbfs=silence_dbfs, padding_ms=padding_ms,
                fade_ms=fade_ms, trim_silence=trim_silence
            )
            rows.append({
                "source_name": source.name,
                "source_sha256": result["source_sha256"],
                "output_name": name,
                "output_sha256": result["output_sha256"],
                "output_bytes": result["bytes"],
                "before": result["before"],
                "after": result["after"],
                "removed_leading_frames": result["removed_leading_frames"],
                "removed_trailing_frames": result["removed_trailing_frames"],
            })
        manifest = {
            "schema": "vvh.master-batch.v1",
            "input_count": len(sources),
            "model_identity_required_for_install": True,
            "clip_processing": {
                "target_peak_dbfs": float(target_peak_dbfs),
                "silence_dbfs": float(silence_dbfs),
                "padding_ms": float(padding_ms),
                "fade_ms": float(fade_ms),
                "trim_silence": bool(trim_silence),
            },
            "clips": rows,
            "human_review_required": True,
            "creator_manifest_changed": False,
            "redistribution_verified": False,
            "install_authorized": False,
        }
        with (dest / "batch-mastering.json").open("x", encoding="utf-8") as stream:
            json.dump(manifest, stream, indent=2, ensure_ascii=False, sort_keys=True)
            stream.write("\n")
        return {
            "schema": manifest["schema"],
            "output_dir": str(dest), "clip_count": len(rows),
            "manifest": str(dest / "batch-mastering.json"),
            "human_review_required": True,
            "creator_manifest_changed": False, "install_authorized": False,
            "redistribution_verified": False,
        }
    except BaseException:
        shutil.rmtree(dest)
        raise
