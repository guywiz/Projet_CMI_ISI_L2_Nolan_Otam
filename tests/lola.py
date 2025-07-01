import sqlite3
from dash import Dash, dcc, html, Input, Output,ctx,no_update
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

db = sqlite3.connect(
    "Emploi.db", check_same_thread=False)

app = Dash(__name__)

cur=db.cursor()
cur.execute("SELECT nom_metier FROM metiers JOIN familles_metier ON familles_metier.code_famille_BMO=metiers.code_famille_BMO WHERE famille_metier= 'Autres métiers'")
liste_metiers = [i[0] for i in cur.fetchall()]
app.layout = html.Div([
    html.H4("Recrutements en fonction des années"),
    dcc.Graph(id="time-series-chart"),
    html.P("Sélectionner la famille de métiers"),
    dcc.Dropdown(
        id="ticker",
        options=["Autres métiers", "Fonctions liées à la vente, au tourisme et aux services", "Autres techniciens et employés", "Fonctions sociales et médico-sociales", 
        "Ouvriers de la construction et du bâtiment","Ouvriers des secteurs de l'industrie",
        "Fonctions d'encadrement", "Fonctions administratives"],
        value="Autres métiers",
        clearable=False,
    ),
    html.P("Sélectionner le métier"),
    dcc.Dropdown(
        id="choix_met",
        options=liste_metiers,
    ),
])


@app.callback(
    Output("time-series-chart", "figure"),
    Output("choix_met", 'options' ),
    Output("choix_met","value"),
    Input("ticker", "value"),
    Input("choix_met", "value"))
def display_time_series(ticker, choix_met):
    ch_value = None if ctx.triggered_id =="ticker" else no_update
    if ctx.triggered_id =="ticker": 
        concat = f"""familles_metier.famille_metier = "{ticker}" """
    else: 
        concat = f"""metiers.nom_metier = "{choix_met}" """
    df = pd.read_sql_query(f"""SELECT met, famille_metier, annee FROM recrutements INNER JOIN metiers ON recrutements.code_metier_BMO = metiers.code_metier_BMO INNER JOIN familles_metier ON metiers.code_famille_BMO = familles_metier.code_famille_BMO WHERE """+concat, db)
    df_gb = df.groupby("annee", as_index=False).agg({'met':'sum'})
    fig = px.line(df_gb, x="annee", y="met")

    cur.execute(f"""SELECT nom_metier FROM metiers JOIN familles_metier ON familles_metier.code_famille_BMO=metiers.code_famille_BMO WHERE famille_metier= "{ticker}" """)
    liste_metiers = [i[0] for i in cur.fetchall()]
    return fig,liste_metiers,ch_value


app.run_server(debug=True)