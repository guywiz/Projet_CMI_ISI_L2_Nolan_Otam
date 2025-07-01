
# Projet CMI Programmation - Visualisation de données avec Dash

Ce projet consiste à développer une application de visualisation de données sur l'emploi, en utilisant la librairie Dash de Python. Les données sont obtenues à partir du site data.gouv.fr et stockées dans une base de données. L'application est conçue selon le modèle MVC, avec un contrôleur qui dispose de callbacks pour exercer son contrôle sur les événements de l'application.

  

## Installation

  

1. Clonez le dépôt Git : git clone `git@gitlab.emi.u-bordeaux.fr:notam/projet-cmi-isi-l2.git`

2. Installez les dépendances : pip install -r requirements.txt

3. Importez les données dans la base de données : exécutez le script importDB.py situé dans le dossier components

4. Lancez l'application : python dashapp.py

5. Ouvrez un navigateur et accédez à l'URL http://127.0.0.1:8050

  

## Structure du projet

Le projet est organisé en plusieurs dossiers :

  

- dashapp : contient les différents composants de l'application (vue, modèle, contrôleur)

- data : contient les fichiers de données au format CSV, ainsi que les fichiers GeoJSON pour les cartes

- documentation : contient la documentation du projet

- tests : contient nos fichiers de tests

  

## Modèle de données

Le modèle gère l'accès aux données qui sont stockées dans une base de données. Le schéma de données est documenté dans le fichier Schéma_base, situé dans le dossier documentation. Les scripts permettant de reconstuire facilement la base de données à partir des fichiers sources obtenus de data.gouv.fr et de construire un fichier GeoJSON sur les bassins d'emploi sont fournis dans le dossier components.

  

## Visualisations

Nous avons sélectionné 4 visualisations pertinentes pour répondre à certaines questions sur les données :

  

1. Diagramme circulaire : Répartition des emplois par famille de métier et métier par année

2. Histogramme : Histogramme des emplois par famille de métier et métier par année

3. Carte géographique : répartition des emplois par région/département/bassin d'emploi par année

4. Graphique en courbe : Evolution du nombre de projet d'emploi par famille de métier et métier


Nous avons géré des interactions sur ces visualisations (sélection d'une zone ou cliquer sur une zone, etc.). 