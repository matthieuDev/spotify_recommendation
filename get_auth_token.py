import requests, base64, string, random
import urllib.parse
from secrets_keys import api_client_id, api_client_secret, auth_code, redirect_uri

from hashlib import sha256
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException

import time
SELENIUM_TIMEOUT_SECOND = 60  

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

def get_auth_token_with_auth_code(api_client_id=api_client_id, api_client_secret=api_client_secret, auth_code=auth_code, redirect_uri=redirect_uri):
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

def generate_code_challenge_pkce(codeVerifier):
    sha = sha256(codeVerifier.encode('utf-8'))
    return base64.b64encode(sha.digest()).decode("utf8")\
        .replace('=', '')\
        .replace('+', '-')\
        .replace('/', '_')
        
def get_auth_code_pkce() :
    code_verifier  = generate_random_string(64)
    code_challenge = generate_code_challenge_pkce(code_verifier)

    query_params =  {
        'response_type': 'code',
        'client_id': api_client_id,
        'scope': 'user-read-private user-read-email',
        'code_challenge_method': 'S256',
        'code_challenge': code_challenge,
        'redirect_uri': redirect_uri,
    }
    driver = webdriver.Firefox()
    driver.get('https://accounts.spotify.com/authorize?' + urllib.parse.urlencode(query_params))
    
    for i in range(SELENIUM_TIMEOUT_SECOND) :
        time.sleep(1)
        try :
            if driver.current_url.startswith(redirect_uri.strip('/')):
                query = urllib.parse.urlparse(driver.current_url).query
                auth_codes = urllib.parse.parse_qs(query).get('code', [])
                driver.quit()
                if len(auth_codes) == 0 :
                    print("auth code not found")
                    return None
                return auth_codes[0], code_verifier
        except (NoSuchElementException, WebDriverException, AssertionError):
            print('The driver appears to be dead')
            try : 
                driver.quit()
            except :
                pass
            return None, code_verifier
    return None, code_verifier
    
def get_auth_token_pkce(api_client_id=api_client_id, redirect_uri=redirect_uri):
    auth_code, code_verifier = get_auth_code_pkce()
    if auth_code is None :
        print("could not get auth_code")        
        return
    
    res = requests.post(
        'https://accounts.spotify.com/api/token',
        headers={
             'Content-Type': 'application/x-www-form-urlencoded',
        },
        data={
            "client_id": api_client_id,
            "grant_type": 'authorization_code',
            "code": auth_code,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
        },
    )

    if res.status_code != 200:
        print('"error, response text:", ', res.text)
        return {} 
    jres = res.json()
    assert 'access_token' in jres
    return jres


if __name__ == '__main__' :
    jres = get_auth_token_pkce()
    print(jres)