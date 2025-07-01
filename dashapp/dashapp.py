import model.data
import view.GUI
import sqlite3
from dash import Dash, dcc, html, Input, Output, State, ctx, no_update
from dash.exceptions import PreventUpdate

import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Importations

# Constantes

carte_option = [
    {"nom_dropdown": "Région", "nom_geojson": "regions", "nom_title": "région"},
    {
        "nom_dropdown": "Département",
        "nom_geojson": "departements",
        "nom_title": "départements",
    },
    {
        "nom_dropdown": "Bassin d'emploi",
        "nom_geojson": "bassins",
        "nom_title": "bassin d'emploi",
    },
]
carte_cores = {
    "Région": {
        "nom_dropdown": "Région",
        "nom_geojson": "regions",
        "nom_title": "région",
    },
    "Département": {
        "nom_dropdown": "Département",
        "nom_geojson": "departements",
        "nom_title": "départements",
    },
    "Bassin d'emploi": {
        "nom_dropdown": "Bassin d'emploi",
        "nom_geojson": "bassins",
        "nom_title": "bassin d'emploi",
    },
}

possible_plot = [
    {"value": "Piechart", "label": "Répartition des projets de recrutement"},
    {"value": "Histo", "label": "Histogramme des projets de recrutement"},
    {"value": "Line", "label": "Evolution du nombre de projets"},
]
radio_cors = {"met": "", "smet": " saisonniers", "xmet": " difficiles"}

REDS_SCALE = [
    [0.0, "rgb(255,245,240)"],
    [0.125, "rgb(254,224,210)"],
    [0.25, "rgb(252,187,161)"],
    [0.375, "rgb(252,146,114)"],
    [0.5, "rgb(251,106,74)"],
    [0.625, "rgb(239,59,44)"],
    [0.75, "rgb(203,24,29)"],
    [0.875, "rgb(165,15,21)"],
    [1.0, "rgb(103,0,13)"],
]

TEAL_SCALE = [
    [0.0, "rgb(209, 238, 234)"],
    [0.16666666666666666, "rgb(168, 219, 217)"],
    [0.3333333333333333, "rgb(133,196, 201)"],
    [0.5, "rgb(104, 171, 184)"],
    [0.6666666666666666, "rgb(79, 144, 166)"],
    [0.8333333333333334, "rgb(59, 115, 143)"],
    [1.0, "rgb(42, 86, 116)"],
]

YLORBR_SCALE = [
    [0.0, "rgb(255,255,229)"],
    [0.125, "rgb(255,247,188)"],
    [0.25, "rgb(254,227,145)"],
    [0.375, "rgb(254,196,79)"],
    [0.5, "rgb(254,153,41)"],
    [0.625, "rgb(236,112,20)"],
    [0.75, "rgb(204,76,2)"],
    [0.875, "rgb(153,52,4)"],
    [1.0, "rgb(102,37,6)"],
]

color_scale_liste = [REDS_SCALE, TEAL_SCALE, YLORBR_SCALE]

db = sqlite3.connect("../Emploi.db", check_same_thread=False)

choro_init_data = model.data.get_choro_init_data(2018, "reg", "nom_reg", db)
pie_init_data = model.data.get_pie_init_data(
    2018, "famille_metier", "metiers.code_famille_BMO", db
)


def saut_de_ligne(string):
    return string if len(string) < 40 else string[:40] + "<br>" + string[40:]


def change_geojson(carte, annee, fig, radio_button, options=None):
    z, hover, ids, cmin, cmax, colorscale, geojson = model.data.get_choro_data(
        carte, annee, color_scale_liste, carte_cores, db, radio_button
    )
    fig = view.GUI.get_choro(
        fig, z, hover, ids, cmin, cmax, colorscale, geojson, None, carte
    )

    return (
        fig,
        carte,
        None,
        f"Cartographie des projets de recrutement{radio_cors[radio_button]} par {carte_cores[carte]['nom_title']} en {annee}",
        no_update if options is None else options,
    )


def change_year(carte, annee, fig, radio_button):
    if annee == 2017 and carte == "Bassin d'emploi":
        options = [i["nom_dropdown"] for i in carte_option[:-1]]
        return change_geojson("Département", annee, fig, radio_button, options)

    options = [i["nom_dropdown"] for i in carte_option]
    z, hover, ids, cmin, cmax, colorscale, geojson = model.data.get_choro_data(
        carte, annee, color_scale_liste, carte_cores, db, radio_button
    )

    selected_points = model.data.get_updated_locations(carte, ids, fig)

    fig = view.GUI.get_choro(
        fig, z, hover, ids, cmin, cmax, colorscale, geojson, selected_points, carte
    )

    return (
        fig,
        carte,
        None,
        f"Cartographie des projets de recrutement{radio_cors[radio_button]} par {carte_cores[carte]['nom_title']} en {annee}",
        options,
    )


