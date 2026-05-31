import urllib.request
import json
import os
import requests

# Set your CertiK API key here (or via environment variable)
CERTIK_API_KEY = os.environ.get("CERTIK_API_KEY", "YOUR_CERTIK_API_KEY")
CERTIK_BASE_URL = "https://partner.certik-skynet.com"

def get_certik_score(chain_prefix, address, project_name):
    """Attempt to call CertiK API for a specific project/token."""
    if not address or address.lower() == "none":
        return f"Skipped (No contract address found for {project_name})"
        
    formatted_address = f"{chain_prefix}:{address}"
    url = f"{CERTIK_BASE_URL}/v1/security-scores/{formatted_address}"
    
    headers = {
        "X-Certik-Api-Key": CERTIK_API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 401:
            return "Unauthorized (Valid API Key Required)"
        elif response.status_code == 404:
            return "Not Found in CertiK database"
        
        response.raise_for_status()
        data = response.json()
        return data.get("securityScore", "No Score Field")
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    print("Fetching protocol mappings from DeFiLlama to get token addresses...")
    protocols_url = "https://api.llama.fi/protocols"
    
    slug_to_address = {}
    try:
        req_proto = urllib.request.Request(protocols_url)
        with urllib.request.urlopen(req_proto) as res_proto:
            protocols_data = json.loads(res_proto.read())
            for p in protocols_data:
                slug_to_address[p.get('slug')] = p.get('address')
    except Exception as e:
        print("Failed to fetch protocol categories:", e)
        return

    # Let's take top 5 projects as an example to call the API
    sample_projects = [
        {"chain": "eth", "slug": "aave-v3"},
        {"chain": "eth", "slug": "morpho-blue"},
        {"chain": "bsc", "slug": "pancakeswap-amm-v3"},
        {"chain": "solana", "slug": "jupiter-lend"},
        {"chain": "sui", "slug": "navi-lending"}
    ]
    
    print("\n--- Calling CertiK Skynet API for DeFi Protocols ---\n")
    for proj in sample_projects:
        slug = proj["slug"]
        chain_prefix = proj["chain"]
        address = slug_to_address.get(slug)
        
        # Format the address by removing chain prefix if DefiLlama provides it (e.g. 'ethereum:0x...')
        clean_address = address
        if address and ':' in address:
            clean_address = address.split(':')[1]
            
        print(f"Project: {slug.upper()}")
        print(f"DefiLlama Address: {address}")
        
        score = get_certik_score(chain_prefix, clean_address, slug)
        print(f"CertiK Security Score: {score}")
        print("-" * 50)

if __name__ == "__main__":
    main()
