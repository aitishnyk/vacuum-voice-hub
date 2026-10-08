from . import dreame_canonical_ogg, robovoice_r2567r_mp3, ijai_named_mp3
ADAPTERS={
 "dreame-canonical-ogg":dreame_canonical_ogg.adapt,
 "robovoice-r2567r-mp3":robovoice_r2567r_mp3.adapt,
 "ijai-named-mp3":ijai_named_mp3.adapt,
}
def get(name):
    if name not in ADAPTERS: raise KeyError(f"Unsupported source format: {name}")
    return ADAPTERS[name]
