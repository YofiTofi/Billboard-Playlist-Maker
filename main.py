import requests
import bs4
import spotipy
from spotipy.oauth2 import SpotifyOAuth


BASE_BILLBOARD_URL = "https://www.billboard.com/charts/hot-100/"
SCOPE = "playlist-modify-private"


def song_searcher(songs, singers, spotify):
    """
    Known issues:
        - Sometimes Spotify returns the wrong song in a result, mostly karaoke or instrumental versions
        of the song instead of the original. This issue is partly mitigated by adding the  "-karaoke -instrumental"
        to the query, but this method is not perfect. There were still a few cases where the wrong song was returned
        by Spotify.
    :param songs: a list of songs to search for
    :param singers: a list of singers who are the creators of the songs
    :param spotify: the authenticated spotify connection
    :return: a list of spotify URIs of all the given songs, if they are on spotify. else - song is skipped
    """
    uri_list = []
    for idx, song in enumerate(songs):
        search_result = spotify.search(q=f"{song} {singers[idx]} -karaoke -instrumental", limit=1)
        try:
            uri = dict(search_result)["tracks"]["items"][0]["uri"]
            uri_list.append(uri)
        except IndexError:
            print(f"The song {song} by {singers[idx]}, rated {idx+1}, is not on Spotify.")
    return uri_list


spotify_connection = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE))
username = spotify_connection.current_user()["display_name"]
lookup_date = input("What date do you want to travel to? Use YYYY-MM-DD format: ")
response = requests.get(url=BASE_BILLBOARD_URL + lookup_date).text
soup = bs4.BeautifulSoup(response, "html.parser")
relevant_tags = soup.find_all(name="ul", class_="o-chart-results-list-row")
song_names = [tag.find(name="h3").text.strip() for tag in relevant_tags]
singer_names = [tag.find_all(name="span")[1].text.strip() for tag in relevant_tags]
song_URIs = song_searcher(song_names, singer_names, spotify_connection)
playlist = spotify_connection.user_playlist_create(user=username, name=f"{lookup_date} Billboard 100", public=False)
spotify_connection.playlist_add_items(playlist_id=playlist["uri"], items=song_URIs)
print("Playlist created")
