# Anatomie d'une réponse JSON de l'API 

Vous trouverez dans ce dossier un exemple de réponse de l'API pour une collection de démonstration.

## La collection
```
{
  "type": "collection", 
  "id": 7, 
  "attributes": {
    "name": "Nina Simone - Collection de demonstration", 
    "Category": [
      {
        "category": {
          "type": "category", 
          "attributes": {
            "category_name": "Musique"
          }
        }
      }
    ], 
   "description": "Une collection comprenant une photographie de Nina Simone en train de chanter (photographie de David. D. Spitzed, 1977). "
  }, 
  "relationships": {
    "editions": [
      {
        "author": {
          "type": "people", 
          "attributes": {
            "user_id": 1, 
            "login": "superadmin", 
            "user_forename": "Hugo", 
            "user_surname": "Sch"
          }
        }, 
        "on": "Sun, 11 Apr 2021 16:15:17 GMT"
      }
    ]
  }, 
  ```
  
  Cette partie contient les métadonnées de la collection. 
  
  Ici, nous comprenons que la collection s'appelle "Nina Simone - Collection de demonstration", qu'une description est disponible, et qu'elle a été créée par "superadmin" le dimanche 11 avril.
  
  ## Les images
  
  ```
  "images": [
    {
      "image": {
        "type": "image", 
        "attributes": {
          "id": 16, 
          "url": "https://ids.si.edu/ids/iiif/NMAAHC-2012_164_125_001/full/full/0/default.jpg", 
          "annotations": [
            {
              "type": "annotation", 
              "attributes": {
                "id": 6, 
                "annotation_json": [
                  {
                    "type": "Annotation", 
                    "body": [
                      {
                        "type": "TextualBody", 
                        "value": "Nina Simone", 
                        "purpose": "commenting"
                      }
                    ], 
                    "target": {
                      "source": "https://ids.si.edu/ids/iiif/NMAAHC-2012_164_125_001/full/full/0/default.jpg", 
                      "selector": {
                        "type": "FragmentSelector", 
                        "conformsTo": "http://www.w3.org/TR/media-frags/", 
                        "value": "xywh=pixel:263.2655334472656,459.997314453125,743.5176696777344,784.0206298828125"
                      }
                    }, 
                    "@context": "http://www.w3.org/ns/anno.jsonld", 
                    "id": "#bc6c4ae0-7cb0-47f8-b138-a34af9dfd368"
                  }
                ], 
                "relationships": {
                  "editions": [
                    {
                      "author": {
                        "type": "people", 
                        "attributes": {
                          "user_id": 1,
                          "login": "superadmin", 
                          "user_forename": "Hugo", 
                          "user_surname": "Sch"
                        }
                      }, 
                      "on": "Sun, 11 Apr 2021 16:15:58 GMT"
                    }
                  ]
                }
              }
            }, 
             [AUTRES ANNOTATIONS]
          ]
        }
      }
    }
  ], 
  ```
  
Cette partie contient les métadonnées des images de la collection. Pour chaque image, on indique le lien de celle-ci et les annotations.

## Les annotations

```
{
  "type": "annotation", 
  "attributes": {
    "id": 6, 
    "annotation_json": [
      {
        "type": "Annotation", 
        "body": [
          {
            "type": "TextualBody", 
            "value": "Nina Simone", 
            "purpose": "commenting"
          }
        ], 
        "target": {
          "source": "https://ids.si.edu/ids/iiif/NMAAHC-2012_164_125_001/full/full/0/default.jpg", 
          "selector": {
            "type": "FragmentSelector", 
            "conformsTo": "http://www.w3.org/TR/media-frags/", 
            "value": "xywh=pixel:263.2655334472656,459.997314453125,743.5176696777344,784.0206298828125"
          }
        }, 
        "@context": "http://www.w3.org/ns/anno.jsonld", 
        "id": "#bc6c4ae0-7cb0-47f8-b138-a34af9dfd368"
      }
    ], 
    "relationships": {
      "editions": [
        {
          "author": {
            "type": "people", 
            "attributes": {
              "user_id": 1, 
              "login": "superadmin", 
              "user_forename": "Hugo", 
              "user_surname": "Sch"
            }
          }, 
          "on": "Sun, 11 Apr 2021 16:15:58 GMT"
        }
      ]
    }
  }
}
```

Une annotation prend ce format. L'annotation en elle-même est générée par [Annotorious](https://recogito.github.io/annotorious/getting-started/web-annotation/) selon le modèle des annotations intéropérables instauré par le [W3C](https://www.w3.org/TR/annotation-model/). 

Dans ```body```, on retrouve la ```value``` qui est la valeur de l'annotation créée par l'utilisateur-ice.
Dans ```target```, on retrouve la ```source``` de l'image (son URL), et la ```value``` qui nous donne les coordonnées xywh (x, y, width, heighth) en pixel de l'annotation sur l'image annotée. 

Ces quelques valeurs permettraient de réexploiter les annotations, en les visualisant sur un viewer par exemple, ou en les récupérant automatiquement.
