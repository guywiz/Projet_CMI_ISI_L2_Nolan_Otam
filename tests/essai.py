import sqlite3
import pandas as pd 
import plotly.graph_objects as go
from dash import Dash, html, dcc, dash_table, no_update
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

db = sqlite3.connect("/home/marie/code/code/projet_programmation_CMI/projet/projet-cmi-isi-l2/Emploi.db", check_same_thread=False)

# Légui mane louma beug représenter ? 
# Dama beug sou choisiré région si drop-down bi (je sais je sais sama yone nekoussi but still)
# ma affichel ko horintal bar chart bou am pour chaque famille de métiers proportions xmet, met ak smet  
# avec un nbre de projets de recrutements jugés difficiles  supérieur à la moyenne 
# Pour lolou louma soxla dans mon dataframe ? familles de métiers yi, régions yi, nbre de projets de recrutements jugés difficiles yi

liste_regions = ['Auvergne-Rhône-Alpes', 'Hauts-De-France', "Provence-Alpes-Côte D'Azur", 'Grand Est', 'Occitanie', 'Normandie', 
                 'Nouvelle-Aquitaine', 'Centre-Val-De-Loire', 'Bourgonne-Franche-Comté', 'Bretagne', 'Corse', 'Pays-De-La-Loire', 
                 'Île-De-France', 'Guadeloupe', 'Martinique', 'Guyane', 'La Réunion', 'Mayotte']

for x in liste_regions:
    my_query = f'''SELECT familles_metier.famille_metier, recrutements.met, recrutements.smet,recrutements.xmet, geo.nom_reg
                        FROM familles_metier 
                        INNER JOIN metiers ON familles_metier.code_famille_BMO = metiers.code_famille_BMO 
                        INNER JOIN recrutements ON metiers.code_metier_BMO = recrutements.code_metier_BMO 
                        INNER JOIN geo ON recrutements.code_bassin = geo.code_bassin WHERE geo.nom_reg = "{x}"
                    '''

    df = pd.read_sql_query(my_query, con = db)

    # Conversion des données des colonnes smet et xmet en int
    df['smet'] = pd.to_numeric(df['smet'], errors = 'coerce')
    df['xmet'] = pd.to_numeric(df['xmet'], errors = 'coerce')
    df['met'] = pd.to_numeric(df['xmet'], errors = 'coerce')


    #Li diaratouko
    # Filtre booléeen pour ne retenir que les lignes correspondant à une région donnée:
    #df = df[df['nom_reg'] == 'Bretagne'

    #Calcul du total des xmet par famille de métier
    #df = df.agg({'xmet':sum,'smet':sum,'met':sum})  
    df = df.groupby(['famille_metier'], as_index=False).agg({'xmet':sum,'smet':sum,'met':sum})

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df['famille_metier'],
        x=df['xmet'],
        name='xmet',
        orientation='h',
        marker=dict(
            color='rgb(67, 67, 67)',
            line=dict(color='rgba(67, 67, 67, 1.0)', width=3)
        )
    ))
    fig.add_trace(go.Bar(
        y=df['famille_metier'],
        x=df['smet'],
        name='smet',
        orientation='h',
        marker=dict(
            color='rgb(248, 248, 255)',
            line=dict(color='rgba(248, 268, 255, 1.0)', width=3)
        )
    ))

    fig.add_trace(go.Bar(
        y=df['famille_metier'],
        x=df['met'],
        name='met',
        orientation='h',
        marker=dict(
            color='rgba(128, 65, 80, 0.6)',
            line=dict(color='rgba(128, 65, 80, 1.0)', width=3)
        )
    ))


    fig.update_layout(barmode='stack')
    fig.update_layout(title = "{}".format(x))
    fig.show()

  
   
external_stylesheets = [dbc.themes.BOOTSTRAP]
app = Dash(__name__, external_stylesheets=external_stylesheets)


@app.callback(
    Output("donut-pie-chart", "figure"),
    Input('donut-pie-chart', 'clickData'),
)
def donut_pie_chart_callback(clickData):
    status = None

    if not clickData:
        return no_update
    else:
        status = clickData["points"][0]["label"]
        df2 = pd.read_sql_query(
            "SELECT met, nom_metier, familles_metier.famille_metier FROM metiers INNER JOIN recrutements ON recrutements.code_metier_BMO = metiers.code_metier_BMO INNER JOIN familles_metier ON familles_metier.code_famille_BMO =  metiers.code_famille_BMO ", db)
        df_gb2 = df2.groupby(
            ["famille_metier", "nom_metier"], as_index=False).agg({'met': 'sum'}).sort_values('met', ascending=False)
        df_gb2 = df_gb2[df_gb2["famille_metier"] == status]

        top_df = df_gb2.head(10)
        autres = {"met": pd.DataFrame(df_gb2.iloc[10:])['met'].sum(
        ), "nom_metier": "Autres", "famille_metier": "Autres"}
        top_df = top_df.append(autres, ignore_index=True)

        return px.pie(top_df, values='met', names='nom_metier')


app.layout = html.Div(children=[dcc.Graph(id='donut-pie-chart',
                                          figure=fig)])

if __name__ == '__main__':
    app.run_server(debug=True)
    #Calcul des pourcentages
    #pourcentages = (df[['met', 'smet', 'xmet']].T/df[['met', 'smet', 'xmet']].T.sum()).T    

    #fig = go.Figure
    #go.Funnel(
    #        x = df['xmet'], 
    #        y = df['famille_metier'],
    #        name='xmet',
    #        orientation = 'h',
    #))
    #fig.show()

    