def choro_click(carte, annee, fig, clickData, radio_button):
    if carte == "Département" and annee == 2017:
        fig, carte = view.GUI.resize(
            clickData["points"][0]["location"],
            fig,
            carte,
            model.data.load_geojson(
                f"../data/geojson/{carte_cores[carte]['nom_geojson']}.geojson"
            ),
        )

        return (
            fig,
            "Département",
            None,
            f"Cartographie des projets de recrutement par {carte_cores['Département']['nom_title']} en {annee}",
            no_update,
        )

    if carte == "Bassin d'emploi":
        fig, carte = view.GUI.resize(
            clickData["points"][0]["location"],
            fig,
            carte,
            model.data.load_geojson(
                f"../data/geojson/{carte_cores[carte]['nom_geojson']}.geojson"
            ),
        )

        return (
            fig,
            carte,
            None,
            f"Cartographie des projets de recrutement{radio_cors[radio_button]} par {carte_cores[carte]['nom_title']} en {annee}",
            no_update,
        )

    fig, carte = view.GUI.resize(
        clickData["points"][0]["location"],
        fig,
        carte,
        model.data.load_geojson(
            f"../data/geojson/{carte_cores[carte]['nom_geojson']}.geojson"
        ),
    )
    z, hover, ids, cmin, cmax, colorscale, geojson = model.data.get_choro_data(
        carte, annee, color_scale_liste, carte_cores, db, radio_button
    )
    selected_points = model.data.get_new_locations(clickData, carte, ids, db)
    fig = view.GUI.get_choro(
        fig, z, hover, ids, cmin, cmax, colorscale, geojson, selected_points, carte
    )

    return (
        fig,
        carte,
        None,
        f"Cartographie des projets de recrutement{radio_cors[radio_button]} par {carte_cores[carte]['nom_title']} en {annee}",
        no_update,
    )


def change_plot(plot_choice, choro, carte, annee, radio_button):
    fig = no_update
    met_list = no_update
    time_series_visibility = {"display": "none"}
    selected_points = (
        choro["data"][0]["selectedpoints"]
        if "selectedpoints" in choro["data"][0]
        else None
    )
    if selected_points is not None:
        selected_points = [choro["data"][0]["locations"][i] for i in selected_points]
        selected_points = [i if i[0] != "0" else i[1:] for i in selected_points]

    if plot_choice == "Piechart":
        df = model.data.get_pie_data(
            db, "code_famille_BMO", selected_points, carte, annee, radio_button
        )
        fig = view.GUI.get_pie(
            df[radio_button], df["famille_metier"], annee, radio_cors[radio_button]
        )

    elif plot_choice == "Histo":
        df = model.data.get_chart_data(
            db, "code_famille_BMO", selected_points, carte, annee
        )
        fig = view.GUI.get_chart(df, "famille_metier", annee)

    elif plot_choice == "Line":
        famille_metiers = model.data.get_fam_met_lbl(db)
        df = model.data.get_time_series_data(
            db, famille_metiers[0], None, selected_points, carte
        )
        fig = view.GUI.get_time_series(
            df, "Evolution du nombre de projets de recrutement"
        )
        met_list = model.data.get_met_lbl(db, famille_metiers[0])
        met_list = ["Veuillez choisir une famille de métiers"]
        time_series_visibility = {"display": "block"}

    return fig, None, time_series_visibility, met_list, None


def update_plot(plot_choice, fig, clickData, choro, carte, annee, radio_button, trigger="Other",fam_choice = None, met_choice = None):
    selected_points = (
        choro["data"][0]["selectedpoints"]
        if "selectedpoints" in choro["data"][0]
        else None
    )
    if selected_points is not None:
        selected_points = [choro["data"][0]["locations"][i] for i in selected_points]
        selected_points = [i if i[0] != "0" else i[1:] for i in selected_points]
    if clickData is not None:
        if plot_choice == "Piechart":
            df = model.data.get_clic_pie_data(
                clickData["points"][0]["label"],
                db,
                "nom_metier",
                selected_points,
                carte,
                annee,
                radio_button,
            )
            fig = view.GUI.update_pie(
                fig,
                df[radio_button],
                df["nom_metier"],
                annee,
                df["famille_metier"][0],
                radio_cors[radio_button],
            )

        elif plot_choice == "Histo":
            df = model.data.get_clic_chart_data(
                clickData["points"][0]["customdata"][0],
                db,
                "nom_metier",
                selected_points,
                carte,
                annee,
            )
            fig = view.GUI.update_chart(
                fig,
                df["nom_metier"],
                df["met"],
                df["xmet"],
                df["smet"],
                annee,
                df["famille_metier"][0],
            )

        elif plot_choice == "Line":
            raise PreventUpdate

    else:
        if trigger == "choropleth" and plot_choice == "Line":
            fig = change_met(fam_choice, met_choice, fig, choro, carte)[0]
        else : 
            fig = change_plot(plot_choice, choro, carte, annee, radio_button)[0]

    return fig, no_update, no_update, no_update, no_update



