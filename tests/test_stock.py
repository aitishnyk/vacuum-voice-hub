import json
from vacuum_voice_hub.stock import list_stock

def test_stock_manifest_parser(tmp_path):
    p=tmp_path/'soundpackage.json'
    p.write_text(json.dumps({'voices':[{'lang':'RU','url':'https://example.invalid/ru.tar.gz','md5':'a'*32,'size':12345}]}))
    r=list_stock('dreame.vacuum.r2209',p.as_uri())
    assert r['items'][0]['id']=='RU'
    assert r['items'][0]['size']==12345
