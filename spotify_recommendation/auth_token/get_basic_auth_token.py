
import requests, base64
from spotify_recommendation.secrets_keys import api_client_id, api_client_secret

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
