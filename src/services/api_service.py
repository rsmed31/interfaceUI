# src/services/api_service.py
import aiohttp
import asyncio
from typing import Dict, Optional
import ipinfo

# Cache for storing IP locations
ip_location_cache: Dict[str, Optional[dict]] = {}

BASE_URL = "http://localhost:8000"
TIMEOUT = 2  # Reduced timeout for quicker detection

# Initialize ipinfo handler
IPINFO_TOKEN = '9a2815cabdac3d'  # Replace with your token
handler = ipinfo.getHandler(IPINFO_TOKEN)

def set_base_url(url):
    global BASE_URL
    if not url.startswith('http://') and not url.startswith('https://'):
        BASE_URL = f"http://{url}"
    else:
        BASE_URL = url

async def fetch_health_status(session):
    try:
        async with session.get(f"{BASE_URL}/health", timeout=TIMEOUT) as response:
            if response.status == 200:
                return "Reachable"
            else:
                return "Not Reachable"
    except asyncio.TimeoutError:
        return "Not Reachable"
    except Exception:
        return "Not Reachable"

async def fetch_cpu_data(session):
    try:
        async with session.get(f"{BASE_URL}/metrics/v1/cpu/usage", timeout=TIMEOUT) as response:
            if response.status == 200:
                return await response.json()
            else:
                return []
    except asyncio.TimeoutError:
        return []
    except Exception:
        return []

async def fetch_cpu_core_info(session):
    try:
        async with session.get(f"{BASE_URL}/metrics/v1/cpu/core", timeout=TIMEOUT) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {}
    except asyncio.TimeoutError:
        return {}
    except Exception:
        return {}

async def fetch_ram_data(session):
    try:
        async with session.get(f"{BASE_URL}/metrics/v1/ram/usage", timeout=TIMEOUT) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {}
    except asyncio.TimeoutError:
        return {}
    except Exception:
        return {}

async def fetch_disk_data(session):
    try:
        async with session.get(f"{BASE_URL}/metrics/v1/disk/usage", timeout=TIMEOUT) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {}
    except asyncio.TimeoutError:
        return {}
    except Exception:
        return {}

async def fetch_recent_logs(session):
    try:
        async with session.get(f"{BASE_URL}/metrics/v1/log/logs/recent", timeout=TIMEOUT) as response:
            if response.status == 200:
                return await response.json()
            else:
                return []
    except asyncio.TimeoutError:
        return []
    except Exception:
        return []

async def fetch_all_data():
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(
            fetch_health_status(session),
            fetch_cpu_data(session),
            fetch_cpu_core_info(session),
            fetch_ram_data(session),
            fetch_disk_data(session),
            fetch_log_data(session),
            fetch_recent_logs(session),
            return_exceptions=True
        )
        return {
            "health_status": results[0],
            "cpu_data": results[1],
            "cpu_core_info": results[2],
            "ram_data": results[3],
            "disk_data": results[4],
            "log_data": results[5],
            "recent_logs": results[6]
        }

async def fetch_log_data(session):
    try:
        async with session.get(f"{BASE_URL}/metrics/v1/log/logs", timeout=TIMEOUT) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {}
    except asyncio.TimeoutError:
        return {}
    except Exception:
        return {}
async def fetch_connected_users(session):
    try:
        async with session.get(f"{BASE_URL}/metrics/v1/users/connected", timeout=TIMEOUT) as response:
            if response.status == 200:
                data = await response.json()
                return data[0] if data else "No users"
            return "Not available"
    except Exception:
        return "Not available"

async def fetch_all_data():
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_health_status(session),
            fetch_cpu_data(session),
            fetch_cpu_core_info(session),
            fetch_ram_data(session),
            fetch_disk_data(session),
            fetch_log_data(session),
            fetch_recent_logs(session),
            fetch_connected_users(session)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "health_status": results[0] if not isinstance(results[0], Exception) else "Not Reachable",
            "cpu_data": results[1] if not isinstance(results[1], Exception) else [],
            "cpu_core_info": results[2] if not isinstance(results[2], Exception) else {},
            "ram_data": results[3] if not isinstance(results[3], Exception) else {},
            "disk_data": results[4] if not isinstance(results[4], Exception) else {},
            "log_data": results[5] if not isinstance(results[5], Exception) else {},
            "recent_logs": results[6] if not isinstance(results[6], Exception) else [],
            "last_connected": results[7] if not isinstance(results[7], Exception) else "N/A"
        }

async def fetch_geolocation(ip: str) -> Optional[dict]:
    # Return cached result if available
    if ip in ip_location_cache:
        return ip_location_cache[ip]

    # For private IP addresses, return None immediately
    if (ip.startswith('192.168.') or 
        ip.startswith('10.') or 
        ip.startswith('172.16.')):
        ip_location_cache[ip] = None
        return None

    try:
        details = handler.getDetails(ip)
        if details.latitude and details.longitude:
            result = {
                "latitude": float(details.latitude),
                "longitude": float(details.longitude)
            }
            ip_location_cache[ip] = result
            print(f"Geolocation for IP {ip}: {result}")
            return result
        ip_location_cache[ip] = None
        print(f"No geolocation found for IP {ip}")
        return None
    except Exception as e:
        print(f"Error fetching geolocation for IP {ip}: {e}")
        ip_location_cache[ip] = None
        return None
