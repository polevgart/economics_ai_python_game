"""Chicken!"""

from strategies.registration import registry_strategy
from .straregy import AArturSmartStrategy


registry_strategy(AArturSmartStrategy)