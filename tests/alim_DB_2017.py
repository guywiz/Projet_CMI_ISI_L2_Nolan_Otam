# -*- coding: utf-8 -*-
import sqlite3
import csv 
import hashlib

##
## SEULEMENT POUR Emploi_2017.csv
##

def to_db(row,db):
    
    alim_metier(row,db)
    alim_familles_metier(row,db)
    alim_geo(row,db)
    alim_recrutements(row,db)



def alim_metier(row,db):
    code_metier_BMO=row["code métier BMO "]
    nom_metier=row["nom_metier BMO"]
    code_famille_BMO=row["Famille_metier"]
    
 
    try:
        cur = db.cursor()
        cur.execute("INSERT INTO metiers('code_metier_BMO','nom_metier','code_famille_BMO') VALUES (?,?,?)",(code_metier_BMO,nom_metier,code_famille_BMO))
    except sqlite3.IntegrityError:
        pass
    except Exception as e:
        print("AUTRE ERREUR : ",e)



def alim_familles_metier(row,db):
    code_famille_BMO=row["Famille_metier"]
    nom_famille_BMO=row["Libellé de famille de métier"]
    
    try:
        cur = db.cursor()
        cur.execute("INSERT INTO familles_metier('code_famille_BMO','famille_metier') VALUES (?,?)",(code_famille_BMO,nom_famille_BMO))
    
    except sqlite3.IntegrityError:
        pass
    except Exception as e:
        print("AUTRE ERREUR : ",e)
        
       

def alim_geo(row,db):
    code_bassin=row["BE17"]
    nom_bassin=row["NOMBE17"]
    dept = row["Dept"]
    nom_dept = row["NomDept"]
    reg = row ["REG"]
    nom_reg = row ["NOM_REG"]
    

    try:
        cur = db.cursor()
        cur.execute("INSERT INTO geo('code_bassin','nom_bassin','dept','nom_dept','reg','nom_reg') VALUES (?,?,?,?,?,?)",(code_bassin,nom_bassin,dept,nom_dept,reg,nom_reg))
    
    except sqlite3.IntegrityError:
        pass
    except Exception as e:
        print("AUTRE ERREUR : ",e)
        
            
   
def alim_recrutements(row,db):
    met=row["met"]
    xmet = row["xmet"]
    smet = row["smet"]
    code_metier_BMO = row ["code métier BMO "]
    code_bassin = row ["BE17"]
    annee = row["annee"]

    try:
        cur = db.cursor()
        cur.execute("INSERT INTO recrutements('met','xmet','smet','code_metier_BMO','code_bassin','annee') VALUES (?,?,?,?,?,?)",(met,xmet,smet,code_metier_BMO,code_bassin,annee))
    
    except sqlite3.IntegrityError:
        pass
    except Exception as e:
        print("AUTRE ERREUR : ",e)
        
            
   
             
        
db = sqlite3.connect("Emploi.db")

with open('data/Emplois_2017.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            to_db(row,db)
        
db.commit()
db.close()

