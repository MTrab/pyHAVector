"""For testing the module."""

import asyncio
from os import environ
from pathlib import Path
from pyHAVector import Robot
from pyHAVector.connection import ControlPriorityLevel


robot = Robot(
    "00908e7e",
    "192.168.1.223",
    "Vector-A6S1",
    email=environ["EMAIL"],
    password=environ["PASSWORD"],
    settings_dir=Path.cwd() / "vector_config",
)

robot.connect()

asyncio.run(robot.async_speak("Testing my voice"))

# robot.disconnect()
