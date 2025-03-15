import pymongo
from datetime import datetime

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client.get_database("practise2")
meter_col = db.get_collection("meter")
history_col = db.get_collection("energy_history")
config_col = db.get_collection("config")


def is_valid_iso8601(timestamp: str) -> bool:
    try:
        datetime.fromisoformat(timestamp)
        return True
    except ValueError:
        return False


def create_meter(_id: str, last_day: float = 0, last_night: float = 0):
    meter = {
        "_id": _id,
        "last_day": last_day,
        "last_night": last_night,
        "updated_at": "never"
    }
    meter_col.insert_one(meter)
    return meter


def del_meter_by_id(_id: str):
    meter_col.delete_one({"_id": _id})


def get_meter_by_id(_id: str):
    meter = meter_col.find_one({"_id": _id})
    if not isinstance(meter, dict):
        raise ValueError("No such meter id")
    return meter


def get_config():
    config = config_col.find_one({"_id": "tariffs"})
    if not isinstance(config, dict):
        raise ValueError("Config not found!")
    return config


def get_history():
    history = list(history_col.find({}))
    if not history:
        raise ValueError("History not found!")
    return history


def add_usage_by_id(_id: str, usage_day: float, usage_night: float, date_iso8601: datetime.date = ""):
    if not is_valid_iso8601(date_iso8601):
        date_iso8601 = datetime.utcnow().isoformat()

    if (usage_day < 0) or (usage_night < 0):
        raise ValueError("Usage must be > 0")

    meter_check = meter_col.find_one({"_id": _id})
    if not isinstance(meter_check, dict):
        raise ValueError("Meter not found!")

    meter_col.update_one(
        {"_id": _id},
        {
            "$inc": {"last_day": usage_day, "last_night": usage_night},
            "$set": {"updated_at": date_iso8601}
        }
    )


def write_to_history(data: dict):
    required_keys = {
        "meter_id": str,
        "prev_day": (int, float),
        "prev_night": (int, float),
        "used_day": (int, float),
        "used_night": (int, float),
        "corrected": bool,
        "cost_day": (int, float),
        "cost_night": (int, float),
        "total_cost": (int, float),
    }

    for key, expected_type in required_keys.items():
        if key not in data:
            raise ValueError(f"Missing required key: {key}")
        if not isinstance(data[key], expected_type):
            raise TypeError(f"Invalid type for {key}")
    if not data["date_iso8601"] or (not is_valid_iso8601(data["date_iso8601"])):
        data["date_iso8601"] = datetime.utcnow().isoformat()

    history_col.insert_one(data)
