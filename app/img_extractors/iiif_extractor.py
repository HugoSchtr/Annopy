import requests


def ark_query(manifest, from_f, to_f):
    """
    From an ark identifier, a beginning folio number (from) and an ending folio number (to),
    saves a list of image URLs located in the given interval, by requesting them
    from Gallica's IIIF API. Also saves in a list the metadata of the given ark identifier.
    :param ark: ark identifier from which images URL will get retrieve.
    :type ark: str
    :param from_f: beginning folio number for the download interval.
    :type from_f: int
    :param to_f: ending folio number for the download interval.
    :type to_f: int
    :return: image URL list
    :rtype: list
    """

    url_img_list = []

    r = requests.get(manifest)
    if r.status_code == 200:
        data = r.json()
        for item in data['sequences']:
            for page in item['canvases']:
                for img_data in page["images"]:
                    img_url = img_data["resource"]["@id"]
                    url_img_list.append(img_url)
    else:
        return False

    if from_f == 1:
        from_f = 0
    if from_f > 1:
        from_f = from_f - 1
    url_img_list = url_img_list[from_f:to_f]

    return url_img_list


# ark_query("https://ids.si.edu/ids/manifest/NMAAHC-2012_164_125_001", 0, 2)
# Test de la fonction
