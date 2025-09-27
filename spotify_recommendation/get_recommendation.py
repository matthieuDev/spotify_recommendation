from spotify_recommendation.auth_token import get_auth_token_pkce
from spotify_recommendation.spotify_querier import spotify_querier
from spotify_recommendation.secrets_keys import api_spclient_wg_spotify_bearer

def get_recommendation(playlist_id_to_recommend, new_playlist_name, user_id, exlude_track_from_playlist=[]):
    auth_token = get_auth_token_pkce()
    querier = spotify_querier(auth_token, api_spclient_wg_spotify_bearer=api_spclient_wg_spotify_bearer)
    
    track_count = querier.get_recommended_tracks_for_playlist(
        playlist_id_to_recommend,
        exlude_track_from_playlist=exlude_track_from_playlist,
    )
    
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
        key=lambda x : x['nb_views'],
    ))
    
    playlist_to_recommend_name = querier.get_playlist(playlist_id_to_recommend)['name']
    created_playlists = querier.create_playlist(user_id, new_playlist_name,  f'Recommendation playlist from: "{playlist_to_recommend_name}"')
    
    list_uris = [track['uri'] for track in ordered_tracks]
    return querier.add_track_to_playlist(created_playlists['id'], list_uris)
