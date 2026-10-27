#!/usr/bin/env python3
"""Machine-readable source acceptance, deliberately separate from platform acceptance."""
import hashlib,json,os,tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from vacuum_voice_hub import __version__
from vacuum_voice_hub.demo import audit_assets,start_demo,process_demo,export_demo,demo_file
from vacuum_voice_hub.sitegen import build_site,verify_site
from scripts.v2_release_acceptance import acceptance

def main():
    baseline=acceptance(compatible=True)
    assert baseline['ok'],baseline['errors']
    assert __version__=='2.1.0'
    with tempfile.TemporaryDirectory() as td:
        old=os.environ.get('VVH_DATA_DIR');os.environ['VVH_DATA_DIR']=td
        try:
            doc=audit_assets();session=start_demo()
            source=demo_file(session['id'],'originals/01.wav');before=hashlib.sha256(source.read_bytes()).hexdigest()
            processed=process_demo(session['id'],'01.wav',-6)
            exported=export_demo(session['id'])
            assert before==hashlib.sha256(source.read_bytes()).hexdigest()
            assert exported['sha256']==hashlib.sha256(demo_file(session['id'],exported['file']).read_bytes()).hexdigest()
            site=build_site(Path(td)/'site');assert verify_site(Path(td)/'site')['ok']
            assert site['models']==223 and site['voices']==55
        finally:
            if old is None:os.environ.pop('VVH_DATA_DIR',None)
            else:os.environ['VVH_DATA_DIR']=old
    print(json.dumps({'schema':'vvh.v21-source-acceptance.v1','version':__version__,'status':'SOURCE_TESTED','demo_events':len(doc['events']),'demo_e2e':True,'originals_preserved':True,'site_models':site['models'],'site_voices':site['voices'],'v2_invariants_preserved':True,'desktop_tested':False,'signed':False,'hardware_install_authorized':False},indent=2))
if __name__=='__main__':main()
