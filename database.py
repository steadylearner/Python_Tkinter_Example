from tinydb import TinyDB, Query

db = TinyDB("db.json")
query = Query()
settings = db.table("settings")


# TODO
# Rename these
def read_settings(name):
    return settings.search(query.name == name)


def upsert_settings(name, details):
    settings.upsert({"name": name, "details": details}, query.name == name)


def read_input_text_language():
    return read_settings("form")[0]["details"]["input_text"]


def read_translated_text_language():
    return read_settings("form")[0]["details"]["translated_text"]


def read_voice_language():
    return read_settings("form")[0]["details"]["voice_language"]


def read_voice_gender():
    return read_settings("form")[0]["details"]["voice_gender"]
