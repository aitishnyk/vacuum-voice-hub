import hashlib,json,os,time,zipfile
from importlib import metadata
from pathlib import Path
from tempfile import TemporaryDirectory
from . import __version__
from .sitegen import build_site

RELEASE_SCHEMA="vvh.release-manifest.v1"
FEED_SCHEMA="vvh.update-feed.v1"

def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def _epoch(value=None):
    raw=value if value is not None else os.environ.get("SOURCE_DATE_EPOCH","0")
    try:return max(0,int(raw))
    except Exception:raise ValueError("SOURCE_DATE_EPOCH must be an integer")

def _iso(epoch):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(epoch))

def _zip_datetime(epoch):
    epoch=max(epoch,315532800)
    t=time.gmtime(epoch)
    sec=t.tm_sec-(t.tm_sec%2)
    return (t.tm_year,t.tm_mon,t.tm_mday,t.tm_hour,t.tm_min,sec)

def _write_json(path,obj):
    Path(path).write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")

def _direct_requirements():
    try:reqs=metadata.requires("vacuum-voice-hub") or []
    except metadata.PackageNotFoundError:reqs=[]
    return sorted(r for r in reqs if "extra ==" not in r)

def _sbom(epoch):
    return {
        "spdxVersion":"SPDX-2.3",
        "dataLicense":"CC0-1.0",
        "SPDXID":"SPDXRef-DOCUMENT",
        "name":f"Vacuum Voice Hub {__version__}",
        "documentNamespace":f"https://github.com/aitishnyk/vacuum-voice-hub/spdx/{__version__}",
        "creationInfo":{
            "created":_iso(epoch),
            "creators":["Tool: Vacuum Voice Hub release builder"],
        },
        "packages":[{
            "name":"vacuum-voice-hub",
            "SPDXID":"SPDXRef-Package-VVH",
            "versionInfo":__version__,
            "downloadLocation":"NOASSERTION",
            "filesAnalyzed":False,
            "licenseConcluded":"MIT",
            "licenseDeclared":"MIT",
            "externalRefs":[],
            "comment":"Direct runtime requirements: "+"; ".join(_direct_requirements()),
        }],
    }

def _make_public_zip(site_dir,out,epoch):
    dt=_zip_datetime(epoch)
    names=["index.html","catalog.json","models.json","manifest.json"]
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as zf:
        for name in names:
            data=(Path(site_dir)/name).read_bytes()
            info=zipfile.ZipInfo("public/"+name,date_time=dt)
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o100644<<16)
            info.create_system=3
            zf.writestr(info,data)

