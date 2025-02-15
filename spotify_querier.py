import requests, json, os, time
import urllib.parse

class spotify_querier :
    def __init__(self, api_auth_token, cache_folder = 'cache/') :
        self.api_auth_token =  api_auth_token
        self.cache_folder = cache_folder
        
        self.web_authorisation_token = None
        self.web_authorisation_token_expiration_date = None
        self.web_authorisation_token = self.get_web_authorisation_token()
        
        if not os.path.exists(self.cache_folder) :
            os.mkdir(self.cache_folder)
            
    def get_web_authorisation_token(self) :
        '''
        return type : {
            'clientId': 'XXXXXXXXX',
            'accessToken': 'XXXXXXXXX',
            'accessTokenExpirationTimestampMs': [timestamp in ms],
            'isAnonymous': True
        }
        '''
        if self.web_authorisation_token is None or \
            self.web_authorisation_token_expiration_date is None or\
            self.web_authorisation_token_expiration_date  > time.time():
            r_token = requests.get("https://open.spotify.com/get_access_token?reason=transport&productType=web_player").json()

            self.web_authorisation_token_expiration_date = r_token['accessTokenExpirationTimestampMs'] / 1000
            self.web_authorisation_token_expiration = r_token['accessToken'] 
        
        return self.web_authorisation_token_expiration

    def post(self, url, headers, payload, cached_filename):
        cached_path = f'{self.cache_folder}{cached_filename}.json'
        if os.path.exists(cached_path):
            with open(cached_path, encoding='utf8') as f :
                return json.load(f)
            
        response = requests.request("POST", url, headers=headers, data=payload).json()
        
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

        print(url)
        return self.get(
            url,
            headers = {
                'authorization': f'Bearer {self.get_web_authorisation_token()}'
            },
            cached_filename = f'tracks_of_recommended_playlist_{playlist_id}',
        )
