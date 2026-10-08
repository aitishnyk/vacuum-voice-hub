from vacuum_voice_hub import credentials

class FakeKeyring:
    def __init__(self):self.data={}
    def set_password(self,service,name,value):self.data[(service,name)]=value
    def get_password(self,service,name):return self.data.get((service,name))
    def delete_password(self,service,name):
        if (service,name) not in self.data:raise KeyError(name)
        del self.data[(service,name)]

def test_keyring_roundtrip_without_exposing_token(monkeypatch):
    fake=FakeKeyring()
    monkeypatch.setattr(credentials,"_keyring",lambda:fake)
    token="d"*32
    saved=credentials.save("my-x10",token)
    assert saved=={"name":"my-x10","stored":True}
    assert token not in str(saved)
    assert credentials.status("my-x10")["stored"] is True
    assert credentials.load("my-x10")==token
    assert credentials.delete("my-x10")["deleted"] is True
    assert credentials.status("my-x10")["stored"] is False
