#!/usr/bin/env python3
"""Native unsigned desktop build. Run independently on each target architecture."""
import json,platform,subprocess,sys,hashlib,shutil,os,plistlib
from pathlib import Path
from vacuum_voice_hub import __version__
ROOT=Path(__file__).resolve().parents[1]
def main():
    system=platform.system();arch=platform.machine()
    codec=Path(os.environ['VVH_FFMPEG']).resolve(strict=True)
    license_output=subprocess.check_output([str(codec),'-L'],stderr=subprocess.STDOUT,text=True)
    if '--enable-nonfree' in license_output or 'not legally redistributable' in license_output:
        raise SystemExit('Refusing to bundle nonredistributable FFmpeg')
    notices=Path(os.environ['VVH_CODEC_NOTICES']).resolve(strict=True)
    cmd=[sys.executable,'-m','PyInstaller','--noconfirm','--clean','--windowed','--onedir','--name','VacuumVoiceHub','--collect-data','vacuum_voice_hub','--collect-all','miio','--exclude-module','imageio_ffmpeg','--add-binary',str(codec)+os.pathsep+'.','--add-data',str(notices)+os.pathsep+'licenses','--collect-all','webview','--copy-metadata','keyring','--hidden-import','keyring.backends.macOS' if system=='Darwin' else 'keyring.backends.Windows' if system=='Windows' else 'keyring.backends.SecretService']
    if system=='Darwin':cmd+=['--icon',str(ROOT/'vacuum_voice_hub/brand/macos.icns'),'--osx-bundle-identifier','org.vacuumvoicehub.desktop']
    elif system=='Windows':cmd+=['--icon',str(ROOT/'vacuum_voice_hub/brand/windows.ico')]
    cmd += [str(ROOT/'vacuum_voice_hub/desktop.py')]
    subprocess.run(cmd,cwd=ROOT,check=True)
    dest=ROOT/'dist';name=f'VacuumVoiceHub-{__version__}-{system}-{arch}'
    if system=='Darwin':
        info=dest/'VacuumVoiceHub.app'/'Contents'/'Info.plist'
        with info.open('rb') as stream:plist=plistlib.load(stream)
        plist['CFBundleShortVersionString']=__version__;plist['CFBundleVersion']=__version__
        with info.open('wb') as stream:plistlib.dump(plist,stream)
        subprocess.run(['codesign','--force','--deep','--sign','-',str(dest/'VacuumVoiceHub.app')],check=True)
        artifact=dest/(name+'.zip')
        subprocess.run(['ditto','-c','-k','--sequesterRsrc','--keepParent',str(dest/'VacuumVoiceHub.app'),str(artifact)],check=True)
    else:
        artifact=Path(shutil.make_archive(str(dest/name),'zip',dest,'VacuumVoiceHub'))
    meta={'version':__version__,'platform':system,'architecture':arch,'artifact':artifact.name,'size':artifact.stat().st_size,'sha256':hashlib.sha256(artifact.read_bytes()).hexdigest(),'build_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'signing_status':'UNSIGNED','build_status':'BUILD_READY','desktop_test_status':'NOT_TESTED','download_status':'NOT_PUBLISHED','source_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip())}
    (dest/(name+'.json')).write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps(meta,indent=2))
if __name__=='__main__':main()
