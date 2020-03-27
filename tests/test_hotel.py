import unittest

from hotels.models.hotel import Hotel


class TestHotel(unittest.TestCase):
    def test_from_json(self):
        hotels = [
            Hotel("a", "rating", "votes", 123, "£", ["comm1", "comm2"], "/detail1"),
            Hotel("2a", "rating2", "votes2", 2123, "£", ["comm"], "/detail1"),

        ]
        list_of_dict = [h.to_dict() for h in hotels]
        list_hotels = Hotel.from_json(list_of_dict)
        for i, h in enumerate(list_hotels):
            self.assertEqual(h.to_dict(), hotels[i].to_dict())


if __name__ == '__main__':
    unittest.main()
