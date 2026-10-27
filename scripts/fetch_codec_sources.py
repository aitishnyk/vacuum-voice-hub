#!/usr/bin/env python3
"""Pinned upstream codec sources with hashes, notices and redistributable source bundle."""
import argparse,hashlib,json,shutil,tarfile,urllib.request
from pathlib import Path
SOURCES={
 'ffmpeg-7.1.tar.xz':('https://ffmpeg.org/releases/ffmpeg-7.1.tar.xz','40973d44970dbc83ef302b0609f2e74982be2d85916dd2ee7472d30678a7abe6'),
 'libogg-1.3.5.tar.xz':('https://downloads.xiph.org/releases/ogg/libogg-1.3.5.tar.xz','c4d91be36fc8e54deae7575241e03f4211eb102afb3fc0775fbbc1b740016705'),
 'libvorbis-1.3.7.tar.xz':('https://downloads.xiph.org/releases/vorbis/libvorbis-1.3.7.tar.xz','b33cc4934322bcbf6efcbacf49e3ca01aadbea4114ec9589d1b1e9d20f72954b'),
 'lame-3.100.tar.gz':('https://downloads.sourceforge.net/project/lame/lame/3.100/lame-3.100.tar.gz','ddfe36cab873794038ae2c1210557ad34857a4b6bdc515785d1da9e175b1da1e'),
}
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args()
 root=Path(args.output).resolve();root.mkdir(parents=True,exist_ok=True)
 notices=root/'NOTICES';notices.mkdir(exist_ok=True)
 metadata={}
 for name,(url,digest) in SOURCES.items():
  target=root/name
  if not target.exists():
   with urllib.request.urlopen(url,timeout=60) as response:target.write_bytes(response.read())
  if hashlib.sha256(target.read_bytes()).hexdigest()!=digest:raise SystemExit('Source hash mismatch: '+name)
  metadata[name]={'url':url,'sha256':digest}
  with tarfile.open(target) as archive:
   for item in archive:
    basename=Path(item.name).name
    if item.isfile() and basename in {'COPYING.LGPLv2.1','COPYING.LGPLv3','COPYING','COPYING.LESSER','COPYING.GPLv2','COPYING.GPLv3'} and len(Path(item.name).parts)==2:
     (notices/(name.split('.tar')[0]+'-'+basename)).write_bytes(archive.extractfile(item).read())
 (notices/'SOURCES.json').write_text(json.dumps(metadata,indent=2)+'\n')
 (notices/'README.txt').write_text('Vacuum Voice Hub invokes FFmpeg as a separate executable. This minimal build does not enable GPL or nonfree components. FFmpeg is LGPL-2.1-or-later; LAME is LGPL, libogg/libvorbis are BSD. Full upstream notices are included. Source archives and build recipe accompany the application as VacuumVoiceHub-codec-sources.tar.gz. Rebuild with build_codec.sh and replace the standalone ffmpeg executable to use a modified codec. No warranty. No external speech models or voice packs are bundled.\n')
 recipe=Path(__file__).with_name('build_codec.sh')
 shutil.copyfile(recipe,root/'build_codec.sh')
 with tarfile.open(root/'VacuumVoiceHub-codec-sources.tar.gz','w:gz') as archive:
  for name in SOURCES:archive.add(root/name,arcname=name)
  archive.add(root/'build_codec.sh',arcname='build_codec.sh');archive.add(notices,arcname='NOTICES')
 print(json.dumps({'source_bundle':'VacuumVoiceHub-codec-sources.tar.gz','sources':metadata},indent=2))
if __name__=='__main__':main()
