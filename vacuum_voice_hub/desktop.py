import threading
from vacuum_voice_hub.server import make_server

def main():
    try:
        import webview
    except Exception as e:
        raise SystemExit("Desktop dependencies are missing. Install: pip install 'vacuum-voice-hub[desktop]'") from e
    server=make_server(0)
    port=server.server_address[1]
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        webview.create_window(
            "Vacuum Voice Hub",
            f"http://127.0.0.1:{port}/",
            width=1280,
            height=860,
            min_size=(900,650),
        )
        webview.start(debug=False)
    finally:
        server.shutdown()
        server.server_close()

if __name__=="__main__":
    main()
