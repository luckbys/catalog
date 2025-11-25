import requests
import json
import time

# Configuration from evolution-api-config.js
EVOLUTION_API_URL = 'https://chatbot-evolution-api.zv7gpn.easypanel.host'
EVOLUTION_API_KEY = '429683C4C977415CAAFCCE10F7D57E11'

LOCAL_API_URL = 'http://localhost:8000'

def fetch_evolution_instances():
    print(f"Fetching instances from {EVOLUTION_API_URL}...")
    headers = {
        'apikey': EVOLUTION_API_KEY,
        'x-api-key': EVOLUTION_API_KEY
    }
    
    try:
        # Remove trailing slash
        url = EVOLUTION_API_URL.rstrip('/')
        
        response = requests.get(f"{url}/instance/fetchInstances", headers=headers)
        
        if response.status_code != 200:
            print(f"Error fetching instances: {response.status_code} - {response.text}")
            return []
            
        data = response.json()
        # Handle both array and object wrapper formats
        instances = data if isinstance(data, list) else data.get('instances', [])
        
        print(f"Found {len(instances)} instances.")
        return instances
        
    except Exception as e:
        print(f"Exception fetching instances: {e}")
        return []

def update_local_backend(instances):
    print("Updating local backend...")
    
    formatted_instances = []
    
    for inst in instances:
        # Extract instance name safely
        name = inst.get('instance', {}).get('instanceName') or inst.get('instanceName') or inst.get('name')
        
        if not name:
            continue
            
        formatted_instances.append({
            "id": f"sync-{int(time.time())}-{name}",
            "instanceName": name,
            "apiUrl": EVOLUTION_API_URL,
            "apiKey": EVOLUTION_API_KEY,
            "sellerPhone": "" # Optional
        })
    
    if not formatted_instances:
        print("No valid instances to sync.")
        return

    try:
        response = requests.post(f"{LOCAL_API_URL}/api/evolution/instances", json=formatted_instances)
        
        if response.status_code == 200:
            print("Successfully synced instances to local backend!")
        else:
            print(f"Error updating local backend: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Exception updating local backend: {e}")

if __name__ == "__main__":
    instances = fetch_evolution_instances()
    if instances:
        update_local_backend(instances)
