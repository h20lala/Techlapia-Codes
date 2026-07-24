import urllib.request
import json
import sys

SUPABASE_URL = "https://qekehslduothjlhxzmbw.supabase.co"
SUPABASE_KEY = "sb_publishable_flpDIdOuSh5DNedl9wqjhw_qOfz1DZy"

try:
    url = f"{SUPABASE_URL}/rest/v1/logs?select=*&limit=5"
    req = urllib.request.Request(
        url,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
    )
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print(json.dumps(data, indent=2))
except Exception as e:
    print("Error:", e)
