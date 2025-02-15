import requests, base64, string, random
import urllib.parse
from secrets_keys import api_client_id, api_client_secret, auth_code, redirect_uri


def get_basic_auth_token(api_client_id=api_client_id, api_client_secret=api_client_secret):
    base64_auth = base64.b64encode(f'{api_client_id}:{api_client_secret}'.encode("ascii")).decode('ascii')
    res = requests.post(
        'https://accounts.spotify.com/api/token',
        headers={
            'Authorization': f'Basic {base64_auth}',
        },
        data={
            "grant_type": 'client_credentials'
        },
    )
    assert res.status_code == 200
    jres = res.json()
    assert 'access_token' in jres
    return jres['access_token']

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_authorize_url():
    state = generate_random_string(16)
    scope = 'playlist-modify-private%20playlist-modify-public'

    query_params = {
        'response_type': 'code',
        'client_id': api_client_id,
        'scope': scope,
        'redirect_uri': 'http://localhost:8888/callback/',
        'state': state
    }

    return 'https://accounts.spotify.com/authorize?' + urllib.parse.urlencode(query_params)

def get_auth_token(api_client_id=api_client_id, api_client_secret=api_client_secret, auth_code=auth_code, redirect_uri=redirect_uri):
    base64_auth = base64.b64encode(f'{api_client_id}:{api_client_secret}'.encode("ascii")).decode('ascii')
    res = requests.post(
        'https://accounts.spotify.com/api/token',
        headers={
            'Authorization': f'Basic {base64_auth}',
        },
        data={
            "grant_type": 'authorization_code',
            'code': auth_code,
            'redirect_uri': redirect_uri,
        },
    )

    if res.status_code != 200:
        print('"error, response text:", ', res.text)
        return {} 
    jres = res.json()
    assert 'access_token' in jres
    return jres['access_token']
