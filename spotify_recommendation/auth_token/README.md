
# Spotify Authentication Token

This repository provides three methods to obtain an authentication token for interacting with the Spotify API. Each method serves different use cases depending on the level of access required.

## Methods

### 1. `get_basic_auth_token`

This method uses the **Client Credentials Flow** to obtain a basic authentication token. It requires your `api_client_id` and `api_client_secret`.

- **Use Case**: Ideal for accessing public Spotify data (e.g., searching for tracks, albums, or artists). 
- **Limitations**: Does not support user-specific operations (e.g., creating playlists, accessing user data) because it does not allow scopes.

#### Usage:
```python
from get_basic_auth_token import get_basic_auth_token

token = get_basic_auth_token()
print(token)
```

---

### 2. `get_auth_token_with_auth_code`

This method uses the **Authorization Code Flow** to obtain an authentication token. It requires an `auth_code`, which is obtained by redirecting the user to Spotify's authorization URL.

- **Use Case**: Suitable for applications that need to perform user-specific operations (e.g., creating playlists, modifying user data).
- **Steps**:
  1. Generate the authorization URL using `generate_authorize_url()`.
  2. Redirect the user to this URL.
  3. After the user grants permission, Spotify will redirect back to your `redirect_uri` with an `auth_code`.
  4. Use this `auth_code` to obtain the token.

#### Usage:
```python
from get_auth_token_with_auth_code import generate_authorize_url, get_auth_token_with_auth_code

# Step 1: Generate the authorization URL
auth_url = generate_authorize_url()
print("Go to this URL and authorize:", auth_url)

# Step 2: After authorization, extract the `auth_code` from the redirect URL
auth_code = "YOUR_AUTH_CODE_FROM_REDIRECT_URL"

# Step 3: Get the token
token = get_auth_token_with_auth_code(auth_code)
print(token)
```

---

### 3. `get_auth_token_pkce`

This method uses the **Authorization Code Flow with PKCE (Proof Key for Code Exchange)** to obtain an authentication token. It is designed for applications that cannot securely store a client secret (e.g., mobile or desktop apps).

- **Use Case**: Ideal for applications where client secret storage is insecure or unavailable.
- **Features**: Automatically opens a browser window for user authentication and handles the token retrieval process.

#### Usage:
```python
from get_auth_token_pkce import get_auth_token_pkce

token = get_auth_token_pkce()
print(token)
```

---

## Common Setup

### Required Credentials
All methods require the following credentials, which should be stored in `secrets_keys.py`:
- `api_client_id`: Your Spotify API client ID.
- `api_client_secret`: Your Spotify API client secret (not required for PKCE).
- `redirect_uri`: The redirect URI registered in your Spotify Developer Dashboard.
- `auth_code`: The authorization code obtained after user redirection (only for `get_auth_token_with_auth_code`).

### Dependencies
Install the required dependencies using:
```bash
pip install requests selenium
```

### Caching (PKCE Method)
The PKCE method caches the token in a JSON file (`auth_token_pkce.json`) to avoid repeated authentication. The token is automatically refreshed when it expires.

---

## Notes
- Ensure that your `redirect_uri` is correctly configured in the Spotify Developer Dashboard.
- For the PKCE method, ensure that `selenium` and a compatible browser driver (e.g., Firefox) are installed.
- The `get_auth_token_with_auth_code` method requires manual extraction of the `auth_code` from the redirect URL.
