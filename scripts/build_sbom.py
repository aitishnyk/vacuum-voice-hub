#!/usr/bin/env python3
"""Record installed build environment versions and copy available distribution notices."""
import argparse,importlib.metadata,json,re
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--notices',required=True);args=p.parse_args()
 notices=Path(args.notices)/'Python';notices.mkdir(parents=True,exist_ok=True)
 components=[]
 for dist in sorted(importlib.metadata.distributions(),key=lambda d:d.metadata['Name'].lower()):
  name=dist.metadata['Name'];license_names=[]
  for file in dist.files or []:
   if '.dist-info/' in str(file) and re.search(r'(LICENSE|COPYING|NOTICE)',Path(file).name,re.I):
    source=dist.locate_file(file)
    if source.is_file():
     safe=re.sub('[^A-Za-z0-9._-]','_',name+'-'+str(file).split('.dist-info/')[-1])
     (notices/safe).write_bytes(source.read_bytes());license_names.append('Python/'+safe)
  components.append({'name':name,'version':dist.version,'declared_license':dist.metadata.get('License-Expression') or dist.metadata.get('License') or 'See distribution notices','notices':license_names})
 Path(args.output).write_text(json.dumps({'schema':'vvh.build-environment-sbom.v1','scope':'Installed build environment; includes build-only tools, not a claim that every distribution is shipped','components':components},indent=2)+'\n')
if __name__=='__main__':main()
