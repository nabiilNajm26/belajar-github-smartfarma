import json    

def buka_txt(nama):
    with open(nama,"r") as f:
        ret = f.readlines()
        ret = [x.rstrip() for x in ret]
    return ret

def buka_json(nama):
    with open(nama) as json_file:
        data = json.load(json_file)
    return data
