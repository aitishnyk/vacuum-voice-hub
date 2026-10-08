from . import dreame_numeric,roborock_legacy,ijai_zip,semantic_bundle
from ..catalog import model_by_id

ADAPTERS={
    "dreame_numeric":dreame_numeric,
    "roborock_legacy":roborock_legacy,
    "ijai_zip":ijai_zip,
    "semantic_bundle":semantic_bundle,
}

def get(model_id):
    model=model_by_id(model_id)
    name=model.get("adapter")
    if name not in ADAPTERS:
        raise KeyError(f"No runtime adapter {name!r} for {model_id}")
    return ADAPTERS[name]
