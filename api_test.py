import base64
import time
import aiohttp
import asyncio
from typing import Any, Dict, List, Optional, Union

PRG_FILE_NAME = "birthday.prg"
API_BASE = "http://192.168.1.100"

async def reset_machine_soft() -> dict:
    try:
        result = await make_request("PUT", "machine:reset")
    except Exception as e:
        result = {"errors": [f"Error during API call for reset"]}
    return result

async def run_prg_binary(prg_data_binary: bytes) -> dict:
    base64_str = base64.b64encode(prg_data_binary).decode().strip()
    try:
        prg_data = base64.b64decode(base64_str, validate=True)
    except Exception as e:
        print(f"Error during base64 decoding")

    url = f"{API_BASE}/v1/runners:run_prg"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, 
                data=prg_data, 
                headers={'Content-Type': 'application/octet-stream'},
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    try:
                        response_data = await response.json()
                    except:
                        response_data = {"message": "Program started"}
                    result = {
                        "success": True,
                        "message": f"Program sent and started successfully via API.",
                        "size_bytes": len(prg_data),
                        "response": response_data
                    }
                else:
                    body = await response.text()
                    result = {"errors": [f"Failed to run PRG: HTTP {response.status}: {body}"]}    
        return result
    except Exception as e:
        return {"errors": [f"Error during API call to run PRG"]}

async def make_request(method: str, endpoint: str, params: Optional[Dict] = None, 
                        data: Optional[Union[Dict, bytes]] = None) -> Dict[str, Any]:
    """Make HTTP request to Ultimate API"""
    if not API_BASE:
        return {"errors": ["No C64 host configured. "]}
    url = f"{API_BASE}/v1/{endpoint}"

    # Create a fresh session for each request to avoid connection issues
    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, params=params, json=data, timeout=aiohttp.ClientTimeout(total=5)) as response:
            if response.status == 204:
                return {"ok": True}
            if response.status == 200:
                content_type = response.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    return await response.json()
                raw = await response.read()
                try:
                    return {"data": raw.hex()}
                except Exception:
                    return {"data": raw.decode(errors="replace")}
            body = await response.text()
            return {"errors": [f"HTTP {response.status}: {body}"]}

    
if __name__ == "__main__":

    # Load a PRG binary file
    with open(PRG_FILE_NAME, "rb") as f:
        file_content = f.read()

    # Test 1: reset the machine
    result = asyncio.run(reset_machine_soft())
    print(result)

    # Test 2: run a PRG binary
    time.sleep(5)  # wait a bit before next test
    result = asyncio.run(run_prg_binary(file_content))
    print(result)   

    # Test 3: reset the machine again
    time.sleep(5)  # wait a bit before next test
    result = asyncio.run(reset_machine_soft())
    print(result)

    # Test 4: run a PRG binary again
    time.sleep(5)  # wait a bit before next test
    result = asyncio.run(run_prg_binary(file_content))
    print(result)   