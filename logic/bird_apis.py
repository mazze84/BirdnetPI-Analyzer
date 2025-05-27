import requests
import streamlit as st

@st.cache_data
def get_desc_from_wiki(scientific_name, lang='en'):
    url = f"https://{lang}.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles={scientific_name}"
    response = requests.get(url)
    response = response.json()
    wiki_desc = ""
    for value in response['query']['pages']:
        wiki_desc = response['query']['pages'][value]['extract']

    return wiki_desc

def get_short_desc_wiki(scientific_name, lang='en'):
    wiki_desc = get_desc_from_wiki(scientific_name, lang)
    if len(wiki_desc) > 400:
        wiki_desc = wiki_desc[0:400]
        wiki_desc = wiki_desc[0: wiki_desc.rfind(" ")] + "..."
    bird_name = scientific_name.replace(" ", "_")
    wiki_desc += f"[https://{lang}.wikipedia.org/wiki/{bird_name}]"
    return wiki_desc

@st.cache_data
def get_pic_from_flickr(scientific_name):
    headers = {'User-Agent': 'Python_Flickr/1.0'}
    flickr_api = st.secrets["flickr_api"]
    if flickr_api is None or flickr_api == "":
        return ""
    flickr_url = f"https://www.flickr.com/services/rest/?method=flickr.photos.search&api_key={flickr_api}&text={scientific_name}&sort=relevance&per_page=5&media=photos&format=json&nojsoncallback=1"
    flickr_resp = requests.get(url=flickr_url, headers=headers)
    data = flickr_resp.json()["photos"]["photo"][0]

    image_url = 'https://farm'+str(data["farm"])+'.static.flickr.com/'+str(data["server"])+'/'+str(data["id"])+'_'+str(data["secret"])+'.jpg'
    return image_url

