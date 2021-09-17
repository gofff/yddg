"""
    Yandex Disk Data Generator

    Asynchronous generator to work with data from Yandex Disk
    storage (disk.yandex.ru) without saving items to long-term
    memory
"""

__version__ = '0.1.0'

__all__ = ["YDDataGenerator"]

from .data_generator import YDDataGenerator
