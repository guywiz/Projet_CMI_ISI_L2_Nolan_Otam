from dash import Dash, html, dcc, dash_table, no_update
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import sqlite3
import plotly.express as px
import pandas as pd

# requetes a la BD
db = sqlite3.connect(
    "Emploi.db", check_same_thread=False)

# option 1

# cur= db.cursor()
# cur.execute("SELECT ...FROM")
# rows=cur.fetchall()

# option 2

df = pd.read_sql_query("SELECT met, famille_metier, metiers.code_famille_BMO FROM recrutements INNER JOIN metiers ON recrutements.code_metier_BMO = metiers.code_metier_BMO INNER JOIN familles_metier ON metiers.code_famille_BMO = familles_metier.code_famille_BMO", db)

df_gb = df.groupby(["famille_metier", "code_famille_BMO"],
                   as_index=False).agg({'met': 'sum'})


fig = px.pie(df_gb, values='met', names='famille_metier')

# https: // community.plotly.com/t/how-to-get-click-event-from -donut-pie-when-the-hole-in -the-middle-is -clicked/63569/3
# maintenant pon va essayer de preciser des informations sur chaque morceau de pie...

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
