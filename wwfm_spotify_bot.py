import creds
import requests
from requests.utils import requote_uri
import json
import spotify_login
import datetime

# Global variables
ww_fm_twitter_id = '848867413848457217'
max_tweets = '155'

def get_oauth_twitter():
    print('Getting oauth from twitter...')
    url = 'https://api.twitter.com/oauth2/token'
    data = 'grant_type=client_credentials'
    auth = creds.twitter_basic
    headers = {'Authorization': 'Basic ' + str(auth), 'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=data, headers=headers)
    oauth = json.loads(response.content)
    print('Received ' + str(response.status_code) + ' response from twitter /oauth/token')
    return oauth.get('access_token')

def get_tweets(user_id):
    print('Getting tweets for ' + ww_fm_twitter_id)
    url = 'https://api.twitter.com/1.1/statuses/user_timeline.json?user_id=' + user_id + '&count=' + max_tweets
    token = get_oauth_twitter()
    headers = {'Authorization': 'Bearer ' + str(token)}
    response = requests.get(url, headers=headers)
    print('Received ' + str(response.status_code) + ' response from /statuses/user_timeline')
    return json.loads(response.content)

def get_tracks_from_tweets(tweets):
    tracks = []
    for tweet in tweets:
        track = tweet['text'].replace('Now Playing: ', '')
        tracks.append(track)
    return tracks

def get_oauth_spotify():
    print('Getting oauth from spotify...')
    spotify_auth_url = 'https://accounts.spotify.com/api/token'
    data = 'grant_type=client_credentials'
    auth = creds.spotify_basic
    headers = {'Authorization': 'Basic ' + str(auth), 'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(spotify_auth_url, data=data, headers=headers)
    oauth = json.loads(response.content)
    print('Received ' + str(response.status_code) + ' response from /token')
    return oauth.get('access_token')

def query_spotify(tracks):
    spotify_search = 'https://api.spotify.com/v1/search'
    type = 'track'
    token = get_oauth_spotify()
    headers = {'Authorization': 'Bearer ' + token}
    track_ids = {}
    print('Searching for tracks...')
    for track in tracks:
        url = append_spotify_query_string(spotify_search, track, type)
        print(url)
        response = requests.get(url, headers=headers)
        track_id = get_track_id_from_response(json.loads(response.content))
        if track_id != '':
            print('Found ' + str(track) + ' on Spotify!')
            track_ids[track] = track_id
    print('Found ' + str(len(track_ids)) + ' out of a possible ' + str(len(tracks)))
    return track_ids

def append_spotify_query_string(endpoint, track, type):
    track = track.replace(' ', '+')
    query = endpoint + '?q=' + track + '&type=' + type
    return clean_uri(query)

def clean_uri(uri):
    uri = uri.replace('#', '')
    uri = uri.replace('(', '')
    uri = uri.replace(')', '')
    uri = uri.replace('&amp', '')
    return uri


def get_track_id_from_response(reponse):
    tracks = reponse['tracks']
    items = tracks['items']
    if len(items) > 0:
        track_id = items[0]['id']
        return track_id
    return ''

def create_playlist(auth):
    url = 'https://api.spotify.com/v1/users/' + creds.spotify_uname + '/playlists'
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    playlist_name = 'WWFM bot ' + today
    description = 'Playlist created by ww_fm_spotify_bot on ' + today
    print('Creating playlist: ' + playlist_name)
    data = {
        'name': playlist_name,
        'public': True,
        'description': description
    }
    headers = {'Authorization': 'Bearer ' + str(auth), 'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    print('Received ' + str(response.status_code) + ' response code from /playlists')
    playlist_json = json.loads(response.content)
    playlist_url = playlist_json['external_urls']['spotify']
    print('Created playlist: ' + playlist_name + ' link: ' + playlist_url)
    return playlist_json['id']

def generate_tracks_json(track_ids):
    uris = {}
    tracks = []
    for track_title in track_ids:
        track_uri = 'spotify:track:' + track_ids.get(track_title)
        tracks.append(track_uri)
    uris['uris'] = tracks
    return json.dumps(uris)

def post_tracks(tracks, playlist_id, auth):
    print('Adding tracks to playlist: ' + playlist_id)
    url = 'https://api.spotify.com/v1/playlists/%playlist_id%/tracks'.replace('%playlist_id%', playlist_id)
    headers = {'Authorization': 'Bearer ' + auth, 'Content-Type': 'application/json'}
    response = requests.post(url, data=tracks, headers=headers)
    if response.status_code == 201:
        print('Tracks added. Happy listening! Bot out.')
    else:
        print('Error during bot execution. please refer to logs for details')

# Main sequence
track_ids = query_spotify(
    get_tracks_from_tweets(
        get_tweets(ww_fm_twitter_id)))
auth = spotify_login.login_to_spotify()
playlist_id = create_playlist(auth)
tracks_body = generate_tracks_json(track_ids)
post_tracks(tracks_body, playlist_id, auth)