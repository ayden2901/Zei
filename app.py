import asyncio
import socket

import uvicorn
from fastapi import FastAPI

from Navy import bot, logger
from Navy.__main__ import main, stop_main

app = FastAPI()


@app.get("/")
def hello():
    return {"message": "Userbot API running"}


@app.post("/start")
async def start_userbot():
    """Mulai userbot"""
    try:
        asyncio.create_task(main())
        return {"status": "Userbot started successfully"}
    except Exception as e:
        logger.error(f"Failed to start userbot: {e}")
        return {"error": str(e)}


@app.post("/stop")
async def stop_userbot():
    """Hentikan userbot"""
    try:
        await stop_main()
        return {"status": "Userbot stopped successfully"}
    except Exception as e:
        logger.error(f"Failed to stop userbot: {e}")
        return {"error": str(e)}


@app.get("/status")
async def status_userbot():
    """Cek status userbot"""
    try:
        if bot.is_connected:
            return {"status": "Userbot is running"}
        else:
            return {"status": "Userbot is not running"}
    except Exception as e:
        return {"error": str(e)}


def find_available_port(start_port=7860, max_port=7960):
    """Cari port yang tersedia"""
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", port)) != 0:
                return port
    return None  # Jika tidak ada port yang tersedia


if __name__ == "__main__":
    port = find_available_port()
    if port:
        print(f"Port {port} is available. Starting server...")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        print("No available ports found in the range.")