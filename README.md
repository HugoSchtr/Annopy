# Annopy

Annopy est une application web développée avec le framework python [Flask](https://flask.palletsprojects.com/en/1.1.x/), mettant à disposition une plateforme de production participative (crowdsourcing) dans le but d'annoter des images. 

Chaque utilisateur-ice peut créer une collection, contenant des images importées à partir d'un manifest [IIIF](https://iiif.io/) ou d'un album [Flickr](https://www.flickr.com/), et annoter les images des différentes collections existantes.

Les annotations sont générées et gérées avec la librairie JavaScript [Annotorious](https://recogito.github.io/annotorious/), version [2.3.3](https://github.com/recogito/annotorious/releases/tag/v2.3.3).

Cette plateforme collaborative a été créée par [Hugo Scheithauer](https://github.com/HugoSchtr) dans le cadre du [Master 2 "Technologies appliquées à l'histoire"](http://www.chartes.psl.eu/fr/cursus/master-technologies-numeriques-appliquees-histoire) de l'Ecole nationale des chartes.

# Fonctionnalités

Le workflow de crowdsourcing a été conçue de la manière suivante :

1. Un-e utilisateur-ice crée une collection, en indiquant le nom du projet, une courte description, une catégorie et en important des images depuis un serveur extérieur. L'utilisateur-ice peut choisir d'importer des images depuis deux sources différents : 
  * Un manifest IIIF
  * Un album Flickr
