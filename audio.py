import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
from time import sleep
import json
import time

def main():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="54735820284c4380ac403bb4ae089d9c",
                                                   client_secret="3ccbf7901668460e80a03015d5f12da0",
                                                   redirect_uri="http://localhost:1337/callback",
                                                   scope="user-read-recently-played user-read-playback-state "
                                                         "user-top-read playlist-modify-public "
                                                         "user-modify-playback-state playlist-modify-private "
                                                         "user-follow-modify user-read-currently-playing "
                                                         "user-follow-read user-library-modify "
                                                         "user-read-playback-position playlist-read-private "
                                                         "user-read-email user-read-private user-library-read "
                                                         "playlist-read-collaborative",
                                                   open_browser=False))

    # Shows playing devices
    res = sp.devices()

    # Gets the device with the name below
    device_id = ""
    for d in res['devices']:
        if d['name'] == 'Web Player (Chrome)':
            device_id = d['id']

    # Ma
    user_list = {"nick": '5sq0472fjzjxdx70quovzgcy7', "yale": 'yaleduffy'}

    users_in_scene = ["nick"]
    songs = []
    for i in range(0,len(users_in_scene)):
        songs += get_songs(sp, user_list[users_in_scene[i]])

    print(songs)
    sp.start_playback(uris=songs, device_id=device_id)


def get_songs(sp, username):
    playlists = sp.user_playlists(username)
    playlist_id = get_playlists(sp, playlists, "Party")
    results = sp.playlist_items(playlist_id, additional_types=['track'])
    tracks = []
    for x in range(0, len(results['items'])):
        tracks += [results['items'][x]['track']['uri']]
    return tracks


def get_playlists(sp, playlists, playlist_name):
    current_playlist_id = ""
    while playlists:
        for i, playlist in enumerate(playlists['items']):
            # print(
            #     "%4d %s %s" %
            #     (i +
            #      1 +
            #      playlists['offset'],
            #      playlist['uri'],
            #      playlist['name']))
            if playlist['name'] == playlist_name:
                current_playlist_id = playlist['uri']
        # gets next page
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
    return current_playlist_id


if __name__ == "__main__":
    main()