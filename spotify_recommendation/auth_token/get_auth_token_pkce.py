import requests, base64, string, random, os, json
import urllib.parse
from spotify_recommendation.secrets_keys import api_client_id, redirect_uri
from spotify_recommendation.path import cache_folder

from hashlib import sha256
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException

import time
SELENIUM_TIMEOUT_SECOND = 120  

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

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
        'scope': 'playlist-modify-private%20playlist-modify-public',
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
    
def get_auth_token_pkce(api_client_id=api_client_id, redirect_uri=redirect_uri, cache_folder = cache_folder):
    cache_auth_token_file = cache_folder + 'auth_token_pkce.json'
    if os.path.exists(cache_auth_token_file) :
        with open(cache_auth_token_file, encoding="utf8") as f :
            cache_auth_token = json.load(f)
        if 'access_token' in cache_auth_token and \
            'expires_at' in cache_auth_token and \
            cache_auth_token['expires_at'] > time.time() :
            return cache_auth_token['access_token']
        else :
            os.remove(cache_auth_token_file)
    
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
    assert 'expires_in' in jres
    
    #substract 5 seconds to be sure we do not get past the timeout
    jres['expires_at'] = time.time() + jres['expires_in'] - 5
    with open(cache_auth_token_file, 'w', encoding="utf8") as f :
        json.dump(jres, f)
    return jres['access_token']


if __name__ == '__main__' :
    access_token = get_auth_token_pkce()
    print(access_token)