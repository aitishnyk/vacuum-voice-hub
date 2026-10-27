"""Native pywebview launcher with bounded shutdown and optional packaging smoke."""
import json
import sys
import tempfile
import threading
from pathlib import Path
from vacuum_voice_hub.server import make_server


def main():
    smoke = '--smoke-test' in sys.argv
    report_path = None
    if smoke:
        position = sys.argv.index('--smoke-test')
        if len(sys.argv) <= position + 1:
            raise SystemExit('Usage: VacuumVoiceHub --smoke-test /absolute/report.json')
        report_path = Path(sys.argv[position+1]).absolute()
    try:
        import webview
    except Exception as exc:
        raise SystemExit("Desktop dependencies are missing. Install: pip install 'vacuum-voice-hub[desktop]'") from exc
    report = {'schema':'vvh.desktop-smoke.v1','gui_loaded':False,'demo_e2e':False,
              'native_audible_playback_verified':False,'signed':False}
    if smoke:
        import os
        from vacuum_voice_hub.demo import start_demo,process_demo,export_demo
        with tempfile.TemporaryDirectory(prefix='vvh-native-smoke-') as td:
            old=os.environ.get('VVH_DATA_DIR');os.environ['VVH_DATA_DIR']=td
            try:
                started=start_demo();process_demo(started['id'],'01.wav',-6);export_demo(started['id'])
                report['demo_e2e']=True
            finally:
                if old is None:os.environ.pop('VVH_DATA_DIR',None)
                else:os.environ['VVH_DATA_DIR']=old
    server=make_server(0)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    timer=None
    try:
        window=webview.create_window('Vacuum Voice Hub',f'http://127.0.0.1:{server.server_address[1]}/',
                                     width=1280,height=860,min_size=(900,650))
        if smoke:
            def loaded():
                report['gui_loaded']=True
                window.destroy()
            window.events.loaded += loaded
            timer=threading.Timer(30,window.destroy);timer.daemon=True;timer.start()
        webview.start(debug=False)
    finally:
        if timer:timer.cancel()
        server.shutdown();server.server_close();thread.join(timeout=5)
        report['server_closed']=not thread.is_alive()
        if report_path:report_path.write_text(json.dumps(report,indent=2)+'\n')
    if smoke and not (report['gui_loaded'] and report['demo_e2e'] and report['server_closed']):
        raise SystemExit(1)

if __name__=='__main__':main()
