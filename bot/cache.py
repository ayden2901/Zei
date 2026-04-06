import os
import json
import pytz
from datetime import datetime
from uuid import uuid4
import asyncio
import random
from Navy.database import dB, DB_PATH
import sqlite3
from Navy.helpers import CMD, ButtonUtils, Emoji, Tools, task
import aiosqlite
from pyrogram import Client, filters
from pyrogram.enums import ChatType, ParseMode
from config import BLACKLIST_GCAST
import logging


absen_data = {}
inline_mapping = {}
active_absen_messages = {}
inline_msg_cache = {}
active_absen_inline_ids = {}
absen_owners = {}
DATA_DIR = "data/absensi"
os.makedirs(DATA_DIR, exist_ok=True)

INLINE_MAP_FILE = f"{DATA_DIR}/inline_map.json"

def save_inline_mapping_file():
    with open(INLINE_MAP_FILE, "w") as f:
        json.dump(inline_mapping, f)

def load_inline_mapping_file():
    global inline_mapping
    if os.path.exists(INLINE_MAP_FILE):
        with open(INLINE_MAP_FILE, "r") as f:
            inline_mapping = json.load(f)

# Waktu hari ini (format lokal Indonesia)
def get_today():
    return datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%Y-%m-%d")

# ==================== DATA ABSEN (per inline_id) ====================

def get_absen_file_by_inline(inline_id: str) -> str:
    return f"{DATA_DIR}/group_{inline_id}_{get_today()}.json"

def load_absen_file(inline_id: str) -> dict:
    path = get_absen_file_by_inline(inline_id)
    return json.load(open(path)) if os.path.exists(path) else {}

def save_absen_file(inline_id: str, data: dict):
    path = get_absen_file_by_inline(inline_id)
    with open(path, "w") as f:
        json.dump(data, f)

# ==================== MAPPING INLINE_ID <-> MSG_ID ====================

def save_inline_mapping(chat_id: int, inline_id: str, msg_id: int):
    inline_mapping[inline_id] = (chat_id, msg_id)
    save_inline_mapping_file()  # Tambahkan ini

def get_inline_mapping(inline_id: str):
    return inline_mapping.get(inline_id)

# ==================== SIMPAN METADATA KE FILE (opsional) ====================

def save_inline_meta_file(chat_id: int, inline_id: str):
    path = f"{DATA_DIR}/{chat_id}_{get_today()}_meta.json"
    with open(path, "w") as f:
        json.dump({"inline_message_id": inline_id}, f)

def load_inline_meta_file(chat_id: int):
    path = f"{DATA_DIR}/{chat_id}_{get_today()}_meta.json"
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            return json.load(f).get("inline_message_id")
    except:
        return None


async def get_autoread_status():
    db = await get.dB()
    result = db.execute("SELECT status FROM autoread WHERE user_id = ?", (0,))
    row = result.fetchone()
    return row[0] if row else "OFF"

async def set_autoread_status(status: str):
    db = await get.dB()
    db.execute(
        "INSERT OR REPLACE INTO autoread (user_id, status) VALUES (?, ?)",
        (0, status)
    )
    db.commit()
