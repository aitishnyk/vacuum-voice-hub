from . import dreame_numeric
from ..catalog import model_by_id

ADAPTERS={
    "dreame_numeric":dreame_numeric,
}

def get(model_id):
    model=model_by_id(model_id)
    name=model.get("adapter")
    if name not in ADAPTERS:
        raise KeyError(f"No runtime adapter {name!r} for {model_id}")
    return ADAPTERS[name]
