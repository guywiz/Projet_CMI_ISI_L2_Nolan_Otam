import sqlite3
import pandas as pd
import csv
import plotly.express as px 
import plotly.graph_objects as go

#La proportion de projets de recrutement jugés difficiles (xmet) par région (axe horizontal) 
# pour une famille de métiers (choix dans un menu dropdown)
#Je récupère la liste des familles de métiers :
with open ('/home/marie/code/code/projet_programmation_CMI/projet/projet-cmi-isi-l2/data/Emplois_2017.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    liste_familles_metier= []
    for row in reader:
        if row['Lbl_fam_met'] not in liste_familles_metier:
            liste_familles_metier.append(row['Lbl_fam_met'])

#print(liste_familles_metier)

db = sqlite3.connect("/home/marie/code/code/projet_programmation_CMI/projet/projet-cmi-isi-l2/Emploi.db", check_same_thread=False)

# Regroupement par famille de métiers et région if ever 
# df = pd.read_sql_query("SELECT familles_metier.famille_metier, recrutements.met, recrutements.smet, recrutements.xmet, geo.reg FROM familles_metier INNER JOIN metiers ON familles_metier.code_famille_BMO = metiers.code_famille_BMO INNER JOIN recrutements ON metiers.code_metier_BMO = recrutements.code_metier_BMO 
# INNER JOIN geo ON recrutements.code_bassin = geo.code_bassin", con=db)
#print("")
#print("Groups in DataFrame:")
#groups = df.groupby(['famille_metier', 'reg'])
#for group_key, group_value in groups:
    #group = groups.get_group(group_key).agg({"met":"sum","xmet":"sum", "smet":"sum"})
    #print(group)
    #print("")

# SINON :
# Le code qui suit calcule et représente la proportion de xmet par région pour chaque famille de métiers
for x in liste_familles_metier:
    my_query = '''SELECT familles_metier.famille_metier, recrutements.met, recrutements.smet, recrutements.xmet, geo.reg, geo.nom_reg
                FROM familles_metier 
                INNER JOIN metiers ON familles_metier.code_famille_BMO = metiers.code_famille_BMO 
                INNER JOIN recrutements ON metiers.code_metier_BMO = recrutements.code_metier_BMO 
                INNER JOIN geo ON recrutements.code_bassin = geo.code_bassin WHERE familles_metier.famille_metier = "{}"
            '''.format(x)

    df = pd.read_sql_query(my_query, con=db)

    # Conversion des données des colonnes smet et xmet en int
    df['smet'] = pd.to_numeric(df['smet'], errors = 'coerce')
    df['xmet'] = pd.to_numeric(df['xmet'], errors = 'coerce')


    # Calcul des totaux de met, smet et xmet par région
    df = df.groupby(['nom_reg'],as_index=False).agg({"met":"sum","xmet":"sum", "smet":"sum"})
    # Calcul des proportions de met, smet et xmet par région
    #proportions = (df.T/df.T.sum()).T

    #Représentation avec un diagramme circulaire 
    diagramme = px.pie(df, values='xmet', names='nom_reg', title = '''Proportion de projets de recrutement jugés difficiles (xmet) par région 
    pour la famille de métiers "{}" '''.format(x))

    diagramme.show()