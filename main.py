from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
USER_ID = "316g66uwod3nsyyozmqvmdacakdu"
os.environ["SPOTIPY_CLIENT_ID"] = "40a62237eadd40f9a307265020b55d94"
os.environ["SPOTIPY_CLIENT_SECRET"] = "48ba3687b95540908e2a96e16d975f11"
os.environ["SPOTIPY_REDIRECT_URI"] = "http://example.com"

client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

with open("token.txt") as token:
    header = token.read()

#----- scrape the billboard site for song titles from the chosen date ----------#
destination = input("What time do you want to travel to?(YYYY-MM-DD):")

billboard_url = f"https://www.billboard.com/charts/hot-100/{destination}"

response = requests.get(billboard_url)
response.raise_for_status()
billboard_contents = response.text

soup = BeautifulSoup(billboard_contents, "html.parser")
title_list = []

first_song = soup.find(name="a", class_="c-title__link lrv-a-unstyle-link")
first_song_title = first_song.getText().strip()
title_list.append(first_song_title)

songs = soup.find_all(name="h3", class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 u-max-width-230@tablet-only")
for song in songs:
    title = song.getText().strip()
    title_list.append(title)

print(title_list)
#----- interact with spotify
sp = spotipy.Spotify(auth_manager=(SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope="playlist-modify-private", show_dialog=True, cache_path="token.txt")))
#create list of query parameters for search
q_list = []
year = destination.split("-")[0]
for song in title_list:
    track = song
    year = destination.split("-")[0]
    q = f"track:{track} year:{year}"
    q_list.append(q)

print(q_list)
uri_list = []
for q in q_list:
    track = sp.search(q=q, type="track")
    try:
        track_uri = track["tracks"]["items"][0]["uri"]
        uri_list.append(track_uri)
    except IndexError:
        print(f"{q} not in spotify, skipping")

playlist = sp.user_playlist_create(user=USER_ID, name=f"{destination} Billboard chart toppers", public=False)
sp.playlist_add_items(playlist_id=playlist["id"], items=uri_list)


