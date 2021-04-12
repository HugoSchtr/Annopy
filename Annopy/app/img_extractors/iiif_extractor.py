import requests


def iiif_query(manifest, from_f, to_f):
    """ Récupère une liste d'URL d'images à partir d'un manifest IIIF.

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

    # On convertit les from_f et to_f en integer.
    # Si l'utilisateur a donné des chaînes de caractères qui ne peuvent pas être convertis en integer
    # (lettres, caractères spéciaux), on renvoie False.
    try:
        from_f = int(from_f)
        to_f = int(to_f)
    except ValueError:
        return False

    # On stocke l'objet de la réponse HTTP dans r.
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
                    # Nous pourrions tester chaque URL pour savoir si le code de réponse HTTP est 200 avec :
                    # request = requests.get(img_url)
                    # Si le code HTTP est 200, alors on ajoute l'URL à url_list.
                    # if request.status_code == 200:
                        # url_img_list.append(img_url)
                    # Cependant, obtenir le code de réponse HTTP pour chaque image d'un manifest volumineux
                    # prend trop de temps.
                    # On ajoute donc les liens sans vérifier leur validité.
                    url_img_list.append(img_url)
    else:
        return False

    # Afin d'améliorer l'expérience utilisateur-rice, on modifie la gestion des index de la liste.
    # Puis, on slice url_img_list selon le choix de l'utilisateur-rice.
    if from_f >= 1:
        from_f = from_f - 1
    url_img_list = url_img_list[from_f:to_f]

    return url_img_list

# Test de la fonction
# imgs = iiif_query("https://gallica.bnf.fr/iiif/ark:/12148/bpt6k9923506/manifest.json", 1, 4)
# print(imgs)
