import aiohttp
import asyncio
from typing import Dict, Optional
import ipinfo

# Cache for storing IP locations
ip_location_cache: Dict[str, Optional[dict]] = {}

BASE_URL = "http://localhost:8000"
TIMEOUT = 5  # Reduced timeout for quicker detection

# Initialize ipinfo handler
IPINFO_TOKEN = "9a2815cabdac3d"  # Replace with your token
handler = ipinfo.getHandler(IPINFO_TOKEN)

def set_base_url(url):
    """
    Set the base URL for the API requests.

    Args:
        url (str): The base URL to set.
    """
    global BASE_URL
    if not url.startswith("http://") and not url.startswith("https://"):
        BASE_URL = f"http://{url}"
    else:
        BASE_URL = url

async def fetch_data(session, endpoint):
    """
    Fetch data from the specified API endpoint.

    Args:
        session (aiohttp.ClientSession): The aiohttp client session.
        endpoint (str): The API endpoint to fetch data from.

    Returns:
        dict or str: The fetched data or status.
    """
    try:
        async with session.get(f"{BASE_URL}{endpoint}", timeout=TIMEOUT) as response:
            if endpoint == "/health":
                return "Reachable" if response.status == 200 else "Not Reachable"
            if response.status == 200:
                return await response.json()
            else:
                return {} if endpoint != "/metrics/v1/log/logs/recent" else []
    except asyncio.TimeoutError:
        return (
            "Not Reachable"
            if endpoint == "/health"
            else {} if endpoint != "/metrics/v1/log/logs/recent" else []
        )
    except Exception:
        return (
            "Not Reachable"
            if endpoint == "/health"
            else {} if endpoint != "/metrics/v1/log/logs/recent" else []
        )

async def fetch_all_data():
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_data(session, "/health"),
            fetch_data(session, "/metrics/v1/cpu/usage"),
            fetch_data(session, "/metrics/v1/cpu/core"),
            fetch_data(session, "/metrics/v1/ram/usage"),
            fetch_data(session, "/metrics/v1/disk/usage"),
            fetch_data(session, "/metrics/v1/log/logs"),
            fetch_data(session, "/metrics/v1/log/logs/recent"),
            fetch_data(session, "/metrics/v1/users/connected"),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Add default values for empty responses
        cpu_core_info = results[2] if not isinstance(results[2], Exception) else {}
        if not cpu_core_info.get('processor_name'):
            cpu_core_info['processor_name'] = 'Unavailable'
        if not cpu_core_info.get('number_of_cores'):
            cpu_core_info['number_of_cores'] = 'Unavailable'
        if not cpu_core_info.get('frequency'):
            cpu_core_info['frequency'] = 'Unavailable'

        last_connected = results[7] if not isinstance(results[7], Exception) else 'Unavailable'
        if not last_connected or last_connected == 'N/A':
            last_connected = 'Unavailable'

        return {
            "health_status": results[0] if not isinstance(results[0], Exception) else "Not Reachable",
            "cpu_data": results[1] if not isinstance(results[1], Exception) else [],
            "cpu_core_info": cpu_core_info,
            "ram_data": results[3] if not isinstance(results[3], Exception) else {},
            "disk_data": results[4] if not isinstance(results[4], Exception) else {},
            "log_data": results[5] if not isinstance(results[5], Exception) else {},
            "recent_logs": results[6] if not isinstance(results[6], Exception) else [],
            "last_connected": last_connected,
        }

async def fetch_geolocation(ip: str) -> Optional[dict]:
    """
    Fetch the geolocation for the given IP address.

    Args:
        ip (str): The IP address to fetch geolocation for.

    Returns:
        dict or None: Dictionary containing latitude and longitude, or None if not found.
    """
    # Return cached result if available
    if ip in ip_location_cache:
        return ip_location_cache[ip]

    # For private IP addresses, return None immediately
    if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172.16."):
        ip_location_cache[ip] = None
        return None

    try:
        details = handler.getDetails(ip)
        if details.latitude and details.longitude:
            result = {
                "latitude": float(details.latitude),
                "longitude": float(details.longitude),
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
