
from spotify_recommendation.get_recommendation import get_recommendation
import argparse

if __name__ == '__main__' :
    parser = argparse.ArgumentParser(
        prog='Recommendation playlist',
        description='Recommend a playlist base on another playlist to find tracks with few views in the sea of proposition.',
    )
    parser.add_argument('--playlist_id', help="Id of the playlist to use as base to recommend")
    parser.add_argument('--new_playlist_name', help="Name of the new playlist")
    parser.add_argument('--user_id', help="Your user id")
    parser.add_argument('--exlude_track_from_playlist', help="List of id of the playlists from which no tracks should be in the result")
    
    args = parser.parse_args()

    print(get_recommendation(
        args.playlist_id,
        args.new_playlist_name,
        args.user_id,
        args.exlude_track_from_playlist.split(','),
    ))
    