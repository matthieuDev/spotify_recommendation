import requests, json, os, time
import urllib.parse
from .path import cache_folder

class spotify_querier :
    def __init__(self, api_auth_token, cache_folder = cache_folder) :
        self.api_auth_token =  api_auth_token
        self.cache_folder = cache_folder
        
        self.web_authorisation_token = None
        self.web_authorisation_token_expiration_date = None
        self.web_authorisation_token = self.get_web_authorisation_token()
        
        if not os.path.exists(self.cache_folder) :
            os.mkdir(self.cache_folder)
            
    def get_web_authorisation_token(self) :
        '''
        requests return type : {
            'clientId': 'XXXXXXXXX',
            'accessToken': 'XXXXXXXXX',
            'accessTokenExpirationTimestampMs': [timestamp in ms],
            'isAnonymous': True
        }
        '''
        if self.web_authorisation_token is None or \
            self.web_authorisation_token_expiration_date is None or\
            self.web_authorisation_token_expiration_date < time.time():
            response = requests.get("https://open.spotify.com/get_access_token?reason=transport&productType=web_player")
            if response.status_code != 200 :
                print("error, response text:", response.text)
                return {}
            r_token = response.json()

            self.web_authorisation_token_expiration_date = r_token['accessTokenExpirationTimestampMs'] / 1000
            self.web_authorisation_token_expiration = r_token['accessToken'] 
        
        return self.web_authorisation_token_expiration

    def post(self, url, headers, payload, cached_filename=None):
        if not cached_filename is None and os.path.exists(cached_path):
            cached_path = f'{self.cache_folder}{cached_filename}.json'
            with open(cached_path, encoding='utf8') as f :
                return json.load(f)
            
        response = requests.request("POST", url, headers=headers, data=json.dumps(payload)).json()
        
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
        if response.status_code != 200 :
            print("error, response text:", response.text)
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
                'Authorization': f'Bearer {self.get_web_authorisation_token()}'
            },
            cached_filename = f'seed_to_playlist_{track_id}',
        )
    
    def get_tracks_from_recommended_playlist(self, playlist_id) :
        
        if playlist_id.startswith('spotify:playlist:'):
            playlist_id = playlist_id.replace('spotify:playlist:', '')
            
        extensions_param = urllib.parse.quote('{"persistedQuery":{"version":1,"sha256Hash":"5372ff05b73f2a1c21b392a238c462f6d2a1391200a47ddac51984e0d3fcd65b"}')
        variables_params = urllib.parse.quote(json.dumps({"uri":f"spotify:playlist:{playlist_id}","offset":0,"limit":100}).replace(' ', ''))
        url = f"https://api-partner.spotify.com/pathfinder/v1/query?operationName=fetchPlaylistContentsWithGatedEntityRelations&variables={variables_params}&extensions={extensions_param}%7D"

        return self.get(
            url,
            headers = {
                'authorization': f'Bearer {self.get_web_authorisation_token()}'
            },
            cached_filename = f'tracks_of_recommended_playlist_{playlist_id}',
        )
        
    def get_recommended_tracks_for_playlist(self, playlist_id):
        track_count = {}

        playlist_to_recommend = self.get_playlist(playlist_id)
        for track in playlist_to_recommend['tracks']['items']:
            track_id = track['track']['id']
            
            recommended_playlist = self.get_seed_to_playlist_from_track(track_id)
            recommended_playlist_id = recommended_playlist['mediaItems'][0]['uri']
            
            recommended_tracks = self.get_tracks_from_recommended_playlist(recommended_playlist_id)
            
            for recommended_track_container in recommended_tracks['data']['playlistV2']['content']['items']:
                recommended_track = recommended_track_container['itemV2']['data']
                uri = recommended_track['uri']
                if uri in track_count :
                    track_count[uri]['nb_recommended'] += 1
                else :
                    track_count[uri] = {
                        'nb_recommended': 1,
                        'nb_views': int(recommended_track['playcount']),
                        'name': recommended_track['name'],
                    }
        
        return track_count

    def create_playlist(self, user_id, new_playlist_name, new_playlist_recommendation) :
        
        return self.post(
            f'https://api.spotify.com/v1/users/{user_id}/playlists',
            headers = {
                'authorization': f'Bearer {self.api_auth_token}',
                'Content-Type': 'application/json',
            },
            payload={
                "name": new_playlist_name,
                "description": new_playlist_recommendation,
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
        
        