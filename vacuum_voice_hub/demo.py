"""Offline, isolated demo sessions; no robot transports or caller-selected paths."""
import hashlib, json, re, secrets, shutil, tempfile, wave
import functools, threading
_LOCK = threading.RLock()
def serialized(function):
    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        with _LOCK:
            return function(*args, **kwargs)
    return wrapped
from importlib.resources import files
from pathlib import Path
from .paths import data_dir
from .creator import new_workspace, assign_audio, build_workspace
from .audio_mastering import master_preview
from .audio_timeline import audio_timeline


def assets():
    return Path(str(files('vacuum_voice_hub') / 'demo_assets'))


def audit_assets():
    root = assets()
    doc = json.loads((root / 'manifest.json').read_text())
    for event in doc['events']:
        name = event['file']
        if Path(name).name != name or not name.endswith('.wav'):
            raise ValueError('invalid demo asset name')
        path = root / name
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != event['sha256']:
            raise ValueError('demo recording integrity failure')
        with wave.open(str(path), 'rb') as clip:
            if (clip.getnchannels(), clip.getsampwidth(), clip.getframerate()) != (1, 2, 16000):
                raise ValueError('demo recordings must be mono PCM16 at 16 kHz')
            if not 4000 <= clip.getnframes() <= 16000 * 30 or len(clip.readframes(clip.getnframes())) != clip.getnframes()*2:
                raise ValueError('invalid demo recording data')
    if len(doc['events']) != 8:
        raise ValueError('demo requires eight recordings')
    return doc


def _base():
    base = data_dir() / 'demo'
    if base.is_symlink():
        raise ValueError('symlinked demo directory refused')
    base.mkdir(exist_ok=True)
    return base


def session_root(identity):
    if not isinstance(identity, str) or not re.fullmatch(r'[a-f0-9]{24}', identity):
        raise ValueError('invalid demo session')
    root = _base() / identity
    if root.is_symlink() or not root.is_dir():
        raise ValueError('demo session missing; start a new demo')
    return root


@serialized
def start_demo():
    doc = audit_assets()
    base = _base()
    identity = secrets.token_hex(12)
    staging = Path(tempfile.mkdtemp(prefix='.prepare-', dir=base))
    try:
        new_workspace(staging, pack_id='vvh-demo-'+identity, name='Orbit · Offline Demo',
                      author='Vacuum Voice Hub contributors', language='en', license_name='CC0-1.0')
        for folder in ('originals','processed','exports'):
            (staging / folder).mkdir()
        for event in doc['events']:
            original = staging / 'originals' / event['file']
            shutil.copyfile(assets() / event['file'], original)
            assign_audio(staging, event['semantic'], original)
        (staging / 'demo.json').write_text(json.dumps(doc))
        staging.rename(base / identity)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return {'id': identity, 'events': doc['events'], 'install_authorized': False}


def demo_file(identity, name):
    root = session_root(identity)
    parts = Path(name).parts
    if len(parts) != 2 or parts[0] not in {'originals','processed','exports'} or parts[1] in {'.','..'}:
        raise ValueError('invalid demo file')
    path = root / name
    if path.parent.is_symlink() or path.is_symlink() or not path.is_file():
        raise ValueError('demo file missing')
    path.resolve().relative_to(root.resolve())
    return path


@serialized
def process_demo(identity, semantic, peak=-3):
    root = session_root(identity)
    doc = json.loads((root / 'demo.json').read_text())
    event = next((e for e in doc['events'] if e['file'] == semantic), None)
    if event is None:
        raise ValueError('unknown demo event')
    source = demo_file(identity, 'originals/' + event['file'])
    if hashlib.sha256(source.read_bytes()).hexdigest() != event['sha256']:
        raise ValueError('demo original changed; start a new demo')
    if (root / 'processed').is_symlink():
        raise ValueError('symlinked processing directory refused')
    output = root / 'processed' / (secrets.token_hex(12)+'.wav')
    master_preview(source, output, target_peak_dbfs=peak)
    assign_audio(root, event['semantic'], output)
    return {'file': 'processed/'+output.name, 'timeline': audio_timeline(output), 'install_authorized': False}


@serialized
def export_demo(identity):
    root = session_root(identity)
    if (root / 'exports').is_symlink():
        raise ValueError('symlinked export directory refused')
    output = root / 'exports' / (secrets.token_hex(12)+'.tar.gz')
    build_workspace(root, 'dreame.vacuum.r2209', output)
    return {'file': 'exports/'+output.name, 'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
            'size': output.stat().st_size, 'model_id': 'dreame.vacuum.r2209',
            'install_authorized': False, 'partial_demo_pack': True}


@serialized
def copy_to_creator(identity):
    from .creator import default_workspace
    root = session_root(identity)
    doc = json.loads((root / 'demo.json').read_text())
    pack_id = 'demo-copy-'+secrets.token_hex(12)
    target = default_workspace(pack_id)
    try:
        new_workspace(target, pack_id=pack_id, name='My Demo Project',
                      author='Vacuum Voice Hub contributors', language='en', license_name='CC0-1.0')
        for event in doc['events']:
            assign_audio(target, event['semantic'], demo_file(identity, 'originals/'+event['file']))
    except Exception:
        if target.exists():
            shutil.rmtree(target)
        raise
    return {'id': pack_id, 'install_authorized': False}
