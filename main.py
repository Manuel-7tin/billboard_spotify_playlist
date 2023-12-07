# 1- Import required Libraries
from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint


def get_song_owner(artistes: str):
    """Takes in a string of multiple artists involved in a song and returns the actual song owner"""
    artist_list = artistes.split(" ")
    song_owner = ""
    for artist in artist_list:
        if artist == "Featuring" or artist == "With" or artist == "X" or artist == "&" or artist == "x":
            break
        elif artist[len(artist) - 1] == ",":
            index = artist_list.index(artist)
            if artist_list[index + 1] == "The" and artist_list[index + 2] == "Creator":
                song_owner += artist + " "
            else:
                song_owner += artist.strip(",")
                return song_owner
        else:
            song_owner += artist + " "
    return song_owner[0:len(song_owner)-1]


# 2- Set less-likely to change variables ("I have forgotten the professional term for them")
CLIENT_ID = "Your_Spotify_Client_ID"
CLIENT_SECRET = "Your_Spotify_Client_Secret"
SCOPE = "playlist-modify-private user-read-private playlist-modify-public"

# 3- Scrape top 100 weekly trending songs from billboards official website
song_date = input("Which day do you want to travel to? Type the date in this format YYYY-MM-DD: ")
date_links = "https://www.billboard.com/charts/hot-100/" + song_date + "/"
response = requests.get(url=date_links)
site = response.text
song_list = []
soup = BeautifulSoup(site, "html.parser")
songs = soup.find_all("h3", class_="u-line-height-normal@mobile-max")
artists = soup.find_all("span", class_="a-truncate-ellipsis-2line")

# for artist in artists:
#     artiste = artist.getText().strip(" \n\t")
#     song_owner = get_song_owner(artist.getText().strip(" \n\t"))
#     print(artiste, "-_---_-", song_owner)
#     print(len(artiste), "-_---_-", len(song_owner))

# 4- Create a list of dictionaries of songs and their respective artists
for i in range(len(songs)):
    artist_song = {
        "artist": get_song_owner(artists[i].getText().strip(" \n\t")),
        "song": songs[i].getText().strip(" \n\t"),
    }
    # print("Artist is:  --_-", artist_song["artist"], "-_--")
    song_list.append(artist_song)
print("song len is", len(song_list))
# pprint(song_list)

# 5- Establish spotify connection
auth_manager = SpotifyOAuth(scope=SCOPE, client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                            redirect_uri="http://example.com")
spotify = spotipy.Spotify(auth_manager=auth_manager)
# pprint(spotify.me())
username = spotify.me().get("display_name")
user_id = spotify.me().get("id")
print("Thy name hath", username, "--And id hath", user_id)

# result = spotify.search("calm down")
# for name in result.get("tracks").get("items"):
#     name["album"]["available_markets"] = ""
#     print("\n --_- A BREAK -_--\n")
#     # pprint(name)
#     print("Track uri is", name["uri"])

# 6- Create a list of spotify uri's for the song-artist list created in step 4 above
uri_list = []
not_found = []
found = []
for song in song_list:
    result = spotify.search(song.get("song"))
    for name in result.get("tracks").get("items"):
        artist_song = name.get("album").get("artists")[0]
        if artist_song.get("name") == song.get("artist"):
            # uri_list.append({song.get("artist"): [song.get("song"), artist_song.get("uri")]})
            uri_list.append(name.get("uri"))
            found.append({
                "artist": song.get("artist"),
                "song": song.get("song"),
            })
            break
for dic in song_list:
    if dic not in found:
        not_found.append(dic)
pprint(uri_list)
# pprint(not_found)
print("len of not_found = ", len(not_found))

# 7- Create private spotify playlist for user
playlist_name = song_date + " Billboard " + str(len(uri_list))
print(playlist_name)
playlist = spotify.user_playlist_create(user=user_id, name=playlist_name)

# 8- Add tracks to the playlist created in step 7 above
spotify.playlist_add_items(playlist_id=playlist["id"], items=uri_list)
