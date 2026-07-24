import urllib.request
import json

SUPABASE_URL = "https://qekehslduothjlhxzmbw.supabase.co"
SUPABASE_KEY = "sb_publishable_flpDIdOuSh5DNedl9wqjhw_qOfz1DZy"

try:
    url = f"{SUPABASE_URL}/rest/v1/?apikey={SUPABASE_KEY}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        tables = [path.strip('/') for path in data.get('paths', {}).keys() if not path.startswith('/rpc')]
        print("Tables in Supabase:", tables)
except Exception as e:
    print("Error:", e)
