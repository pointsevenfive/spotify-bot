import creds
import requests
import json
import spotify_login as spotify
import datetime
import re as regex

# Global variables
api_twitter = 'https://api.twitter.com'
api_spotify = 'https://api.spotify.com'
open_spotify = 'https://open.spotify.com'
spotify_accounts = 'https://accounts.spotify.com'
max_tweets = '200'
max_tracks = 5
status_codes = {}

# Formatting
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'

def start_bot():
    print('Beep boop starting spotify bot...')
    print('max tweets set to: ' + max_tweets)
    print('twitter user id: ' + creds.ww_fm_twitter_id)

def log_response(url, rsp_code):
    code = str(rsp_code)
    status_codes[url] = code
    if not code.startswith('2'):
        code = FAIL + code + ENDC
    else:
        code = OKGREEN + code + ENDC
    print('Received {code} response from {url}'.format(code=code, url = url))

def get_oauth_twitter():
    url = api_twitter + '/oauth2/token'
    data = 'grant_type=client_credentials'
    auth = creds.twitter_basic
    headers = {
        'Authorization': 'Basic {auth}'.format(auth=str(auth)), 
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(url, data=data, headers=headers)
    oauth = json.loads(response.content)
    log_response(url, response.status_code)
    return oauth.get('access_token')

def get_tweets(user_id):
    url = api_twitter + '/1.1/statuses/user_timeline.json?user_id=' + user_id + '&count=' + max_tweets
    token = get_oauth_twitter()
    headers = { 'Authorization': 'Bearer {token}'.format(token=str(token)) }
    response = requests.get(url, headers=headers)
    log_response(url, response.status_code)
    return json.loads(response.content)

def get_tracks_from_tweets(tweets):
    tracks = []
    for tweet in tweets:
        track = tweet['text'].replace('Now Playing: ', '')
        tracks.append(track)
    return tracks

def get_oauth_spotify():
    url = spotify_accounts + '/api/token'
    data = 'grant_type=client_credentials'
    auth = creds.spotify_basic
    headers = {
        'Authorization': 'Basic {auth}'.format(auth=str(auth)), 
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(url, data=data, headers=headers)
    oauth = json.loads(response.content)
    log_response(url, response.status_code)
    return oauth.get('access_token')

def query_spotify(tracks):
    spotify_search = api_spotify + '/v1/search'
    query_type = 'track'
    token = get_oauth_spotify()
    headers = {'Authorization': 'Bearer ' + token}
    track_ids = {}
    track_idx = 0
    print('Searching for tracks...')
    while len(track_ids) < max_tracks:
        track = tracks[track_idx]
        url = append_spotify_query_string(spotify_search, track, query_type)
        response = requests.get(url, headers=headers)
        track_id = get_track_id_from_response(json.loads(response.content))
        if track_id != '':
            print('Found ' + str(track) + ' on Spotify!')
            track_ids[track] = track_id
        track_idx += 1
    print('Found ' + str(len(track_ids)) + ' out of a possible ' + str(len(tracks)))
    return track_ids

def append_spotify_query_string(endpoint, track, query_type):
    track = track.replace(' ', '+')
    query = endpoint + '?q=' + track + '&type=' + query_type
    return clean_uri(query)

def clean_uri(uri):
    return regex.sub('(#|\(|\)|&amp)', '', uri)

def get_track_id_from_response(reponse):
    tracks = reponse['tracks']
    items = tracks['items']
    if len(items) > 0:
        track_id = items[0]['id']
        return track_id
    return ''

def get_playlist_name():
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    playlist_name = 'WWFM bot ' + today
    return playlist_name

def create_playlist(tracks):
    auth = spotify.login_to_spotify()
    url = api_spotify + '/v1/users/' + creds.spotify_uname + '/playlists'
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    playlist_name = 'WWFM bot ' + today
    description = 'Playlist created by ww_fm_spotify_bot on ' + today
    data = {
        'name': playlist_name,
        'public': True,
        'description': description
    }
    headers = {
        'Authorization': 'Bearer {token}'.format(token=auth), 
        'Content-Type': 'application/json'
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    log_response(url, response.status_code)
    playlist_json = json.loads(response.content)
    return add_tracks(tracks, playlist_json['id'], auth)
    

def get_tracks_json(track_ids):
    uris = {}
    tracks = []
    for track_title in track_ids:
        track_uri = 'spotify:track:' + track_ids.get(track_title)
        tracks.append(track_uri)
    uris['uris'] = tracks
    return json.dumps(uris)

def add_tracks(tracks, playlist_id, auth):
    url = api_spotify + '/v1/playlists/{id}/tracks'.format(id=playlist_id)
    headers = {
        'Authorization': 'Bearer {token}'.format(token=auth), 
        'Content-Type': 'application/json'
    }
    response = requests.post(url, data=tracks, headers=headers)
    log_response(url, response.status_code)
    return open_spotify + '/user/{user_id}/playlist/{id}'.format(user_id=creds.spotify_uname, id=playlist_id)

def post_playlist(link):
    url = api_twitter + '/1.1/statuses/update.json'
    token = get_oauth_twitter()
    headers = {'Authorization': 'Bearer {token}'.format(token=str(token))}
    playlist_name = get_playlist_name()
    data = {'status': playlist_name, 'attachment_url': link}
    response = requests.post(url, headers=headers, data=data)
    log_response(url, response.status_code)

def health_check():
    is_failure = False
    for url in status_codes.keys():
        code = status_codes[url]
        if not url.startswith('2'):
            is_failure = True
    if is_failure:
        end = input(FAIL + 'Error occurred when running bot...' + WARNING + ' maintenance required please check output' + ENDC)

def run():
    start_bot()
    post_playlist(
        create_playlist(
            get_tracks_json(
                query_spotify(
                    get_tracks_from_tweets(
                        get_tweets(creds.ww_fm_twitter_id))))))

run()
health_check()
