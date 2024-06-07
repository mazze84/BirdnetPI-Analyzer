import requests
import streamlit as st

def get_desc_from_wiki(science_name):
    url = f"https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles={science_name}"
    response = requests.get(url)
    response = response.json()
    wiki_desc = ""
    for value in response['query']['pages']:
        wiki_desc = response['query']['pages'][value]['extract']

    return wiki_desc

def get_pic_from_flickr(common_name):
    headers = {'User-Agent': 'Python_Flickr/1.0'}
    flickr_api = st.secrets["flickr_api"]
    if flickr_api is None or flickr_api == "":
        return ""
    flickr_url = f"https://www.flickr.com/services/rest/?method=flickr.photos.search&api_key={flickr_api}&text={common_name}&sort=relevance&per_page=5&media=photos&format=json&nojsoncallback=1"
    flickr_resp = requests.get(url=flickr_url, headers=headers)
    data = flickr_resp.json()["photos"]["photo"][0]

    image_url = 'https://farm'+str(data["farm"])+'.static.flickr.com/'+str(data["server"])+'/'+str(data["id"])+'_'+str(data["secret"])+'_n.jpg'
    return image_url

