import requests

def photoset_flickr_query(api_key, photoset_id, user_id):
    imgs = []
    counter = 1

    url_query = "https://api.flickr.com/services/rest/?method=flickr.photosets.getPhotos&api_key={0}&photoset_id={1}&user_id={2}&nojsoncallback=1&format=json".format(
        api_key, photoset_id, user_id
    )

    r = requests.get(url_query)
    data = r.json()

    if r.status_code == 200:
        if data["stat"] == "ok":
            for item in data['photoset']['photo']:
                imgs.append([item['id'], item['secret'], item["server"]])
                counter += 1
        else:
            return False

    imgs = imgs[::-1]

    url_list = []

    for idx in imgs:
        id = idx[0]
        secret = idx[1]
        server = idx[2]
        url_list.append("https://live.staticflickr.com/{0}/{1}_{2}_{3}.jpg".format(server, id, secret, "b"))
    print(url_list)

    return url_list


# imgs = photoset_flickr_query("e75749d1274235bdac7667545e19a86d", "72157718781176996", "192476676@N05")
# On teste la fonction
