from spotify_recommendation.auth_token import get_auth_token_pkce
import requests

def get_all_categories(auth_token):
    url = 'https://api.spotify.com/v1/browse/categories?limit=50'
    res = []

    for _ in range(10):
        if not url :
            break
        req = requests.get(url, headers= {
            "Authorization": f"Bearer {auth_token}"
        })
        assert req.status_code == 200

        res_categories = req.json()['categories']
        for category in res_categories['items'] :
            res.append({"id" : category['id'], 'name' : category['name']})

        url = res_categories['next']
        
    return res

if __name__ == '__main__':
    auth_token = get_auth_token_pkce()
    all_categories = get_all_categories(auth_token)
    print(all_categories)