def change_fam_met(fam_choice, met_choice, plot, choro, carte):
    selected_points = (
        choro["data"][0]["selectedpoints"]
        if "selectedpoints" in choro["data"][0]
        else None
    )
    if selected_points is not None:
        selected_points = [choro["data"][0]["locations"][i] for i in selected_points]
        selected_points = [i if i[0] != "0" else i[1:] for i in selected_points]

    df = model.data.get_time_series_data(db, fam_choice, None, selected_points, carte)
    if fam_choice is None:
        title = "Evolution du nombre de projets de recrutement"
    else:
        title = f"Evolution du nombre de projets de recrutement<br>pour la famille de métier '{saut_de_ligne(fam_choice)}'"

    fig = view.GUI.update_time_series(plot, df, title)
    if fam_choice is None:
        return fig, None, no_update, ["Veuillez choisir une famille de métiers"], None

    return fig, None, no_update, model.data.get_met_lbl(db, fam_choice), None


def change_met(fam_choice, met_choice, plot, choro, carte):
    if met_choice == "Veuillez choisir une famille de métiers":
        raise PreventUpdate
    if met_choice is None:
        return change_fam_met(fam_choice, met_choice, plot, choro, carte)
    selected_points = (
        choro["data"][0]["selectedpoints"]
        if "selectedpoints" in choro["data"][0]
        else None
    )
    if selected_points is not None:
        selected_points = [choro["data"][0]["locations"][i] for i in selected_points]
        selected_points = [i if i[0] != "0" else i[1:] for i in selected_points]

    df = model.data.get_time_series_data(
        db, fam_choice, met_choice, selected_points, carte
    )
    fig = view.GUI.update_time_series(
        plot,
        df,
        f"Evolution du nombre de projets de recrutement<br>pour le métier '{saut_de_ligne(met_choice)}'",
    )
    return fig, None, no_update, no_update, no_update




app = Dash(__name__)

app.layout = view.GUI.layout(
    year_range=range(2017, 2023),
    pie_data={"values": pie_init_data["met"], "names": pie_init_data["famille_metier"]},
    carte_option=carte_option,
    fig_data={
        "locations": choro_init_data["reg"],
        "z": choro_init_data["SUM(met)"],
        "text": choro_init_data["nom_reg"],
        "geojson": model.data.load_geojson("../data/geojson/regions.geojson"),
    },
    possible_plot=possible_plot,
    radio_list=[
        {"label": "Projets de recrutements", "value": "met"},
        {"label": "Projets saisonniers", "value": "smet"},
        {"label": "Projets difficiles", "value": "xmet"},
    ],
    liste_famille_metiers=model.data.get_fam_met_lbl(db),
    liste_metiers=[],
)


@app.callback(
    Output("choropleth", "figure"),
    Output("carte-dropdown", "value"),
    Output("choropleth", "clickData"),
    Output("choropleth-title", "children"),
    Output("carte-dropdown", "options"),
    Input("carte-dropdown", "value"),
    Input("year-slider", "value"),
    State("choropleth", "figure"),
    Input("choropleth", "clickData"),
    Input("radio_buttons", "value"),
    prevent_initial_call=True,
)
def display_choropleth(carte, annee, fig, clickData, radio_button):
    triggered_id = ctx.triggered_id

    if triggered_id == "carte-dropdown":
        return change_geojson(carte, annee, fig, radio_button)
    elif triggered_id == "year-slider" or triggered_id == "radio_buttons":
        return change_year(carte, annee, fig, radio_button)
    elif triggered_id == "choropleth":
        return choro_click(carte, annee, fig, clickData, radio_button)


@app.callback(
    Output("plot", "figure"),
    Output("plot", "clickData"),
    Output("time_series_dp", "style"),
    Output("choix_met", "options"),
    Output("choix_met", "value"),
    Input("plot-dropdown", "value"),
    Input("plot", "clickData"),
    State("plot", "figure"),
    Input("choropleth", "figure"),
    State("carte-dropdown", "value"),
    State("year-slider", "value"),
    Input("choropleth", "selectedData"),
    State("radio_buttons", "value"),
    Input("choix_fam_met", "value"),
    Input("choix_met", "value"),
    prevent_initial_call=True,
)
def display_plot(
    plot_choice,
    clickData,
    plot,
    choro,
    carte,
    annee,
    selectedData,
    radio_button,
    fam_choice,
    met_choice,
):
    triggered_id = ctx.triggered_id
    if triggered_id == "plot-dropdown":
        return change_plot(plot_choice, choro, carte, annee, radio_button)
    elif triggered_id == "plot" or triggered_id == "choropleth":
        return update_plot(
            plot_choice,
            plot,
            clickData,
            choro,
            carte,
            annee,
            radio_button,
            triggered_id,fam_choice = fam_choice, met_choice = met_choice
        )
    elif triggered_id == "choix_fam_met":
        return change_fam_met(fam_choice, met_choice, plot, choro, carte)
    elif triggered_id == "choix_met":
        return change_met(fam_choice, met_choice, plot, choro, carte)
    else:
        raise ValueError("Unknown trigger_id in display_plot")

if __name__ == "__main__":
    app.run_server(debug=True)

db.close()
