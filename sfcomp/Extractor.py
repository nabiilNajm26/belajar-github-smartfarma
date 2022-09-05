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

    # dewasa-anak-bayi
    if bool(re.search("\s*de?wa?sa?", s, re.IGNORECASE)):
        exist.append("usia_dewasa")
    elif bool(re.search("\s*(ana?k(\s*2|(-|\s*)\s*ana?k))", s, re.IGNORECASE)):
        exist.append("usia_anak")
    elif bool(re.search("\s*(bayi)", s, re.IGNORECASE)):
        exist.append("usia_bayi")
    
    # demam
    if bool(re.search("\s*(demam)|(panas)|(h?ang(a|e)t)", s, re.IGNORECASE)):
        exist.append("demam")
        if bool(re.search("\s*(bayi)", s, re.IGNORECASE)):
            cari_ket_demam(s, exist, unexist)
    
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
    pattern = ["\s*(ta?nda?)?\s*((ke)?ga?wa?td?a?r?u?r?a?(ta?n)?)?\s*ABCD","\s*((d(a|i)(i|a)re)\s*(((1[5-9])|([2-9][0-9]))\s*ha?ri?))|((d(a|i)(i|a)re)\s*(le?bi?h)\s*(da?ri?)?\s*14\s*ha?ri?)|((d(a|i)(i|a)re)\s*14\s*(ha?ri?)\s*(le?bi?h))","((pe?ru?t)\s*((sa?ki?t)|(nye?ri))\s*((pa?ra?h)|(he?ba?t)|(se?ka?li?)|(kro?ni?s)|(ba?n?ge?t)))","\s*((obat)\s*(pemicu))|(dru?g\s*indu?ce?d\s*diarh?e?a)|(((obat)|(pil)|(kapsul)(tablet)))","\s*(((ti?nja?)|(fe?se?s)|(be?ra?k)|(bab))\s*((\w))?\s(be?r)?da?ra?h)|(((\w))?\s(be?r)?da?ra?h\s*((\w))?\s((ti?nja?)|(fe?se?s)|(be?ra?k)|(bab)))|(((ti?nja?)|(fe?se?s)|(be?ra?k)|(bab))\s*cu?ci?a?n\s*be?ra?s)|(cu?ci?a?n\s*be?ra?s)","\s*(de?ma?m|me?ri?a?ng|ge?ra?h|pa?na?s|palak)","\s*(mual|muntah)","\s*((dahaga|haus)\s*(se?kali|ba?nge?t|pa?ra?h))|(dehidra?si?)|(urine?\s*?ge?la?p)|(ge?la?p\s*?\s*urine?)|(ku?li?t\s*(ke?ri?ng|ga?ri?ng))"]

    ket_gejala = ["darurat ABCD","diare > 14 hari","nyeri perut hebat","ada drug induced diarhea","tinja berdarah/spt cucian beras","demam","mual muntah","dehidrasi"]

    i = 0
    while (i <= len(pattern) -1 ) : 
        if(bool(re.search(pattern[i],message,re.IGNORECASE))) : 
            exist.append(ket_gejala[i])
            counter.append(i)
        else : 
            unexist.append(ket_gejala[i])
            
        # counter = i
        i += 1

def cari_ket_demam (message, exist, unexist):
    pattern2 = ["\s*(in(f|v)eksi)","\s*(lesi|lenting(an)?)","\s*((obat pemicu( demam|pa?na?s|h?ang(a|e)t)?)|(drug induced fever))",
    "\s*((pen|t)urun((an)?)|(turun naik)|(naik turun))","\s*((h?abis|baru )?(di ?)?(imunisasi))","\s*((gigi)( *baru? mau|akan tumbuh)?)",
    "disertai bersin, cairan bening dri hidung, atau batuk","ada diare","ruam", "ruam di (seluruh tubuh|area wajah)",
    "\s*(b(i|e)nt(i|o)l)|(sariawan)|((tidak|e?n?g?ga?k?) ?)m(au|o) (makan|menyusui)","\s*((ter)?bangun)*malam|(me)?nangis|((me)?narik)*telinga",
    "\s*(gelisah|muntah|cairan)|(((tidak|e?n?g?ga?k?) )?nafsu( *hilang)?)|(cairan (telinga|kuping))","\s*((pura*(pura)?)|(binti(k|l)*merah)|(dengue))"]

    ket_gejala2 = ["infeksi","lesi lentingan","obat pemicu demam rutin sebulan","terjadi penurunan panas","baru diimunisasi","gigi mau tumbuh",
    "disertai bersin, cairan bening dri hidung, atau batuk","ada diare","ruam", "ruam di seluruh tubuh/area wajah",
    "bintil/sariawan/tidak mau makan menyusui","terbangun di malam, menangis, menarik telinga",
    "tanda gelisah, muntah, nafsu makan hilang, keluar cairan telinga","purapura/bintik merah dengue"]

    length = len(pattern2)
    j = 0
    while (j <= len(pattern2) -1 ) : 
        if(bool(re.search(pattern2[j],message,re.IGNORECASE))) : 
            exist.append(ket_gejala2[j])
            counter.append(j)
        else : 
            unexist.append(ket_gejala2[j])
            
        # counter = j
        j += 1

    



#Apakah ada tanda kegawatdaruratan ABCD?
# Apakah diare berlangsung >14 hari?
# Apakah ada nyeri perut hebat?
# Apakah ada pemicu obat (drug induced diarhea)
# Apakah tinja ada darah atau seperti air cucian beras?
# Apakah ada demam?
