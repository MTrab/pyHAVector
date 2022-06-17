"""For testing the module."""

import asyncio
from os import environ
from pathlib import Path
from pyHAVector import Robot
from pyHAVector.configure import Configure
from pyHAVector.connection import ControlPriorityLevel
from pyHAVector.exceptions import VectorConfigurationException


try:
    robot = Robot(
        "00908e7e",
        "192.168.1.223",
        "Vector-A6S1",
        settings_dir=str(Path.cwd()) + "/vector_config",
    )
except VectorConfigurationException:
    asyncio.run(
        Configure(
            environ["EMAIL"],
            environ["PASSWORD"],
            "Vector-A6S1",
            "00908e7e",
            "192.168.1.223",
            settings_dir=str(Path.cwd()) + "/vector_config",
        ).async_run()
    )
    robot = Robot(
        "00908e7e",
        "192.168.1.223",
        "Vector-A6S1",
        settings_dir=str(Path.cwd()) + "/vector_config",
    )


robot.connect()

asyncio.run(robot.async_speak("Testing my voice"))

# robot.disconnect()
