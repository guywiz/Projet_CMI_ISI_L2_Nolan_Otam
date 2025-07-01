from dash import Dash, html, dcc, dash_table, no_update
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import sqlite3
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
import dash

db = sqlite3.connect(
    "Emploi.db", check_same_thread=False)

df = pd.read_sql_query("SELECT familles_metier.famille_metier, recrutements.met, recrutements.smet, recrutements.xmet FROM familles_metier INNER JOIN metiers ON familles_metier.code_famille_BMO = metiers.code_famille_BMO INNER JOIN recrutements ON metiers.code_metier_BMO = recrutements.code_metier_BMO", db)

# Conversion des données des colonnes smet et xmet en int
df['smet'] = pd.to_numeric(df['smet'], errors='coerce')
df['xmet'] = pd.to_numeric(df['xmet'], errors='coerce')

# Calcul des totaux de met, smet et xmet par région
df = df.groupby(['famille_metier'], as_index=False).agg(
    {"met": "sum", "xmet": "sum", "smet": "sum"})

# Ajout d'une somme avec le total met+smet+xmet pour chaque région
df['somme'] = df['smet'] + df['xmet'] + df['met']


fig = go.Figure(go.Bar(x=df['famille_metier'], y=df['met'], name='met'))
fig.add_trace(go.Bar(x=df['famille_metier'], y=df['smet'], name='smet'))
fig.add_trace(go.Bar(x=df['famille_metier'], y=df['xmet'], name='xmet'))

fig.update_layout(barmode='stack', xaxis={
                  'categoryorder': 'category ascending'})

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = Dash(__name__, external_stylesheets=external_stylesheets)


@app.callback(
    Output("bar-chart", "figure"),
    Input('bar-chart', 'clickData'),
)
def barchart_callback(clickData):
    status = None

    if not clickData:
        return no_update
    else:
        status = clickData["points"][0]["label"]
        df2 = pd.read_sql_query("SELECT met, smet, xmet, nom_metier, familles_metier.famille_metier FROM metiers INNER JOIN recrutements ON recrutements.code_metier_BMO = metiers.code_metier_BMO INNER JOIN familles_metier ON familles_metier.code_famille_BMO =  metiers.code_famille_BMO ", db)
        df_gb2 = df2.groupby(
            ["famille_metier", "nom_metier"], as_index=False).agg({"smet": "sum", "xmet": "sum", "met": "sum"}).sort_values(["met", "xmet", 'smet'], ascending=False)
        df_gb2 = df_gb2[df_gb2["famille_metier"] == status]
        top_df = df_gb2.head(10)
        autres = {"smet": pd.DataFrame(df_gb2.iloc[10:])['smet'].sum(
        ), "xmet": pd.DataFrame(df_gb2.iloc[10:])['xmet'].sum(
        ), "met": pd.DataFrame(df_gb2.iloc[10:])['met'].sum(
        ), "nom_metier": "Autres", "famille_metier": "Autres"}
        top_df = top_df.append(autres, ignore_index=True)

        fig = go.Figure(
            go.Bar(x=top_df['nom_metier'],
                   y=top_df['met'], name='met'))

        fig.add_trace(go.Bar(x=top_df['nom_metier'],
                      y=top_df['smet'], name='smet'))
        fig.add_trace(go.Bar(x=top_df['nom_metier'],
                      y=top_df['xmet'], name='xmet'))

        fig.update_layout(barmode='stack', xaxis={
            'categoryorder': 'category ascending'})

        return fig


app.layout = html.Div(children=[dcc.Graph(id='bar-chart',
                                          figure=fig)])

if __name__ == '__main__':
    app.run_server(debug=True)
