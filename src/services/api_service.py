# src/services/api_service.py
import aiohttp
import asyncio

BASE_URL = "http://localhost:8000"
TIMEOUT = 2  # Reduced timeout for quicker detection

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

async def fetch_all_data():
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(
            fetch_health_status(session),
            fetch_cpu_data(session),
            fetch_cpu_core_info(session),
            fetch_ram_data(session),
            fetch_disk_data(session),
            fetch_log_data(session),
            return_exceptions=True
        )
        return {
            "health_status": results[0],
            "cpu_data": results[1],
            "cpu_core_info": results[2],
            "ram_data": results[3],
            "disk_data": results[4],
            "log_data": results[5]
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