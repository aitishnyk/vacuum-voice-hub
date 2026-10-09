"""Fail-closed comparison of discovered robot model capabilities.

Compatible semantic events or equal adapters do not authorize installation.
"""
from .catalog import model_by_id, event_profile_for_model


def summarize_model(model_id):
    model = model_by_id(model_id)
    profile = event_profile_for_model(model["id"])
    transport = model.get("transport", {})
    return {
        "id": model["id"],
        "name": model["name"],
        "brand": model.get("vendor"),
        "adapter": model["adapter"],
        "event_profile": profile["id"],
        "known_event_ids": sorted({int(x) for x in profile["known_event_ids"]}),
        "event_count": len(profile["known_event_ids"]),
        "package_container": (model.get("package") or {}).get("container"),
        "device_tested": bool(model.get("device_tested")),
        "custom_install_status": (
            "previously-hardware-verified" if model.get("device_tested")
            else "community-experimental" if transport.get("kind") in {
                "miot-local-property", "roborock-miio-sound", "miot-action-url-md5"
            }
            else "vendor-signed-only" if transport.get("kind") == "signed-official-only"
            else "build-only"
        ),
        "install_default": bool(transport.get("allow_default")),
        "identity_source": model.get("catalog_source"),
        "transport_source": transport.get("evidence"),
    }


def compare_models(left_id, right_id):
    """Compare model event overlap and packaging without changing any policy."""
    left = summarize_model(left_id)
    right = summarize_model(right_id)
    a, b = set(left.pop("known_event_ids")), set(right.pop("known_event_ids"))
    overlap = sorted(a & b)
    return {
        "schema": "vvh.model-comparison.v1",
        "left": left, "right": right,
        "common_event_count": len(overlap),
        "common_event_ids": overlap,
        "left_only_event_ids": sorted(a - b),
        "right_only_event_ids": sorted(b - a),
        "event_overlap_left_pct": round(100 * len(overlap) / len(a), 1) if a else 0,
        "event_overlap_right_pct": round(100 * len(overlap) / len(b), 1) if b else 0,
        "same_build_adapter": left["adapter"] == right["adapter"],
        "same_package_container": left["package_container"] == right["package_container"],
        "custom_install_compatibility_proved": False,
        "install_authorized_by_comparison": False,
        "note": "Event/adapter overlap is a research hint, not proof of firmware, voice package signature or custom-install transport.",
    }
