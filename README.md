# Annopy

Annopy est une application web développée avec le framework python [Flask](https://flask.palletsprojects.com/en/1.1.x/), mettant à disposition une plateforme de production participative (crowdsourcing) dans le but d'annoter des images. 

Chaque utilisateur-ice peut créer une collection, contenant des images importées à partir d'un manifest [IIIF](https://iiif.io/) ou d'un album [Flickr](https://www.flickr.com/), et annoter les images des différentes collections existantes.

Les annotations sont générées et gérées avec la librairie JavaScript [Annotorious](https://recogito.github.io/annotorious/), version [2.3.3](https://github.com/recogito/annotorious/releases/tag/v2.3.3).

Cette plateforme collaborative a été créée par [Hugo Scheithauer](https://github.com/HugoSchtr) dans le cadre du [Master 2 "Technologies appliquées à l'histoire"](http://www.chartes.psl.eu/fr/cursus/master-technologies-numeriques-appliquees-histoire) de l'Ecole nationale des chartes.

# Workflow du crowdsourcing 

Le workflow de crowdsourcing a été conçue de la manière suivante :

1. Un-e utilisateur-ice crée une collection, en indiquant le nom du projet, une courte description, une catégorie et en important des images depuis un serveur extérieur. L'utilisateur-ice peut choisir d'importer des images depuis deux sources différents : 

    * Un manifest IIIF
    * Un album Flickr

2. Une fois la collection créée, les utilisateurs peuvent commencer à annoter la collection. 

3. Il est possible de récupérer les données d'une image (metadonnées et annotations), ou d'une collection (metadonnées, images, annotations) à tout moment au format JSON via l'API. 

# Fonctionnalités

### Utilisateurs non connectés

Les utilisateurs non connectées peuvent :

* Naviguer à travers les collections déjà créées. 

* Accéder à une collection et consulter ses metadonnées, ainsi que connaître le nombre d'images à annoter, sans pouvoir les consulter ni les annoter.

* Faire une recherche dans les collections.

* Accéder à la page de la communauté, montrant les membres de la plateforme. 

* S'inscrire.

### Utilisateurs connectés

Les utilisateurs connectés peuvent :

* Avoir accès aux fonctionnalités des utilisateurs non connectés.
* Avoir accès à leur profil utilisateur

    * Modifier leur compte utilisateur
    * Modifier leur mot de passe

* Créer une nouvelle collection pour commencer un projet de crowdsourcing. 
* Créer une nouvelle catégorie si besoin. 
* Annoter les images d'une collection. Attention, un-e utilisateur-ice ne peut annoter qu'une seule fois une image. Une fois les annotations envoyées, l'utilisateur-ice ne pourra plus avoir accès à l'image.
* Modifier (nom, description) une collection.
* Supprimer une collection. 
* Récupérer via l'API les données d'une image d'une collection, ou d'une collection entière. 

# Spécificités techniques

Cette application a été développée avec Python3 et le framework d'application web Flask. Le design de l'application a été réalisé avec le framework [Bootstrap](https://getbootstrap.com/).

# Installation 

## Linux

* Cloner ce repository git en local : ```git clone https://github.com/HugoSchtr/Annopy```

* Installer un environnement virtuel avec Python3 :

   * Assurez-vous que votre version de Python est 3.x : ```python3 --version```
   * Créer un environnement virtuel dans le repository cloné, ou ailleurs en local : ```virtualenv -p python3 [NOM DE VOTRE ENVIRONNEMENT VIRTUEL]```

* Ouvrez un terminal et naviguer jusque dans le dossier courrant de votre environnement virtuel pour le sourcer : ```source env/bin/activate```

* Assurez-vous que vous êtes dans le repository cloné, installer les librairies python de requirements.txt : ```pip install -r requirements.txt```

* Lancez l'application : ```python3 run.py```

Pour relancer l'application plus tard, il suffira de sourcer l'environnement virtuel et de lancer l'application.
