import unittest
import database as db
from calculator import proceed_input_data

TARIFF_DAY = db.get_config()["tariff_day"]
TARIFF_NIGHT = db.get_config()["tariff_night"]
CORRECTION_DAY = db.get_config()["correction_day"]
CORRECTION_NIGHT = db.get_config()["correction_night"]


class TestProceedInputData(unittest.TestCase):

    def test_via_test(self):
        _id = "test_meter"
        val_day = 10
        val_night = 10
        result = proceed_input_data(_id, val_day, val_night)
        db.del_meter_by_id(_id)
        print(result)

    #  1 Тест для вже існуючого
    def test_update_existed(self):
        """
        Лічильник створюється в самому тесті, де він і видалиться,
        так моделюється те, що лічильник існував
        до того як було викликано обрахунок
        Значення в створеному лічильнику ненульові
        """
        _id = "existed_meter"
        prev_day = 10
        prev_night = 10
        input_day = 20
        input_night = 20
        expected_corrected = False
        expected_used_day = input_day - prev_day
        expected_used_night = input_night - prev_night

        expected_cost_day = TARIFF_DAY * expected_used_day
        expected_cost_night = TARIFF_NIGHT * expected_used_night

        expected_current_day = input_day
        expected_current_night = input_night

        db.create_meter(_id, prev_day, prev_night)

        result = proceed_input_data(_id, input_day, input_night)
        db.del_meter_by_id(_id)

        self.assertEqual(result["meter_id"], _id)
        self.assertEqual(result["prev_day"], prev_day)
        self.assertEqual(result["prev_night"], prev_night)
        self.assertEqual(result["used_day"], expected_used_day)
        self.assertEqual(result["used_night"], expected_used_night)
        self.assertEqual(result["current_day"], expected_current_day)
        self.assertEqual(result["current_night"], expected_current_night)
        self.assertEqual(result["corrected"], expected_corrected)
        self.assertEqual(result["cost_day"], expected_cost_day)
        self.assertEqual(result["cost_night"], expected_cost_night)

    #  2 Тест для не існуючого
    def test_create_new_meter_and_update(self):
        """
        має створитись новий лічильник з нульовими даними,
        створення має відбутись через виклик в функції обрахунку
        до яких буде додані введені і виконано порівняння
        в кінці тесту новостворений лічильник видалиться
        """
        _id = "new_meter"
        prev_day = 0
        prev_night = 0
        input_day = 10
        input_night = 10
        expected_corrected = False

        expected_used_day = input_day - prev_day
        expected_used_night = input_night - prev_night

        expected_cost_day = TARIFF_DAY * input_day
        expected_cost_night = TARIFF_NIGHT * input_night

        expected_current_day = prev_day + input_day
        expected_current_night = prev_night + input_night

        result = proceed_input_data(_id, input_day, input_night)
        db.del_meter_by_id(_id)
        self.assertEqual(result["meter_id"], _id)
        self.assertEqual(result["prev_day"], prev_day)
        self.assertEqual(result["prev_night"], prev_night)
        self.assertEqual(result["used_day"], expected_used_day)
        self.assertEqual(result["used_night"], expected_used_night)
        self.assertEqual(result["current_day"], expected_current_day)
        self.assertEqual(result["current_night"], expected_current_night)
        self.assertEqual(result["corrected"], expected_corrected)
        self.assertEqual(result["cost_day"], expected_cost_day)
        self.assertEqual(result["cost_night"], expected_cost_night)

    #  3 Тест для вже існуючого
    def test_update_existed_with_lower_night(self):
        """
        Лічильник створюється в самому тесті, де він і видалиться,
        так моделюється те, що лічильник існував
        до того як було викликано обрахунок
        Значення в створеному лічильнику ненульові
        """
        _id = "existed_meter"
        prev_day = 10
        prev_night = 10
        input_day = 20
        input_night = 5  # менше за попереднє
        expected_used_day = input_day - prev_day
        expected_used_night = CORRECTION_NIGHT
        expected_correction = True

        expected_cost_day = TARIFF_DAY * expected_used_day
        expected_cost_night = TARIFF_NIGHT * expected_used_night

        expected_current_day = prev_day + expected_used_day
        expected_current_night = prev_night + expected_used_night

        db.create_meter(_id, prev_day, prev_night)

        result = proceed_input_data(_id, input_day, input_night)
        db.del_meter_by_id(_id)

        self.assertEqual(result["meter_id"], _id)
        self.assertEqual(result["prev_day"], prev_day)
        self.assertEqual(result["prev_night"], prev_night)
        self.assertEqual(result["used_day"], expected_used_day)
        self.assertEqual(result["used_night"], expected_used_night)
        self.assertEqual(result["current_day"], expected_current_day)
        self.assertEqual(result["current_night"], expected_current_night)
        self.assertEqual(result["corrected"], expected_correction)
        self.assertEqual(result["cost_day"], expected_cost_day)
        self.assertEqual(result["cost_night"], expected_cost_night)

    #  4 Тест для вже існуючого
    def test_update_existed_with_lower_day(self):
        """
        Лічильник створюється в самому тесті, де він і видалиться,
        так моделюється те, що лічильник існував
        до того як було викликано обрахунок
        Значення в створеному лічильнику ненульові
        """
        _id = "existed_meter"
        prev_day = 10
        prev_night = 10
        input_day = 5  # менше за попереднє
        input_night = 20
        expected_used_day = CORRECTION_DAY
        expected_used_night = input_night - prev_night
        expected_correction = True

        expected_cost_day = TARIFF_DAY * expected_used_day
        expected_cost_night = TARIFF_NIGHT * expected_used_night

        expected_current_day = prev_day + expected_used_day
        expected_current_night = prev_night + expected_used_night

        db.create_meter(_id, prev_day, prev_night)

        result = proceed_input_data(_id, input_day, input_night)
        db.del_meter_by_id(_id)

        self.assertEqual(result["meter_id"], _id)
        self.assertEqual(result["prev_day"], prev_day)
        self.assertEqual(result["prev_night"], prev_night)
        self.assertEqual(result["used_day"], expected_used_day)
        self.assertEqual(result["used_night"], expected_used_night)
        self.assertEqual(result["current_day"], expected_current_day)
        self.assertEqual(result["current_night"], expected_current_night)
        self.assertEqual(result["corrected"], expected_correction)
        self.assertEqual(result["cost_day"], expected_cost_day)
        self.assertEqual(result["cost_night"], expected_cost_night)

