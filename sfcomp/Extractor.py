# digunakan untuk inisial extraction
import re
import copy 
import random
from .Utils import *

kw_gejala = buka_txt("sfcomp/data/kw_gejala.txt")
kw_obat_2 = buka_txt("sfcomp/data/kw_obat_2.txt")
kw_obat = buka_txt("sfcomp/data/kw_obat.txt")

# convert list kw_gejala to dict
gejala_dict = {}
for i, kw in enumerate(kw_gejala):
    gejala_dict[kw] = i

def extractor(s, med_rec):
    exist = []
    unexist = []
    id = med_rec[0]
    dialog_status = med_rec[1]
    if med_rec[2]!=None:
        exist = med_rec[2]

    # dewasa-anak
    if bool(re.search("\s*de?wa?sa?", s, re.IGNORECASE)):
        exist.append("usia_dewasa")
    elif bool(re.search("\s*(ana?k(\s*2|(-|\s*)\s*ana?k))", s, re.IGNORECASE)):
        exist.append("usia_anak")
    
    # demam
    if bool(re.search("demam", s)):
        exist.append("demam")
    
    # batuk pilek
    if bool(re.search("batuk", s)) and bool(re.search("pilek", s)):
        exist.append("batuk_pilek")  
    elif bool(re.search("batuk", s)):
        exist.append("batuk")
        unexist.append("pilek")  
    elif bool(re.search("pilek", s)):
        exist.append("pilek")
        unexist.append("batuk")

    #diare 
    if bool(re.search("\s*di?a?re",s, re.IGNORECASE)) :
        exist.append("diare")
        cari_ket_diare(s, exist, unexist)

    return [id, dialog_status, list(set(exist)), list(set(unexist))]


# Function2 keterangan gejala 
# def ket_diare(message, exist, unexist) :
#     print(print)

# Function2 mencari keterangan gejala 
def cari_ket_diare (message, exist, unexist) : 
    pattern = ["\s*(ta?nda?)?\s*((ke)?ga?wa?td?a?r?u?r?a?(ta?n)?)?\s*ABCD","\s*(((sa?ki?t)|(nye?ri))\s*pe?ru?t\s*((pa?ra?h)|(he?ba?t)|(se?ka?li?)|(kro?ni?s)|(ba?n?ge?t)))|((pe?ru?t)\s*((sa?ki?t)|(nye?ri))\s*((pa?ra?h)|(he?ba?t)|(se?ka?li?)|(kro?ni?s)|(ba?n?ge?t)))","\s*((obat)\s*(pemicu))|(dru?g\s*indu?ce?d\s*diarh?e?a)|(((obat)|(pil)|(kapsul)(tablet))\s*(\S)*)","\s*(((ti?nja?)|(fe?se?s)|(be?ra?k)|(bab))\s*((\w)*)?\s*(be?r)?da?ra?h)|(((\w)*)?\s*((\w)*)?\s*(be?r)?da?ra?h\s*((\w)*)?\s*((ti?nja?)|(fe?se?s)|(be?ra?k)|(bab)))|(((ti?nja?)|(fe?se?s)|(be?ra?k)|(bab))\s*(((\S)*)?\s*)*cu?ci?a?n\s*be?ra?s)|((((\S)*)?\s*)*cu?ci?a?n\s*be?ra?s)","\s*((\S|\s)*)+(de?ma?m|me?ri?a?ng|ge?ra?h|pa?na?s|palak)","\s*((\S|\s)*)+(mual|muntah)","\s*(((\S|\s)*)+(dahaga|haus)\s*(se?kali|ba?nge?t|pa?ra?h))|(urine?((\w|\s)*)?ge?la?p)|(ge?la?p\s*((\w)*)?\s*urine?((\w)*)?)|(ku?li?t((\w|\s)*)?(ke?ri?ng|ga?ri?ng))"]

    ket_gejala = ["darurat ABCD","diare > 14 hari","nyeri perut hebat","ada drug induced diarhea","tinja berdarah/spt cucian beras","demam","mual muntah","dehidrasi"]

    i = 0
    while (i <= len(pattern) -1 ) : 
        if(bool(re.search(pattern[i],message,re.IGNORECASE))) : 
            exist.append(ket_gejala[i])
        else : 
            unexist.append(ket_gejala[i])
        
        i += 1

    



#Apakah ada tanda kegawatdaruratan ABCD?
# Apakah diare berlangsung >14 hari?
# Apakah ada nyeri perut hebat?
# Apakah ada pemicu obat (drug induced diarhea)
# Apakah tinja ada darah atau seperti air cucian beras?
# Apakah ada demam?
