import unittest

from hotels.models.hotel import Hotel


class TestHotel(unittest.TestCase):
    def test_from_json(self):
        hotels = [
            Hotel("a", "b", 123, "£", "/detail1"),
            Hotel("2a", "2b", 2123, "£", "/detail1"),

        ]
        list_of_dict = [h.__dict__ for h in hotels]
        list_hotels = Hotel.from_json(list_of_dict)
        for i, h in enumerate(list_hotels):
            self.assertEqual(h.__dict__, hotels[i].__dict__)


if __name__ == '__main__':
    unittest.main()