def build_release(output,source_date_epoch=None):
    out=Path(output).expanduser().resolve()
    out.mkdir(parents=True,exist_ok=True)
    epoch=_epoch(source_date_epoch)
    with TemporaryDirectory(prefix="vvh-release-") as td:
        site=Path(td)/"public"
        site_meta=build_site(site)
        bundle_name=f"VacuumVoiceHub-public-{__version__}.zip"
        bundle=out/bundle_name
        _make_public_zip(site,bundle,epoch)

    sbom_path=out/"sbom.spdx.json"
    _write_json(sbom_path,_sbom(epoch))

    artifact_meta={
        bundle.name:{
            "type":"public-catalog-bundle",
            "sha256":_sha(bundle),
            "size":bundle.stat().st_size,
        },
        sbom_path.name:{
            "type":"spdx-sbom",
            "sha256":_sha(sbom_path),
            "size":sbom_path.stat().st_size,
        },
    }
    manifest={
        "schema":RELEASE_SCHEMA,
        "version":__version__,
        "channel":"stable",
        "source_date_epoch":epoch,
        "artifacts":artifact_meta,
        "contracts":[
            "vvh.semantic.v1",
            "vvh.voicepack.v1",
            "vvh.compat-report.v1",
            "vvh.transport-evidence.v1",
            "vvh.archive-inventory.v1",
            "vvh.research-assessment.v1",
            "vvh.script-pack.v1",
            "vvh.wav-audio-qa.v1",
            "vvh.workspace-audio-qa.v1",
            "vvh.creator-preflight.v1",
            "vvh.creator-batch.v1",
            "vvh.audio-source-qa.v1",
            "vvh.gain-preview.v1",
            "vvh.master-preview.v1",
            "vvh.master-batch.v1",
            "vvh.software-stable-audit.v1",
            "vvh.language-audio-coverage.v1",
            "vvh.production-review.v1",
            "vvh.returned-review.v1",
            "vvh.review-history.v1",
            "vvh.hardware-acceptance.v1",
            "vvh.reviewer-attestation.v1",
            "vvh.review-audio-acceptance.v1",
            "vvh.signed-pack-manifest.v1",
            "vvh.firmware-evidence-bundle.v1",
            "vvh.translation-overlay.v1",
            "vvh.language-review.v1",
            "vvh.audio-ab-review.v1",
            "vvh.pronunciation-lexicon.v1",
            "vvh.firmware-matrix.v1",
            "vvh.community-inbox.v1",
            "vvh.adapter-descriptor.v1",
            "vvh.adapter-interchange.v1",
            "vvh.local-voice-library.v1",
            "vvh.creator-recovery.v1",
            "vvh.universal-studio.v1",
            "vvh.universal-studio-capabilities.v1",
            "vvh.public-catalog.v1",
            RELEASE_SCHEMA,
            FEED_SCHEMA,
        ],
        "desktop_builds":{
            "workflow":".github/workflows/desktop.yml",
            "artifact_names":["VacuumVoiceHub-macOS","VacuumVoiceHub-Windows","VacuumVoiceHub-Linux"],
            "hashes_in_this_manifest":False,
        },
        "signature":{
            "scheme":"ed25519",
            "status":"unsigned",
            "key_id":None,
            "detached_signature":None,
            "note":"A signature is only populated by a trusted release signing environment. Source builds must not claim signing.",
        },
    }
    manifest_path=out/"release-manifest.json"
    _write_json(manifest_path,manifest)

    feed={
        "schema":FEED_SCHEMA,
        "channel":"stable",
        "current_version":__version__,
        "minimum_python":"3.10",
        "release_manifest":{
            "name":manifest_path.name,
            "sha256":_sha(manifest_path),
            "size":manifest_path.stat().st_size,
        },
        "public_bundle":{
            "name":bundle.name,
            "sha256":artifact_meta[bundle.name]["sha256"],
            "size":artifact_meta[bundle.name]["size"],
        },
    }
    feed_path=out/"update-feed.json"
    _write_json(feed_path,feed)

    checksum_files=[bundle,sbom_path,manifest_path,feed_path]
    sums="".join(f"{_sha(p)}  {p.name}\n" for p in sorted(checksum_files,key=lambda p:p.name))
    sums_path=out/"SHA256SUMS"
    sums_path.write_text(sums,encoding="utf-8")

    return {
        "output":str(out),
        "version":__version__,
        "source_date_epoch":epoch,
        "files":[p.name for p in sorted([*checksum_files,sums_path],key=lambda p:p.name)],
        "public_site":site_meta,
        "verified":verify_release(out)["ok"],
    }

def verify_release(path):
    root=Path(path).expanduser().resolve()
    errors=[]
    required=["release-manifest.json","update-feed.json","sbom.spdx.json","SHA256SUMS"]
    for name in required:
        if not (root/name).is_file():errors.append(f"missing file: {name}")
    if errors:return {"ok":False,"errors":errors}
    manifest=json.loads((root/"release-manifest.json").read_text(encoding="utf-8"))
    feed=json.loads((root/"update-feed.json").read_text(encoding="utf-8"))
    if manifest.get("schema")!=RELEASE_SCHEMA:errors.append("release manifest schema mismatch")
    if feed.get("schema")!=FEED_SCHEMA:errors.append("update feed schema mismatch")
    for name,meta in manifest.get("artifacts",{}).items():
        p=root/name
        if not p.is_file():errors.append(f"missing artifact: {name}");continue
        if p.stat().st_size!=meta.get("size"):errors.append(f"size mismatch: {name}")
        if _sha(p)!=meta.get("sha256"):errors.append(f"sha256 mismatch: {name}")
    rm=feed.get("release_manifest",{})
    manifest_path=root/rm.get("name","")
    if not manifest_path.is_file() or _sha(manifest_path)!=rm.get("sha256"):
        errors.append("update feed release-manifest hash mismatch")
    sums={}
    for line in (root/"SHA256SUMS").read_text(encoding="utf-8").splitlines():
        if "  " in line:
            digest,name=line.split("  ",1);sums[name]=digest
    for name,digest in sums.items():
        p=root/name
        if not p.is_file() or _sha(p)!=digest:errors.append(f"SHA256SUMS mismatch: {name}")
    return {
        "ok":not errors,
        "errors":sorted(set(errors)),
        "version":manifest.get("version"),
        "signature_status":(manifest.get("signature") or {}).get("status"),
    }
