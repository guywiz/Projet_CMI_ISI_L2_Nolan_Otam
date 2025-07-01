import json
import pandas as pd


def load_geojson(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


def get_choro_init_data(annee, col1, col2, db):
    df = pd.read_sql_query(
        f"SELECT SUM(met),{col1},{col2} FROM recrutements INNER JOIN geo on recrutements.code_bassin = geo.code_bassin INNER JOIN metiers on recrutements.code_metier_BMO=metiers.code_metier_BMO WHERE recrutements.annee = {annee}  GROUP BY {col1}",
        db,
    )
    df["reg"] = df["reg"].apply(lambda x: "{0:0>2}".format(x))
    return df


def get_pie_init_data(annee, col1, col2, db):
    df = pd.read_sql_query(
        f"SELECT met, {col1}, {col2} FROM recrutements INNER JOIN metiers ON recrutements.code_metier_BMO = metiers.code_metier_BMO INNER JOIN familles_metier ON metiers.code_famille_BMO = familles_metier.code_famille_BMO WHERE recrutements.annee = {annee}",
        db,
    )
    df = df.groupby(col1, as_index=False).agg({"met": "sum"})
    return df


def get_choro_data(carte, annee, color_scale_liste, carte_cores, db, col):
    if carte == "Région":
        query = f"SELECT SUM({col}),reg,nom_reg FROM recrutements INNER JOIN geo on recrutements.code_bassin = geo.code_bassin INNER JOIN metiers on recrutements.code_metier_BMO=metiers.code_metier_BMO WHERE recrutements.annee = {annee} GROUP BY reg"
        id_col = "reg"
        name_col = "nom_reg"
        cmin = None
        cmax = None
        colorscale = color_scale_liste[0]
        geojson = load_geojson(
            f"../data/geojson/{carte_cores[carte]['nom_geojson']}.geojson"
        )

    elif carte == "Département":
        query = f"SELECT SUM({col}),dept,nom_dept FROM recrutements INNER JOIN geo on recrutements.code_bassin = geo.code_bassin INNER JOIN metiers on recrutements.code_metier_BMO=metiers.code_metier_BMO WHERE recrutements.annee='{annee}' GROUP BY dept"
        id_col = "dept"
        name_col = "nom_dept"
        cmin = None
        cmax = None
        colorscale = color_scale_liste[1]
        geojson = load_geojson(
            f"../data/geojson/{carte_cores[carte]['nom_geojson']}.geojson"
        )

    elif carte == "Bassin d'emploi":
        query = f"SELECT SUM({col}),recrutements.code_bassin,nom_bassin FROM recrutements INNER JOIN geo on recrutements.code_bassin = geo.code_bassin INNER JOIN metiers on recrutements.code_metier_BMO=metiers.code_metier_BMO WHERE recrutements.annee='{annee}' GROUP BY recrutements.code_bassin"
        id_col = "code_bassin"
        name_col = "nom_bassin"
        cmin = None
        cmax = None
        colorscale = color_scale_liste[2]
        geojson = load_geojson(
            f"../data/geojson/{carte_cores[carte]['nom_geojson']}.geojson"
        )
    else:
        raise ValueError("Carte inexistante")

    df = pd.read_sql_query(query, db)

    df[id_col] = df[id_col].apply(
        lambda x: f"{x:0>2}" if id_col in ["dept", "reg"] else f"{x:0>4}"
    )
    cmax = df[f"SUM({col})"].quantile(0.98)
    cmin = 0
    z = df[f"SUM({col})"]
    hover = df[name_col]
    ids = df[id_col]


    return z, hover, ids, cmin, cmax, colorscale, geojson


def get_new_locations(clickData, carte, ids, db):
    location = clickData["points"][0]["location"]

    if carte == "Département":
        col1 = "reg"
        col2 = "dept"
    else:
        col1 = "dept"
        col2 = "code_bassin"

    query = f"""SELECT DISTINCT {col2} FROM geo where {col1} = '{location}'"""

    df = pd.read_sql_query(query, db)

    longueur = 2 if carte == "Département" or carte == "Région" else 4
    selectedPoints = [
        list(ids).index((f"{{0:0>{longueur}}}").format(i))
        for i in list(df[col2])
        if (f"{{0:0>{longueur}}}").format(i) in list(ids)
    ]

    return selectedPoints


def get_updated_locations(carte, ids, fig):
    if "selectedpoints" not in fig["data"][0]:
        return None

    previous_ids = fig["data"][0]["locations"]
    new_selection = [previous_ids[i] for i in fig["data"][0]["selectedpoints"]]

    longueur = 2 if carte == "Département" or carte == "Région" else 4
    selectedPoints = [
        list(ids).index((f"{{0:0>{longueur}}}").format(i))
        for i in new_selection
        if (f"{{0:0>{longueur}}}").format(i) in list(ids)
    ]

    return selectedPoints


def get_pie_data(db, col, selectedpoints, carte, annee, radio_button):
    query = f"SELECT met,smet,xmet, famille_metier, nom_metier, metiers.code_famille_BMO FROM recrutements INNER JOIN metiers ON recrutements.code_metier_BMO = metiers.code_metier_BMO INNER JOIN familles_metier ON metiers.code_famille_BMO = familles_metier.code_famille_BMO INNER JOIN geo on recrutements.code_bassin=geo.code_bassin WHERE annee = {annee}"

    if selectedpoints is not None:
        selectedpoints = ["'" + str(i) + "'" for i in selectedpoints]
        if carte == "Région":
            query += f" AND reg in ({','.join(selectedpoints)})"
        elif carte == "Département":
            query += f" AND dept in ({','.join(selectedpoints)})"
        elif carte == "Bassin d'emploi":
            query += f" AND geo.code_bassin in ({','.join(selectedpoints)})"
        else:
            raise ValueError("Carte inexistante")

    df = pd.read_sql_query(query, db)
    df_gb = df.groupby(["famille_metier", col], as_index=False).agg(
        {radio_button: "sum"}
    )
    return df_gb


def get_clic_pie_data(clic, db, col, selected_point, carte, annee, radio_button):
    df = get_pie_data(db, col, selected_point, carte, annee, radio_button)
    df = df[df["famille_metier"] == clic].sort_values(
        radio_button, ascending=False)
    top_df = df.head(8)
    autres = {
        radio_button: [pd.DataFrame(df.iloc[8:])[radio_button].sum()],
        "nom_metier": ["Autres"],
        "famille_metier": ["Autres"],
    }

    tmp_df = pd.DataFrame(autres)
    top_df = pd.concat([top_df, tmp_df], ignore_index=True)
    return top_df


def get_chart_data(db, col, selectedpoints, carte, annee):
    query = f"SELECT met,xmet,smet, famille_metier, nom_metier, metiers.code_famille_BMO FROM familles_metier INNER JOIN metiers ON familles_metier.code_famille_BMO = metiers.code_famille_BMO INNER JOIN recrutements ON metiers.code_metier_BMO = recrutements.code_metier_BMO INNER JOIN geo on recrutements.code_bassin=geo.code_bassin WHERE annee = {annee}"
    if selectedpoints is not None:
        selectedpoints = ["'" + str(i) + "'" for i in selectedpoints]
        if carte == "Région":
            query += f" AND reg in ({','.join(selectedpoints)})"
        elif carte == "Département":
            query += f" AND dept in ({','.join(selectedpoints)})"
        elif carte == "Bassin d'emploi":
            query += f" AND geo.code_bassin in ({','.join(selectedpoints)})"
        else:
            raise ValueError("Carte inexistante")

    df = pd.read_sql_query(query, db)
    # Calcul des totaux de met, smet et xmet par famille_metier/col
    df = df.groupby(["famille_metier", col], as_index=False).agg(
        {"met": "sum", "xmet": "sum", "smet": "sum"}
    )
    # Ajout d'une colonne avec les projets de recrutements qui sont ni difficiles ni saisoniers
    df["nmet"] = df["met"] - df["smet"] + df["xmet"]
    return df


def get_clic_chart_data(clic, db, col, selectedpoints, carte, annee):
    df = get_chart_data(db, col, selectedpoints, carte, annee)
    df_gb2 = df[df["famille_metier"] == clic].sort_values(
        ["nmet", "smet", "xmet"], ascending=False
    )
    top_df = df_gb2.head(8)
    autres = {
        "smet": [pd.DataFrame(df_gb2.iloc[8:])["smet"].sum()],
        "xmet": [pd.DataFrame(df_gb2.iloc[8:])["xmet"].sum()],
        "met": [pd.DataFrame(df_gb2.iloc[8:])["met"].sum()],
        "nmet": [pd.DataFrame(df_gb2.iloc[8:])["nmet"].sum()],
        "nom_metier": ["Autres"],
        "famille_metier": ["Autres"],
    }

    tmp_df = pd.DataFrame(autres)
    top_df = pd.concat([top_df, tmp_df], ignore_index=True)
    return top_df


def get_fam_met_lbl(db):
    df = pd.read_sql_query("SELECT famille_metier FROM familles_metier", db)
    return df["famille_metier"].to_list()


def get_met_lbl(db, fam_lbl):
    df = pd.read_sql_query(
        f"""SELECT nom_metier FROM metiers JOIN familles_metier ON familles_metier.code_famille_BMO=metiers.code_famille_BMO WHERE famille_metier= "{fam_lbl}" """,
        db,
    )
    return df["nom_metier"].to_list()


def get_time_series_data(db, nom_famille_metier, nom_metier, selectedpoints, carte):
    query = f"SELECT met,xmet,smet, famille_metier, nom_metier,annee FROM familles_metier INNER JOIN metiers ON familles_metier.code_famille_BMO = metiers.code_famille_BMO INNER JOIN recrutements ON metiers.code_metier_BMO = recrutements.code_metier_BMO INNER JOIN geo on recrutements.code_bassin=geo.code_bassin"

    if selectedpoints is not None:
        selectedpoints = ["'" + str(i) + "'" for i in selectedpoints]
        if carte == "Région":
            query += f" WHERE reg in ({','.join(selectedpoints)})"
        elif carte == "Département":
            query += f" WHERE dept in ({','.join(selectedpoints)})"
        elif carte == "Bassin d'emploi":
            query += f" WHERE geo.code_bassin in ({','.join(selectedpoints)})"

    if nom_metier is None:
        if nom_famille_metier is not None:
            if selectedpoints is not None:
                query += " AND"
            else:
                query += " WHERE"
            query += f""" familles_metier.famille_metier = "{nom_famille_metier}" """
    else:
        if selectedpoints is not None:
            query += " AND"
        else:
            query += " WHERE"
        query += f""" metiers.nom_metier = "{nom_metier}"  """

    df = pd.read_sql_query(query, db)
    df_gb = df.groupby("annee", as_index=False).agg(
        {"met": "sum", "xmet": "sum", "smet": "sum"}
    )
    return df_gb
