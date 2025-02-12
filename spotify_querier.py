import requests, json, os

class spotify_querier :
    def __init__(self, api_auth_token, web_authorisation_token, cache_folder = 'cache/') :
        self.api_auth_token =  api_auth_token
        self.web_authorisation_token =  web_authorisation_token
        self.cache_folder = cache_folder
        
        if not os.path.exists(self.cache_folder) :
            os.mkdir(self.cache_folder)
            
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
            
        response = requests.request("GET", url, headers=headers).json()
        
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
                'Authorization': f'Bearer {self.web_authorisation_token}'
            },
            cached_filename = f'seed_to_playlist_{track_id}',
        )