import unittest

from services.fleet_manager import FleetManager


class TestFleetService(unittest.TestCase):
    
    def test_get_fleets(self):
        fleet_service = FleetManager("configs/fleets.json")

        results = fleet_service.get_fleets()

        self.assertIsNotNone(results)
        self.assertTrue(len(results) > 0)


if __name__ == "__main__":
    unittest.main()
