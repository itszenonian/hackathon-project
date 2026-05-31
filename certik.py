import urllib.request
import requests
import json
import os

API_KEY = os.environ.get("CERTIK_API_KEY", "YOUR_CERTIK_API_KEY")
BASE_URL = "https://partner.certik-skynet.com"


def get_security_score(chain, address, project_name=""):
    if not address or address.lower() == "none":
        return None, f"Skipped (no address for {project_name})"

    formatted = f"{chain}:{address}"
    url = f"{BASE_URL}/v1/security-scores/{formatted}"
    headers = {"X-Certik-Api-Key": API_KEY}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 401:
            return None, "Unauthorized (valid API key required)"
        if response.status_code == 404:
            return None, "Not found in CertiK database"
        response.raise_for_status()
        data = response.json()
        return data, data.get("securityScore")
    except requests.exceptions.RequestException as e:
        return None, f"Error: {e}"


def fetch_scores_for_protocols(projects):
    print("Fetching protocol addresses from DeFiLlama...")
    try:
        req = urllib.request.Request("https://api.llama.fi/protocols")
        with urllib.request.urlopen(req) as res:
            protocols = json.loads(res.read())
    except Exception as e:
        print(f"Failed to fetch DeFiLlama protocols: {e}")
        return

    slug_to_address = {p.get("slug"): p.get("address") for p in protocols}

    print("\n--- CertiK Skynet Security Scores ---\n")
    for proj in projects:
        slug = proj["slug"]
        chain = proj["chain"]
        raw_address = slug_to_address.get(slug)

        clean_address = raw_address.split(":")[1] if raw_address and ":" in raw_address else raw_address

        print(f"Project : {slug.upper()}")
        print(f"Address : {raw_address}")

        _, score = get_security_score(chain, clean_address, slug)
        print(f"Score   : {score}")
        print("-" * 50)


if __name__ == "__main__":
    sample_projects = [
        {"chain": "eth",    "slug": "aave-v3"},
        {"chain": "eth",    "slug": "morpho-blue"},
        {"chain": "bsc",    "slug": "pancakeswap-amm-v3"},
        {"chain": "solana", "slug": "jupiter-lend"},
        {"chain": "sui",    "slug": "navi-lending"},
    ]
    fetch_scores_for_protocols(sample_projects)
