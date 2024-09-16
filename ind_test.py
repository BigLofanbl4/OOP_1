import os
import sqlite3
import unittest
from datetime import datetime
from pathlib import Path

from ind import add_person, create_db, select_all, select_by_surname


class DatabaseOperationsTest(unittest.TestCase):
    # Перед началом каждого теста, создаем временную бд
    def setUp(self):
        self.db_path = Path("test_people.db")
        create_db(self.db_path)

    def tearDown(self):
        if self.db_path.exists():
            os.remove(self.db_path)

    # Проверяем правильно ли создаются таблицы
    def test_create_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        self.assertIn(("zodiacs",), tables)
        self.assertIn(("people",), tables)

        conn.close()

    def test_add_person(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        surname = "Plugatyrev"
        name = "Vladislav"
        zodiac = "Capricorn"
        birthday = datetime.strptime("2005-01-12", "%Y-%m-%d").date()

        add_person(self.db_path, surname, name, zodiac, birthday)

        cursor.execute(
            """
        SELECT people.surname, people.name, zodiacs.zodiac_title, people.birthday
        FROM people
        INNER JOIN zodiacs ON zodiacs.zodiac_id = people.zodiac_id
        """
        )
        row = cursor.fetchall()[0]

        conn.close()

        self.assertEqual(row[0], surname)
        self.assertEqual(row[1], name)
        self.assertEqual(row[2], zodiac)
        self.assertEqual(row[3], birthday.strftime("%Y-%m-%d"))

    def test_select_by_surname(self):
        add_person(
            self.db_path,
            "Plugatyrev",
            "Vladislav",
            "Capricorn",
            datetime.strptime("2005-01-12", "%Y-%m-%d").date(),
        )
        add_person(
            self.db_path,
            "Chickodan",
            "Alexey",
            "Lion",
            datetime.strptime("2003-08-08", "%Y-%m-%d").date(),
        )
        add_person(
            self.db_path,
            "Ivanov",
            "Ivan",
            "Gemini",
            datetime.strptime("2000-11-30", "%Y-%m-%d").date(),
        )

        target = select_by_surname(self.db_path, "Chickodan")

        self.assertEqual(target[0]["surname"], "Chickodan")

    def test_select_all(self):
        add_person(
            self.db_path, "Plugatyrev", "Vladislav", "Capricorn", "2005-01-12"
        )
        add_person(self.db_path, "Chickodan", "Alexey", "Lion", "2003-08-08")
        add_person(self.db_path, "Ivanov", "Ivan", "Gemini", "2000-11-30")

        people = select_all(self.db_path)

        self.assertEqual(len(people), 3)
        self.assertEqual(people[0]["surname"], "Plugatyrev")
        self.assertEqual(people[1]["surname"], "Chickodan")
        self.assertEqual(people[2]["surname"], "Ivanov")


if __name__ == "__main__":
    unittest.main()
