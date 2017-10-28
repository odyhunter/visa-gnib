from src.utils import fetch_appointments
from src.config import VISA_TYPE


def test_main():
    assert fetch_appointments(5, VISA_TYPE)
