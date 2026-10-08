from . import dreame_r2209
MODELS={"dreame.vacuum.r2209":dreame_r2209}
def get(model_id):
    if model_id not in MODELS: raise KeyError(f"No runtime adapter for {model_id}")
    return MODELS[model_id]
