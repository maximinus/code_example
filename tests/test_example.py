import unittest

from main import DataWriter


class TestDataHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.handler = DataWriter('example', 100)

    def test_starts_non_running(self):
        self.assertFalse(self.handler.thread.is_alive())

    def test_frequency_correct(self):
        self.assertEqual(self.handler.frequency, 100)

    def test_string_representation(self):
        self.assertEqual(str(self.handler), 'example, 100Hz')


if __name__ == '__main__':
    unittest.main()
