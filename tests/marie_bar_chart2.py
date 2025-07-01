import sqlite3
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go

db = sqlite3.connect("/home/marie/code/code/projet_programmation_CMI/projet/projet-cmi-isi-l2/Emploi.db", check_same_thread=False)
my_query = '''SELECT familles_metier.famille_metier, recrutements.met, recrutements.smet, recrutements.xmet, geo.reg, geo.nom_reg
                FROM familles_metier 
                INNER JOIN metiers ON familles_metier.code_famille_BMO = metiers.code_famille_BMO 
                INNER JOIN recrutements ON metiers.code_metier_BMO = recrutements.code_metier_BMO 
                INNER JOIN geo ON recrutements.code_bassin = geo.code_bassin 
            '''
df = pd.read_sql_query(my_query, db)

# Conversion des données des colonnes smet et xmet en int
df['smet'] = pd.to_numeric(df['smet'], errors = 'coerce')
df['xmet'] = pd.to_numeric(df['xmet'], errors = 'coerce')

# Calcul des totaux de met, smet et xmet par région
df = df.groupby(['nom_reg'],as_index=False).agg({"met":"sum","xmet":"sum", "smet":"sum"})

# Ajout d'une somme avec le total met+smet+xmet pour chaque région
df['somme'] = df['smet'] + df['xmet'] + df['met']



fig = go.Figure(data=[
    go.Bar(name='met', x= df['nom_reg'], y=df['met']),
    go.Bar(name='smet', x= df['nom_reg'], y=df['smet']),
    go.Bar(name='xmet', x= df['nom_reg'], y=df['xmet'])
])

fig.update_layout(barmode='group')
fig.show()

#fig = go.Figure(go.Bar(x=df['nom_reg'], y=df['met'], name='met'))
#fig.add_trace(go.Bar(x=df['nom_reg'], y=df['smet'], name='smet'))
#fig.add_trace(go.Bar(x=df['nom_reg'], y=df['xmet'], name='xmet'))

#fig.update_layout(barmode='stack', xaxis={'categoryorder':'category ascending'})
#fig.show()
