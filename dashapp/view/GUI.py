import plotly.express as px
import plotly.graph_objects as go
import math

from shapely.geometry import Polygon
from dash import Dash, dcc, html, Input, Output, State, ctx
import numpy as np


def layout(
    year_range,
    carte_option,
    fig_data,
    pie_data,
    possible_plot,
    radio_list,
    liste_famille_metiers,
    liste_metiers,
):
    return html.Div(
        id="root",
        children=[
            html.Div(
                id="header",
                children=[
                    html.H1(
                        children="Besoins en Main-d'Œuvre : Aperçu interactif des projets de recrutement"
                    )
                ],
            ),
            html.Div(
                id="app-container",
                children=[
                    html.Div(
                        id="left-column",
                        children=[
                            html.Div(
                                id="year-slider-dropdown-container",
                                children=[
                                    get_year_slider(year_range),
                                    get_left_drop_down(carte_option),
                                    get_radio_button(radio_list),
                                ],
                            ),
                            html.Div(
                                id="chropleth-container",
                                children=[
                                    html.P(
                                        id="choropleth-title",
                                        children=f"Cartographie des projets de recrutement par {carte_option[0]['nom_title']} en {year_range[1]}",
                                    ),
                                    create_dash_choropleth(fig_data),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        id="plot-container",
                        children=[
                            html.P(
                                id="dropdown-title", children="Choisir un graphique : "
                            ),
                            get_right_drop_down(possible_plot),
                            html.Div(
                                id="plot-div",
                                children=get_line_dropdowns(
                                    liste_famille_metiers, liste_metiers
                                )
                                + [
                                    html.Div(
                                        id="container",
                                        children=[create_plot(
                                            pie_data, year_range)],
                                    )
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def get_line_dropdowns(liste_famille_metiers, liste_metiers):
    return [
        html.Div(
            id="time_series_dp",
            style={"display": "none"},
            children=[
                html.P("Sélectionner la famille de métiers"),
                dcc.Dropdown(
                    id="choix_fam_met",
                    options=liste_famille_metiers,
                ),
                html.P("Sélectionner le métier"),
                dcc.Dropdown(
                    id="choix_met",
                    options=liste_metiers,
                ),
            ],
        )
    ]


def get_left_drop_down(carte_option):
    return dcc.Dropdown(
        id="carte-dropdown",
        options=[i["nom_dropdown"] for i in carte_option],
        value=carte_option[0]["nom_dropdown"],
        clearable=False,
    )


def get_right_drop_down(possible_plot):
    return dcc.Dropdown(
        id="plot-dropdown",
        options=possible_plot,
        value=possible_plot[0]["value"],
        clearable=False,
    )


def get_radio_button(radio_list):
    return dcc.RadioItems(
        id="radio_buttons",
        options=radio_list,
        value=radio_list[0]["value"],
        labelStyle={
            "display": "inline-flex",
            "align-items": "center",
            "font-size": "18px",
            "margin-right": "10px",
            "line-height": "1",
        },
        inputStyle={"width": "30px", "height": "30px"},
        inputClassName="custom-radio",
    )


def create_plot(pie_data, year_range):
    return dcc.Graph(
        id="plot",
        style={"height": "100%", "width": "100%"},
        figure=px.pie(values=pie_data["values"], names=pie_data["names"])
        .update_layout(
            paper_bgcolor="#1f2630",
            plot_bgcolor="#1f2630",
            font={"color": "#2cfec1"},
            margin={"t": 75, "r": 0, "b": 60, "l": 0},
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.3, xanchor="left", x=0.1
            ),
            title=f"Répartition des projets de recrutement par famille de métiers en {year_range[1]}",
        )
        .update_traces(textinfo="percent", hovertemplate="%{label} <br> %{value}"),
    )


def get_year_slider(year_range):
    return dcc.Slider(
        year_range[0],
        year_range[-1],
        1,
        value=year_range[1],
        id="year-slider",
        marks={i: f"{i}" for i in year_range},
    )

def create_dash_choropleth(fig_data):
    fig = (
        go.Figure(
            go.Choroplethmapbox(
                locations=fig_data["locations"],
                z=fig_data["z"],
                text=fig_data["text"],
                colorscale="reds",
                geojson=fig_data["geojson"],
                marker_opacity=0.8,
                featureidkey="properties.code",
                zmin=0,zmax=374973.10000000003
            )
        )
        .update_layout(
            mapbox_style="carto-darkmatter",
            mapbox_center={"lat": 47.0, "lon": 2},
            mapbox_zoom=4.5,
            autosize=True,
            paper_bgcolor="#1f2630",
            plot_bgcolor="#1f2630",
            font={"color": "#2cfec1"},
            margin={"t": 0, "r": 0, "b": 0, "l": 0},
        )
        .update_traces(colorbar_x=0.91)
    )
    return dcc.Graph(id="choropleth", figure=fig)


def get_choro(
    fig, z, hover, ids, cmin, cmax, colorscale, geojson, selectedpoints, carte
):
    fig["data"][0]["locations"] = ids
    fig["data"][0]["geojson"] = geojson
    fig["data"][0]["text"] = hover
    fig["data"][0]["colorscale"] = colorscale
    fig["data"][0]["zmin"] = cmin
    fig["data"][0]["zmax"] = cmax
    fig["data"][0]["z"] = z

    try:
        fig["data"][0].pop("selectedpoints")
    except:
        pass

    if selectedpoints is not None:
        fig["data"][0]["selectedpoints"] = selectedpoints

    return fig


def resize(location, fig, carte, geojson):
    zoom, center_long, center_lat = get_location_center(location, geojson)

    fig["layout"]["mapbox"]["zoom"] = zoom
    fig["layout"]["mapbox"]["center"] = {"lon": center_long, "lat": center_lat}

    if carte == "Région":
        carte = "Département"
    elif carte == "Département":
        carte = "Bassin d'emploi"

    return fig, carte


def get_location_center(location, geojson):
    feature = [f for f in geojson["features"]
               if f["properties"]["code"] == location][0]
    poly = Polygon(
        get_best_fitting_polygon(feature["geometry"]["coordinates"])
        if feature["geometry"]["type"] == "MultiPolygon"
        else feature["geometry"]["coordinates"][0]
    )

    center_lon = poly.centroid.y
    center_lat = poly.centroid.x + 0.1

    dif = poly.bounds[3] - poly.bounds[1]

    zoom = -1.461 * math.log(dif) + 7.797

    zoom = round(zoom, 2)

    return zoom, center_lat, center_lon


def get_best_fitting_polygon(polys):
    best = polys[0][0]
    for poly in polys:
        if len(poly[0]) > len(best):
            best = poly[0]

    return best


def get_pie(values, names, year, type_met):
    return (
        px.pie(values=values, names=names)
        .update_layout(
            paper_bgcolor="#1f2630",
            plot_bgcolor="#1f2630",
            font={"color": "#2cfec1"},
            margin={"t": 75, "r": 0, "b": 60, "l": 0},
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.3, xanchor="left", x=0.1
            ),
            title=f"Répartition des projets de recrutement{type_met} par famille de métiers en {year}",
        )
        .update_traces(textinfo="percent", hovertemplate="%{label} <br> %{value}")
    )


def get_chart(df, name, year):
    custom_data = np.stack((df[name], df["met"]), axis=-1)
    hovertemp = "%{customdata[0]} <br> %{y}"
    name_data = [i if len(i) < 25 else i[:22] + "..." for i in df[name]]

    fig = go.Figure(
        data=[
            go.Bar(
                x=name_data,
                y=df["met"],
                name="Projets de recrutement",
                customdata=custom_data,
                hovertemplate=hovertemp,
            ),
            go.Bar(
                x=name_data,
                y=df["smet"],
                name="Projets saisonniers",
                customdata=custom_data,
                hovertemplate=hovertemp,
            ),
            go.Bar(
                x=name_data,
                y=df["xmet"],
                name="Projets difficiles",
                customdata=custom_data,
                hovertemplate=hovertemp,
            ),
        ]
    )

    fig.update_layout(
        barmode="group",
        xaxis={"categoryorder": "category ascending"},
        paper_bgcolor="#1f2630",
        plot_bgcolor="#1f2630",
        font={"color": "#2cfec1"},
        margin={"t": 75, "r": 50, "b": 100, "l": 75},
        title=f"Histogramme des projets de recrutement par famille de métiers en {year}",
    )
    fig.update_layout(
        xaxis=dict(tickangle=75, tickmode="array"),
        legend=dict(x=0.7, traceorder="normal"),
    )

    return fig


def update_pie(fig, values, names, year, famille, type_met):
    if "textinfo" in fig["data"][0]:
        fig["data"][0].pop("textinfo")
    if "textposition" in fig["data"][0]:
        fig["data"][0].pop("textposition")

    fig["layout"][
        "title"
    ] = f"""Répartition des projets de recrutement{type_met} de la famille <br>"{famille}" en {year} """
    fig["layout"]["margin"] = {"t": 75, "r": 0, "b": 80, "l": 0}
    fig["layout"]["legend"] = dict(
        orientation="v",
        yanchor="bottom",
        y=-0.6,
        xanchor="left",
        x=0,
        entrywidth=0.5,
        entrywidthmode="fraction",
    )

    fig["data"][0]["values"] = values
    fig["data"][0]["names"] = names
    fig["data"][0]["labels"] = names
    fig["data"][0]["hovertemplate"] = "%{label} <br> %{value}"

    names_list = list(names)
    colors = [None] * len(names_list)
    colors[names_list.index("Autres")] = "#063970"  # type: ignore

    fig["data"][0]["marker"] = dict(colors=colors)

    return fig


def update_chart(fig, names, met, xmet, smet, year, famille):
    custom_data = np.stack((names, met), axis=-1)
    hovertemp = "%{customdata[0]} <br> %{y}"
    names = [i if len(i) < 25 else i[:22] + "..." for i in names]

    fig["layout"][
        "title"
    ] = f"""Histogramme des projets de recrutement des métiers de la famille <br>"{famille}" en {year}"""

    fig["data"][0]["x"] = names
    fig["data"][0]["y"] = met
    fig["data"][0]["customdata"] = custom_data
    fig["data"][0]["hovertemplate"] = hovertemp

    fig["data"][1]["x"] = names
    fig["data"][1]["y"] = smet
    fig["data"][1]["customdata"] = custom_data
    fig["data"][1]["hovertemplate"] = hovertemp

    fig["data"][2]["x"] = names
    fig["data"][2]["y"] = xmet
    fig["data"][2]["customdata"] = custom_data
    fig["data"][2]["hovertemplate"] = hovertemp

    names.remove("Autres")
    names.append("Autres")
    fig["layout"]["xaxis"] = dict(categoryorder="array", categoryarray=names)

    return fig


def get_time_series(df, title):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            name="Projets de recrutement",
            x=df["annee"],
            y=df["met"],
            mode="markers+lines",
            marker_symbol="circle",
            marker_size=17,
        )
    )
    fig.add_trace(
        go.Scatter(
            name="Projets saisonniers",
            x=df["annee"],
            y=df["smet"],
            mode="markers+lines",
            marker_symbol="star",
            marker_size=17,
        )
    )
    fig.add_trace(
        go.Scatter(
            name="Projets difficiles",
            x=df["annee"],
            y=df["xmet"],
            mode="markers+lines",
            marker_symbol="square",
            marker_size=17,
        )
    )

    fig.update_layout(
        paper_bgcolor="#1f2630",
        legend=dict(x=0.005, y=0.95, traceorder="normal"),
        plot_bgcolor="#1f2630",
        font={"color": "#2cfec1"},
        margin={"t": 75, "r": 50, "b": 75, "l": 75},
        title=title,
    )

    fig.update_xaxes(showgrid=True, ticklabelmode="period")

    return fig


def update_time_series(fig, df, title):
    fig["layout"]["title"] = title

    fig["data"][0]["x"] = df["annee"]
    fig["data"][0]["y"] = df["met"]

    fig["data"][1]["x"] = df["annee"]
    fig["data"][1]["y"] = df["smet"]

    fig["data"][2]["x"] = df["annee"]
    fig["data"][2]["y"] = df["xmet"]

    return fig
