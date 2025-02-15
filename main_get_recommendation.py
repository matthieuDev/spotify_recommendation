import requests, json, os, time
from get_auth_token import get_auth_token
from spotify_querier import spotify_querier

def get_recommendation(playlist_id_to_recommend, new_playlist_name, user_id):
    auth_token = get_auth_token()
    querier = spotify_querier(auth_token)
    
    track_count = querier.get_recommended_tracks_for_playlist(playlist_id_to_recommend)
    
    ordered_tracks = [
        {
            'uri': uri,
            'nb_recommended': info['nb_recommended'],
            'nb_views': info['nb_views'],
            'name': info['name'],
        }
        for uri, info in track_count.items()
    ]
    ordered_tracks = list(sorted(
        ordered_tracks,
        key=lambda x : (x['nb_recommended'], -x['nb_views']),
        reverse=True,
    ))
    
    playlist_to_recommend_name = querier.get_playlist(playlist_id_to_recommend)['name']
    created_playlists = querier.create_playlist(user_id, new_playlist_name,  f'Recommendation playlist from: "{playlist_to_recommend_name}"')
    