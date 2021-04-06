import requests


def ark_query(manifest, from_f, to_f):
    """ Récupère une liste d'URL d'image à partir d'un manifest IIIF.

    :param manifest: URL du manifest IIIF duquel seront récupérées les URL de chaque image.
    :type manifest: str
    :param from_f: Premier chiffre de l'intervalle permettant de sélectionner une fourchette d'images.
    :type from_f: int
    :param to_f: Deuxième chiffre de l'intervalle.
    :type to_f: int
    :return: Liste des URL des images sélectionnées du manifest IIIF.
    :rtype: list
    """

    # On crée une liste vide dans laquelle on pourra stocker les URL de chaque image.
    url_img_list = []

    # On stocke la requête HTTP dans une variable r.
    r = requests.get(manifest)

    # Si le code HTTP de la requête est 200 (success), r est converti en objet JSON et stocké dans data.
    # Pour chaque image du manifest IIIF, on stocke dans img_url l'URL de l'image.
    # Si la requête renvoie un autre code que 200, alors la fonction retourne False.
    if r.status_code == 200:
        data = r.json()
        for item in data['sequences']:
            for page in item['canvases']:
                for img_data in page["images"]:
                    img_url = img_data["resource"]["@id"]
                    url_img_list.append(img_url)
    else:
        return False

    # Afin d'améliorer l'expérience utilisateur-rice, on modifie la gestion des index de la liste.
    # Puis, on slice url_img_list selon le choix de l'utilisateur-rice.
    if from_f == 1:
        from_f = 0
    if from_f > 1:
        from_f = from_f - 1
    url_img_list = url_img_list[from_f:to_f]

    return url_img_list


# ark_query("https://ids.si.edu/ids/manifest/NMAAHC-2012_164_125_001", 0, 2)
# Test de la fonction
