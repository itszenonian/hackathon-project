import requests
import json
import os

# You must obtain a CertiK API key by contacting the CertiK Business Team.
# To keep it secure, it's recommended to load it from an environment variable.
API_KEY = os.environ.get("CERTIK_API_KEY", "YOUR_CERTIK_API_KEY_HERE")

BASE_URL = "https://partner.certik-skynet.com"

def get_security_score(chain, token_address):
    """
    Fetches the CertiK Skynet Security Score for a specific token.
    
    :param chain: The blockchain prefix (e.g., 'eth', 'bsc', 'polygon', 'solana')
    :param token_address: The smart contract address of the token
    :return: JSON response containing the security score data
    """
    # The API requires the address format to be 'chain:address'
    formatted_address = f"{chain}:{token_address}"
    endpoint = f"/v1/security-scores/{formatted_address}"
    url = f"{BASE_URL}{endpoint}"
    
    headers = {
        "X-Certik-Api-Key": API_KEY
    }
    
    print(f"Fetching CertiK Security Score for {formatted_address}...")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        return None

if __name__ == "__main__":
    # Example usage: fetching score for USDT on Ethereum
    chain_prefix = "eth"
    usdt_address = "0xdac17f958d2ee523a2206206994597c13d831ec7"
    
    data = get_security_score(chain_prefix, usdt_address)
    
    if data:
        print("\nSuccessfully retrieved data!")
        print(json.dumps(data, indent=2))
    else:
        print("\nFailed to retrieve data. Please ensure you have a valid API key set.")
