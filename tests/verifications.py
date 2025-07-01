import csv


with open ('/home/marie/code/code/projet_programmation_CMI/projet/projet-cmi-isi-l2/data/Emplois_2017.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    liste_familles_metier= []
    for row in reader:
        if row['Lbl_fam_met'] not in liste_familles_metier:
            liste_familles_metier.append(row['Lbl_fam_met'])

    nb_lignes = 0
    for row in reader:
        if row['xmet'] != row['met']:
            nb_lignes += 1
    
    print ("Le nbre de lignes avec xmet différent de met est :", nb_lignes)
#print(liste_familles_metier)

'rgb(248, 248, 255)'
'rgb(67, 67, 67)'

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
