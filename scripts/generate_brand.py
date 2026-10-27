#!/usr/bin/env python3
"""Reproducible original VVH vector identity and raster derivatives (CairoSVG/Pillow)."""
from pathlib import Path
import cairosvg
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]/'vacuum_voice_hub'/'brand'
ICON='<circle cx="32" cy="32" r="27" fill="#0b1220" stroke="#22d3ee" stroke-width="4"/><path d="M15 32h8l4-12 8 24 5-12h9" fill="none" stroke="#a78bfa" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"/><circle cx="32" cy="12" r="2" fill="#22d3ee"/>'
def svg(width,height,content):return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">{content}</svg>'
def main():
    ROOT.mkdir(exist_ok=True)
    for name in ('master','icon','icon-dark','icon-light'):
        (ROOT/(name+'.svg')).write_text(svg(64,64,ICON))
    for mode,color in [('dark','#f8fafc'),('light','#0b1220')]:
        (ROOT/('wordmark-'+mode+'.svg')).write_text(svg(450,64,ICON+f'<text x="80" y="41" font-family="sans-serif" font-size="30" font-weight="700" fill="{color}">Vacuum Voice Hub</text>'))
    for size in (32,64,128,256,512,1024):
        cairosvg.svg2png(url=str(ROOT/'master.svg'),write_to=str(ROOT/f'icon-{size}.png'),output_width=size,output_height=size)
    im=Image.open(ROOT/'icon-1024.png')
    im.save(ROOT/'windows.ico',sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
    Image.open(ROOT/'icon-32.png').save(ROOT/'favicon.ico')
    im.save(ROOT/'macos.icns',format='ICNS')
    content='<rect width="1200" height="630" fill="#0b1220"/><circle cx="1070" cy="320" r="270" fill="#162235"/><g transform="translate(815 180) scale(4)">'+ICON+'</g><text x="70" y="100" font-family="sans-serif" font-size="28" fill="#a78bfa">VACUUM VOICE HUB</text><text x="70" y="230" font-family="sans-serif" font-weight="700" font-size="64" fill="#f8fafc">Give your robot</text><text x="70" y="310" font-family="sans-serif" font-weight="700" font-size="64" fill="#22d3ee">vacuum a voice.</text><text x="70" y="410" font-family="sans-serif" font-size="25" fill="#b9c8da">Offline voice studio. Model-aware builds.</text><text x="70" y="460" font-family="sans-serif" font-size="25" fill="#b9c8da">Open-source. Yours to customize.</text><text x="70" y="560" font-family="sans-serif" font-size="18" fill="#a78bfa">223 research profiles · Hardware evidence stays explicit</text>'
    (ROOT/'social.svg').write_text(svg(1200,630,content))
    cairosvg.svg2png(url=str(ROOT/'social.svg'),write_to=str(ROOT/'social.png'))
if __name__=='__main__':main()
