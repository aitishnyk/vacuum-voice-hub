#!/usr/bin/env python3
"""Download/checksum verification, independent of build or publication status."""
import argparse,hashlib,json,tempfile,urllib.request
from pathlib import Path

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('url');parser.add_argument('sha256');parser.add_argument('--output',required=True)
    args=parser.parse_args()
    if not args.url.startswith('https://github.com/aitishnyk/vacuum-voice-hub/releases/download/'):
        raise SystemExit('Expected an actual official release asset URL')
    digest=hashlib.sha256();size=0
    with urllib.request.urlopen(args.url,timeout=60) as response:
        for block in iter(lambda:response.read(1024*1024),b''):
            digest.update(block);size+=len(block)
    result={'schema':'vvh.download-verification.v1','url':args.url,'sha256':digest.hexdigest(),'size':size,'download_verified':digest.hexdigest()==args.sha256.lower(),'desktop_tested':False,'signed':False}
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['download_verified'] else 1)
if __name__=='__main__':main()
