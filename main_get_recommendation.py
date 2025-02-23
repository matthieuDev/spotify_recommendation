
from spotify_recommendation.get_recommendation import get_recommendation

if __name__ == '__main__' :
    print(get_recommendation(
        '<playlist_id_to_recommend>',
        '<new_playlist_name>',
        '<user_id>',
    ))
    