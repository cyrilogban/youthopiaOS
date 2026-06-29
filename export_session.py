from pyrogram import Client

api_id = 30549075
api_hash = "0d28ccd2a22881769179cf89fbe5696d"

app = Client("susy", api_id=api_id, api_hash=api_hash)
app.start()
print("\nYOUR STRING SESSION:\n" + app.export_session_string() + "\n")
app.stop()
