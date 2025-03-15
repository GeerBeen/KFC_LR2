import database as db
from datetime import datetime

TARIFF_DAY_KEY = "tariff_day"
TARIFF_NIGHT_KEY = "tariff_night"
CORRECTION_DAY_KEY = "correction_day"
CORRECTION_NIGHT_KEY = "correction_night"


def check_for_correcting_need_by_id(_id: str, current_day: float, current_night: float):
    try:
        meter = db.get_meter_by_id(_id)
        prev_day = meter["last_day"]
        prev_night = meter["last_night"]
        result = prev_day <= current_day and prev_night <= current_night
        return result
    except ValueError:
        return True


def calculate_price(tariff_day: float, tariff_night: float, used_day: float, used_night: float):
    if used_day < 0 or used_night < 0:
        raise ValueError("Used value must be > 0")

    if tariff_day <= 0 or tariff_night <= 0:
        raise ValueError("Tariffs must be > 0")

    cost_day = tariff_day * used_day
    cost_night = tariff_night * used_night
    total_cost = cost_day + cost_night

    return {
        "cost_day": cost_day,
        "cost_night": cost_night,
        "total_cost": total_cost
    }


def proceed_input_data(meter_id: str, current_day_value: float, current_night_value: float):
    try:
        meter = db.get_meter_by_id(meter_id)
    except ValueError:
        meter = db.create_meter(meter_id)

    config = db.get_config()

    used_day = current_day_value - meter.get("last_day", 0)
    used_night = current_night_value - meter.get("last_night", 0)
    tariff_day = config.get(TARIFF_DAY_KEY, 0)
    tariff_night = config.get(TARIFF_NIGHT_KEY, 0)
    corrected = False
    date_iso8601 = datetime.utcnow().isoformat()

    if used_day < 0:
        used_day = config.get("correction_day", 0)
        current_day_value = meter.get("last_day", 0) + used_day
        corrected = True

    if used_night < 0:
        used_night = config.get("correction_night", 0)
        current_night_value = meter.get("last_night", 0) + used_night
        corrected = True

    price = calculate_price(tariff_day, tariff_night, used_day, used_night)

    db.add_usage_by_id(meter_id, used_day, used_night, date_iso8601)
    history_entry = {
        "meter_id": meter_id,
        "date_iso8601": date_iso8601,
        "corrected": corrected,
        "prev_day": meter.get("last_day", 0),
        "prev_night": meter.get("last_night", 0),
        "current_day": current_day_value,
        "current_night": current_night_value,
        "used_day": used_day,
        "used_night": used_night,
        "tariff_day": tariff_day,
        "tariff_night": tariff_night,
        "cost_day": price["cost_day"],
        "cost_night": price["cost_night"],
        "total_cost": price["total_cost"],

    }

    db.write_to_history(history_entry)
    return history_entry
