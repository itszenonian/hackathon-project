import urllib.request
import json

url = "https://api.llama.fi/protocols"
req = urllib.request.Request(url)
try:
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read())
        print(f"Loaded {len(data)} protocols.")
        print("Sample mapping (slug -> category):")
        for i in range(5):
            print(f"- {data[i].get('slug')}: {data[i].get('category')}")
except Exception as e:
    print("Error:", e)