#  4 Тест для вже існуючого
    def test_update_existed_with_lower_day_and_night(self):
        """
        Лічильник створюється в самому тесті, де він і видалиться,
        так моделюється те, що лічильник існував
        до того як було викликано обрахунок
        Значення в створеному лічильнику ненульові
        """
        _id = "existed_meter"
        prev_day = 10
        prev_night = 10
        input_day = 5  # обидва значення менші за превіоус
        input_night = 5
        expected_used_day = CORRECTION_DAY
        expected_used_night = CORRECTION_NIGHT
        expected_correction = True

        expected_cost_day = TARIFF_DAY * expected_used_day
        expected_cost_night = TARIFF_NIGHT * expected_used_night

        expected_current_day = prev_day + expected_used_day
        expected_current_night = prev_night + expected_used_night

        db.create_meter(_id, prev_day, prev_night)

        result = proceed_input_data(_id, input_day, input_night)
        db.del_meter_by_id(_id)

        self.assertEqual(result["meter_id"], _id)
        self.assertEqual(result["prev_day"], prev_day)
        self.assertEqual(result["prev_night"], prev_night)
        self.assertEqual(result["used_day"], expected_used_day)
        self.assertEqual(result["used_night"], expected_used_night)
        self.assertEqual(result["current_day"], expected_current_day)
        self.assertEqual(result["current_night"], expected_current_night)
        self.assertEqual(result["corrected"], expected_correction)
        self.assertEqual(result["cost_day"], expected_cost_day)
        self.assertEqual(result["cost_night"], expected_cost_night)