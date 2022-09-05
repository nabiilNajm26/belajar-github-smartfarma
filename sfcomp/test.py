import random
import json
import re
import copy     

def buka_txt(nama):
    with open(nama,"r") as f:
        ret = f.readlines()
        ret = [x.rstrip() for x in ret]
    return ret

def buka_json(nama):
    with open(nama) as json_file:
        data = json.load(json_file)
    return data

kw_gejala = buka_txt("kw_gejala.txt")
kw_obat_2 = buka_txt("kw_obat_2.txt")
kw_obat = buka_txt("kw_obat.txt")
db_batuk = buka_json("db_batuk.json")

gejala = {}
gejala_aktif = []
gejala_tidak = []
random.seed(8)

ys = []
for g in kw_gejala:
    y = random.random() 
    ys.append(y)
    if y<0.05:
        gejala[g] = 1
    elif y<0.1:
        gejala[g] = -1
    else:
        gejala[g] = 0

print(ys)

print("gejala:")
for k in gejala.keys():
    if gejala[k]==1:
        gejala_aktif.append(k)
    elif gejala[k]==-1:
        gejala_tidak.append(k)
print(gejala_aktif)
print(gejala_tidak)

# # inference
for q in db_batuk["dewasa"]["0"]:
    now = copy.deepcopy(q)
    while True:
        # print(now, ":")
        flag = 0
        flag_tidak = 0
        gejala_now = db_batuk["dewasa"][now]
        keyword_now = gejala_now["keywords"]

        for k in keyword_now:
            if k in gejala_aktif:
                flag = 1
                break
            elif k in gejala_tidak:
                flag_tidak += 1
        
        if flag:
            if "ya" in gejala_now:
                msg = gejala_now["ya"]
                if re.search(r"\[(\d+)\]", msg)==None:
                    print(msg)
                if "obat_ya" in gejala_now:
                    rec_obat = gejala_now["obat_ya"]
                    print(rec_obat)
                if re.search(r"\[(\d+)\]", msg):
                    next = re.search(r"\[(\d+)\]", msg).group(1)
                else:
                    break
        elif flag_tidak==len(keyword_now):
            if "tidak" in gejala_now:
                msg = gejala_now["tidak"]
                if re.search(r"\[(\d+)\]", msg)==None:
                    print(msg)
                if "obat_tidak" in gejala_now:
                    rec_obat = gejala_now["obat_tidak"]
                    print(rec_obat)
                if re.search(r"\[(\d+)\]", msg):
                    next = re.search(r"\[(\d+)\]", msg).group(1)
                else:
                    break
        else:
            print(now, gejala_now["pertanyaan"],"(y/t)")
            inp = input()
            if inp.lower()[0]=="y":
                gejala_aktif+=gejala_now["keywords"]
            else:
                gejala_tidak+=gejala_now["keywords"]

            next = copy.deepcopy(now) # recheck

        
        now = copy.deepcopy(next)


