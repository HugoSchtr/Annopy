import requests

def photoset_flickr_query(api_key, photoset_id, user_id):
    """
    Récupère une liste d'URL depuis un album Flickr via l'API de Flickr.
    Chaque URL correspond à une image de ladite collection.

    :param api_key: API key pour utiliser l'API de Flickr.
    :type api_key: str
    :param photoset_id: identifiant de l'album Flickr duquel on veut récupérer les images.
    :type photoset_id: int
    :param user_id: ID de l'utilisateur-rice à qui appartient l'album duquel on veut récupérer les images.
    :type user_id: str
    :return: liste d'URL d'images
    :rtype: list
    """

    # On crée une liste vide dans laquelle on pourra stocker les données de chaque image.
    imgs = []

    # On crée une variable qui va stocker la requête faite à l'API REST Flickr, plusieurs paramètres sont nécessaires.
    # La method flickr.photosets.getPhotos permet de récupérer une liste de photos dans un album.
    # api_key correspond à l'API key de l'utilisateur-rice.
    # photoset_id correspond à l'ID de l'album duquel on veut récupérer les images.
    # user_id correspond à l'ID utilisateur à qui appartient l'album duquel on veut récupérer les images.
    # nojsoncallback=1 permet d'obtenir comme réponse à la requête HTTP du raw JSON.
    # format=json permet de récupérer du JSON.
    url_query = "https://api.flickr.com/services/rest/?method=flickr.photosets.getPhotos&api_key={0}&photoset_id={1}&user_id={2}&nojsoncallback=1&format=json".format(
        api_key, photoset_id, user_id
    )

    # On stocke la requête HTTP dans une variable r.
    r = requests.get(url_query)

    # Si le code HTTP de la requête est 200 (success), r est converti en objet JSON et stocké dans data.
    # On vérifie que la requête à l'API a bien abouti avec data["stat"] == "ok"
    # On récupère trois données par image sous forme de liste.
    # L'identifiant de l'image, le secret, et le server.
    # Chaque liste est stockée dans la liste imgs. Un index = une image.
    # Si la requête renvoie un autre code que 200, ou si la requête n'a pas abouti, alors la fonction retourne False.
    if r.status_code == 200:
        data = r.json()
        if data["stat"] == "ok":
            for item in data['photoset']['photo']:
                imgs.append([item['id'], item['secret'], item["server"]])
        else:
            return False
    else:
        return False

    # L'objet JSON récupéré depuis l'API Flickr renvoie une liste inversée des images d'une collection.
    # Pour obtenir l'ordre original, visible sur un navigateur, on inverse la liste imgs.
    imgs = imgs[::-1]

    # On crée une liste vide url_list qui va stocker les URL de chaque image de l'album.
    url_list = []

    # On construit l'URL de chaque image à partir des données préalablement récupérées.
    # Au sein des listes imbriquées de imgs :
    # Index 0 = ID de l'image
    # Index 1 = secret
    # Index 2 = server
    # le paramètre b permet de récupérer l'image dans un format large (1024 px maximum pour un côté)
    # Chaque URL est stockée dans url_list.
    for idx in imgs:
        id = idx[0]
        secret = idx[1]
        server = idx[2]
        url_list.append("https://live.staticflickr.com/{0}/{1}_{2}_{3}.jpg".format(server, id, secret, "b"))
    print(url_list)

    return url_list


# imgs = photoset_flickr_query("e75749d1274235bdac7667545e19a86d", "72157718781176996", "192476676@N05")
# On teste la fonction
