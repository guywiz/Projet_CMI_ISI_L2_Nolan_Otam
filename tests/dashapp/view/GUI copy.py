import plotly.express as px
import plotly.graph_objects as go
import math

from shapely.geometry import Polygon
from dash import Dash, dcc, html, Input, Output, State, ctx


def layout(year_range, carte_option, fig_data, possible_plot):
    return html.Div(
        id="root",
        children=[
            html.Div(id="header", children=[
                     html.H1(children="Test de layout")]),
            html.Div(id="app-container", children=[
                html.Div(id="left-column", children=[
                    html.Div(id="year-slider-dropdown-container", children=[
                        get_year_slider(year_range),
                        get_left_drop_down(carte_option)]),

                    html.Div(id="chropleth-container", children=[
                        html.P(id="choropleth-title",
                               children=f"Carte de {year_range[0]}"),
                        create_dash_choropleth(fig_data)
                    ])
                ]),
                html.Div(id="plot-container", children=[
                    html.P(id="dropdown-title", children="Select : "),
                    get_right_drop_down(possible_plot),
                    create_plot()
                ])
            ])

        ])


def get_left_drop_down(carte_option):
    return dcc.Dropdown(id="carte-dropdown",
                        options=carte_option,
                        value=carte_option[0])


def get_right_drop_down(possibe_plot):
    return dcc.Dropdown(id="plot-dropdown",
                        options=possibe_plot,
                        value=possibe_plot[0])


def create_plot():
    return dcc.Graph(id="plot", figure=dict(data=[], layout=dict(paper_bgcolor="#1f2630",
                                                                 plot_bgcolor="#1f2630", font={"color": "#2cfec1"},
                                                                 margin={'t': 75, 'r': 50, 'b': 100, 'l': 75})))


def get_year_slider(year_range):
    return dcc.Slider(year_range[0], year_range[-1], 1,
                      value=year_range[0],
                      id='year-slider',
                      marks={i: f'{i}' for i in year_range})


def create_dash_choropleth(fig_data):
    fig = go.Figure(go.Choroplethmapbox(
        locations=fig_data["locations"],
        z=fig_data["z"],
        text=fig_data["text"],
        colorscale='reds',
        geojson=fig_data["geojson"], marker_opacity=0.8, featureidkey='properties.code')).update_layout(mapbox_style="carto-darkmatter",
                                                                                                        mapbox_center={"lat": 47.0, "lon": 2}, mapbox_zoom=4.5, autosize=True,
                                                                                                        paper_bgcolor="#1f2630",
                                                                                                        plot_bgcolor="#1f2630", font={"color": "#2cfec1"},
                                                                                                        margin={'t': 0, 'r': 0, 'b': 0, 'l': 0}).update_traces(colorbar_x=0.91)
    return dcc.Graph(id="choropleth", figure=fig)


def get_fig(fig, z, hover, ids, cmin, cmax, colorscale, geojson, selectedpoints, carte):

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
    poly = Polygon(get_best_fitting_polygon(
        feature["geometry"]["coordinates"]) if feature["geometry"]["type"] == 'MultiPolygon' else feature["geometry"]["coordinates"][0])

    center_lon = poly.centroid.y
    center_lat = poly.centroid.x + 0.1

    dif = poly.bounds[3]-poly.bounds[1]

    zoom = -1.461 * math.log(dif) + 7.797

    zoom = round(zoom, 2)

    return zoom, center_lat, center_lon


def get_best_fitting_polygon(polys):
    best = polys[0][0]
    for poly in polys:
        if len(poly[0]) > len(best):
            best = poly[0]

    return best


def get_pie(df, names, values):
    return px.pie(df, values=values, names=names)


def get_chart(df, names, values):
    fig = go.Figure(go.Bar(x=df['famille_metier'], y=df['met'], name='met'))
    fig.add_trace(go.Bar(x=df['famille_metier'], y=df['smet'], name='smet'))
    fig.add_trace(go.Bar(x=df['famille_metier'], y=df['xmet'], name='xmet'))

    fig.update_layout(barmode='stack', xaxis={
        'categoryorder': 'category ascending'})
    return fig
