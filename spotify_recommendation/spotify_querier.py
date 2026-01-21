import requests, json, os, time
import urllib.parse
from .path import cache_folder
from spotify_recommendation.secrets_keys import api_client_id

class SpotifyQuerier :
    def __init__(self, api_auth_token, pathfinder_secrets=None, cache_folder = cache_folder) :
        self.api_auth_token =  api_auth_token
        self.cache_folder = cache_folder
        self.pathfinder_secrets = pathfinder_secrets

        '''
        self.web_authorisation_token = None
        self.web_authorisation_token_expiration_date = None
        self.web_authorisation_token = self.get_web_authorisation_token()
        '''
        
        if not os.path.exists(self.cache_folder) :
            os.mkdir(self.cache_folder)

    '''  
    def get_web_authorisation_token(self) :
        if not self.api_spclient_wg_spotify_bearer is None :
            return self.api_spclient_wg_spotify_bearer

        if self.web_authorisation_token is None or \
            self.web_authorisation_token_expiration_date is None or\
            self.web_authorisation_token_expiration_date < time.time():
            
            payload = {
                "client_data": {
                    "client_version": "1.2.74.270.g75831607",
                    "client_id": api_client_id,
                    "js_sdk_data": {
                        "device_brand": "unknown",
                        "device_model": "unknown",
                        "os": "windows",
                        "os_version": "NT 10.0",
                        "device_id": "",
                        "device_type": "computer"
                    }
                }
            }
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }

            r_token = self.post("https://clienttoken.spotify.com/v1/clienttoken", headers=headers, payload=payload)
            
            assert 'granted_token' in r_token and 'token' in r_token['granted_token'] and 'expires_after_seconds' in r_token['granted_token']

            self.web_authorisation_token_expiration_date = time.time() + r_token['granted_token']['expires_after_seconds']
            self.web_authorisation_token_expiration = r_token['granted_token']['token'] 
        
        return self.web_authorisation_token_expiration
    '''

    def post(self, url, headers, payload, cached_filename=None):
        cached_path = f'{self.cache_folder}{cached_filename}.json'
        if os.path.exists(cached_path):
            cached_path = f'{self.cache_folder}{cached_filename}.json'
            with open(cached_path, encoding='utf8') as f :
                return json.load(f)
            
        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        if response.status_code >= 300 :
            print(f"error code {response.status_code}, response text:", response.text)
            return {}
        response = response.json()
        
        if not cached_filename is None :
            with open(cached_path, 'w', encoding='utf8') as f :
                json.dump(response, f)
        return response
    
    def get(self, url, headers, cached_filename):
        cached_path = f'{self.cache_folder}{cached_filename}.json'
        if os.path.exists(cached_path):
            with open(cached_path, encoding='utf8') as f :
                return json.load(f)
            
        response = requests.request("GET", url, headers=headers)
        if response.status_code >= 300 :
            print(f"error code {response.status_code}, response text:", response.text)
            return {}
        response = response.json()
        
        with open(cached_path, 'w', encoding='utf8') as f :
            json.dump(response, f)
        return response
    
    def get_playlist(self, playlist_id):
        if playlist_id.startswith('spotify:playlist:'):
            playlist_id = playlist_id.replace('spotify:playlist:', '')
        return self.get(
            f'https://api.spotify.com/v1/playlists/{playlist_id}',
            headers = {
                'Authorization': f'Bearer {self.api_auth_token}'
            },
            cached_filename = f'playlist_{playlist_id}',
        )

    def get_all_tracks_from_playlist(self, playlist_id) :
        list_tracks = []

        for i in range(0,10000,100) :
            response = self.get(
                f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?offset={i}',
                headers = {
                    'Authorization': f'Bearer {self.api_auth_token}'
                },
                cached_filename=f'playlists_{playlist_id}_tracks_it{i}',
            )

            tracks = response['items']

            list_tracks.extend(tracks)
            if len(tracks) < 100 :
                return list_tracks
            
        print('get_all_tracks_from_playlist out of the loop')
        return list_tracks
    
    
    def get_all_my_liked_tracks(self) :
        list_tracks = []

        for i in range(0,10000,50) :
            response = self.get(
                f'https://api.spotify.com/v1/me/tracks?limit=50&offset={i}',
                headers = {
                    'Authorization': f'Bearer {self.api_auth_token}'
                },
                cached_filename=f'liked_tracks_it{i}',
            )

            tracks = response['items']

            list_tracks.extend(tracks)
            if len(tracks) < 50 :
                return list_tracks
            
        print('get_all_my_liked_tracks out of the loop')
        return list_tracks

    def get_track(self, track_id):
        if track_id.startswith('spotify:track:'):
            track_id = track_id.replace('spotify:track:', '')
        return self.get(
            f'https://api.spotify.com/v1/tracks/{track_id}',
            headers = {
                'Authorization': f'Bearer {self.api_auth_token}'
            },
            cached_filename = f'track_{track_id}',
        )
    
    def get_seed_to_playlist_from_track(self, track_id):
        if track_id.startswith('spotify:track:'):
            track_id = track_id.replace('spotify:track:', '')
        return self.get(
            f"https://spclient.wg.spotify.com/inspiredby-mix/v2/seed_to_playlist/spotify:track:{track_id}?response-format=json",
            headers = {
                'Authorization': f'Bearer {self.pathfinder_secrets.api_spclient_wg_spotify_bearer}'
            },
            cached_filename = f'seed_to_playlist_{track_id}',
        )
    
    def get_tracks_from_recommended_playlist(self, playlist_id) :
        
        if playlist_id.startswith('spotify:playlist:'):
            playlist_id = playlist_id.replace('spotify:playlist:', '')

        return self.post(
            "https://api-partner.spotify.com/pathfinder/v2/query",
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0',
                'Content-Type': 'application/json;charset=UTF-8',
                'Authorization': f'Bearer {self.pathfinder_secrets.api_spclient_wg_spotify_bearer}',
                'client-token': self.pathfinder_secrets.api_spclient_wg_spotify_client_token,
            },
            payload={
                "variables": {
                    "uri": f"spotify:playlist:{playlist_id}",
                    "offset": 0,
                    "limit": 50,
                },
                "operationName": "fetchPlaylistContents",
                "extensions": {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": self.pathfinder_secrets.api_spclient_wg_spotify_hash,
                    }
                }
            },
            cached_filename = f'tracks_of_recommended_playlist_{playlist_id}',
        )
        
    def get_recommended_tracks_for_playlist(self, playlist_id, exlude_track_from_playlist=[],exlude_liked_song_playlists=False):
        track_count = {}
        
        exlude_tracks_uri = set()
        for playlist_id in exlude_track_from_playlist + [playlist_id] :
            it_exclude_track_list = self.get_all_tracks_from_playlist(playlist_id)
            for track in it_exclude_track_list :
                exlude_tracks_uri.add(track['track']['uri'])
                
        if exlude_liked_song_playlists : 
            it_exclude_track_list = self.get_all_my_liked_tracks()
            for track in it_exclude_track_list :
                exlude_tracks_uri.add(track['track']['uri'])
            

        playlist_to_recommend = self.get_playlist(playlist_id)
        for track in playlist_to_recommend['tracks']['items']:
            track_id = track['track']['id']
            
            recommended_playlist = self.get_seed_to_playlist_from_track(track_id)
            recommended_playlist_id = recommended_playlist['mediaItems'][0]['uri']
            
            recommended_tracks = self.get_tracks_from_recommended_playlist(recommended_playlist_id)
            if not recommended_tracks:
                print(track_id, 'failed, skipped')
                continue
                
            for recommended_track_container in recommended_tracks['data']['playlistV2']['content']['items']:
                recommended_track = recommended_track_container['itemV2']['data']
                uri = recommended_track['uri']
                
                if uri in exlude_tracks_uri :
                    print(recommended_track['name'], 'skipped')
                    continue
                
                if uri in track_count :
                    track_count[uri]['nb_recommended'] += 1
                else :
                    track_count[uri] = {
                        'nb_recommended': 1,
                        'nb_views': int(recommended_track['playcount']),
                        'name': recommended_track['name'],
                    }
        
        return track_count

    def create_playlist(self, user_id, new_playlist_name, new_playlist_description) :
        
        return self.post(
            f'https://api.spotify.com/v1/users/{user_id}/playlists',
            headers = {
                'authorization': f'Bearer {self.api_auth_token}',
                'Content-Type': 'application/json',
            },
            payload={
                "name": new_playlist_name,
                "description": new_playlist_description,
                "public": False,
            },
        )

    def add_track_to_playlist(self, playlist_id, list_uri_track) :
        snapshot_results = []
        for i in range(0, len(list_uri_track), 100) :
            snapshot_results.append(self.post(
                f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',
                headers = {
                    'authorization': f'Bearer {self.api_auth_token}',
                    'Content-Type': 'application/json',
                },
                payload={
                    "uris": list_uri_track[i:i+100],
                },
            ))
        return snapshot_results

class PathfinderSecrets:
    def __init__(self,
        api_spclient_wg_spotify_bearer,
        api_spclient_wg_spotify_client_token,
        api_spclient_wg_spotify_hash,
    ) :
        self.api_spclient_wg_spotify_bearer = api_spclient_wg_spotify_bearer 
        self.api_spclient_wg_spotify_client_token = api_spclient_wg_spotify_client_token 
        self.api_spclient_wg_spotify_hash = api_spclient_wg_spotify_hash

    def __str__(self):
        return json.dumps({
            'api_spclient_wg_spotify_bearer': self.api_spclient_wg_spotify_bearer,
            'api_spclient_wg_spotify_client_token': self.api_spclient_wg_spotify_client_token,
            'api_spclient_wg_spotify_hash': self.api_spclient_wg_spotify_hash,
        })