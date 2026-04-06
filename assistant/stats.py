# assistant/absen_data.py

absen_data = {}

def add_absen(chat_id: int, date: str, user: str):
    if chat_id not in absen_data:
        absen_data[chat_id] = {}
    if date not in absen_data[chat_id]:
        absen_data[chat_id][date] = []
    if user not in absen_data[chat_id][date]:
        absen_data[chat_id][date].append(user)

def get_absen_list(chat_id: int, date: str):
    return absen_data.get(chat_id, {}).get(date, [])