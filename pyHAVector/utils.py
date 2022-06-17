"""Utils for Vector module."""

import configparser
from pathlib import Path

from .exceptions import VectorConfigurationException


class Vector3:
    """Represents a 3D Vector (type/units aren't specified).

    :param x: X component
    :param y: Y component
    :param z: Z component
    """

    __slots__ = ("_x", "_y", "_z")

    def __init__(self, x: float, y: float, z: float):
        self._x = float(x)
        self._y = float(y)
        self._z = float(z)

    def set_to(self, rhs):
        """Copy the x, y and z components of the given Vector3 instance.

        :param rhs: The right-hand-side of this assignment - the
                source Vector3 to copy into this Vector3 instance.
        """
        self._x = float(rhs.x)
        self._y = float(rhs.y)
        self._z = float(rhs.z)

    @property
    def x(self) -> float:
        """The x component."""
        return self._x

    @property
    def y(self) -> float:
        """The y component."""
        return self._y

    @property
    def z(self) -> float:
        """The z component."""
        return self._z

    @property
    def magnitude_squared(self) -> float:
        """float: The magnitude of the Vector3 instance"""
        return self._x**2 + self._y**2 + self._z**2

    @property
    def magnitude(self) -> float:
        """The magnitude of the Vector3 instance"""
        return math.sqrt(self.magnitude_squared)

    @property
    def normalized(self):
        """A Vector3 instance with the same direction and unit magnitude"""
        mag = self.magnitude
        if mag == 0:
            return Vector3(0, 0, 0)
        return Vector3(self._x / mag, self._y / mag, self._z / mag)

    def dot(self, other):
        """The dot product of this and another Vector3 instance"""
        if not isinstance(other, Vector3):
            raise TypeError("Unsupported argument for dot product, expected Vector3")
        return self._x * other.x + self._y * other.y + self._z * other.z

    def cross(self, other):
        """The cross product of this and another Vector3 instance"""
        if not isinstance(other, Vector3):
            raise TypeError("Unsupported argument for cross product, expected Vector3")

        return Vector3(
            self._y * other.z - self._z * other.y,
            self._z * other.x - self._x * other.z,
            self._x * other.y - self._y * other.x,
        )

    @property
    def x_y_z(self):
        """tuple (float, float, float): The X, Y, Z elements of the Vector3 (x,y,z)"""
        return self._x, self._y, self._z

    def __repr__(self):
        return f"<{self.__class__.__name__} x: {self.x:.2f} y: {self.y:.2f} z: {self.z:.2f}>"

    def __add__(self, other):
        if not isinstance(other, Vector3):
            raise TypeError("Unsupported operand for +, expected Vector3")
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        if not isinstance(other, Vector3):
            raise TypeError("Unsupported operand for -, expected Vector3")
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        if not isinstance(other, (int, float)):
            raise TypeError("Unsupported operand for * expected number")
        return Vector3(self.x * other, self.y * other, self.z * other)

    def __truediv__(self, other):
        if not isinstance(other, (int, float)):
            raise TypeError("Unsupported operand for / expected number")
        return Vector3(self.x / other, self.y / other, self.z / other)


class Component:
    """Base class for all components."""

    def __init__(self, robot):
        self._robot = robot

    @property
    def robot(self):
        return self._robot

    @property
    def conn(self):
        return self._robot.conn

    @property
    def force_async(self):
        return self._robot.force_async

    @property
    def grpc_interface(self):
        """A direct reference to the connected aiogrpc interface."""
        return self._robot.conn.grpc_interface


def read_configuration(serial: str, name: str, settings_dir: str = None) -> dict:
    """Open the default conf file, and read it into a :class:`configparser.ConfigParser`
    If :code:`serial is not None`, this method will try to find a configuration with serial
    number :code:`serial`, and raise an exception otherwise. If :code:`serial is None` and
    :code:`name is not None`, this method will try to find a configuration which matches
    the provided name, and raise an exception otherwise. If both :code:`serial is None` and
    :code:`name is None`, this method will return a configuration if exactly `1` exists, but
    if multiple configurations exists, it will raise an exception.

    :param serial: Vector's serial number
    :param name: Vector's name
    """
    home = settings_dir or str(Path.home())
    conf_file = str(home + "/config.ini")
    parser = configparser.ConfigParser(strict=False)
    parser.read(conf_file)

    sections = parser.sections()
    if not sections:
        raise VectorConfigurationException(
            "Could not find the sdk configuration file. Please run `python3 -m anki_vector.configure` to set up your Vector for SDK usage."
        )
    elif (serial is None) and (name is None):
        if len(sections) == 1:
            serial = sections[0]
        else:
            raise VectorConfigurationException(
                "Found multiple robot serial numbers. "
                "Please provide the serial number or name of the Robot you want to control.\n\n"
                "Example: ./01_hello_world.py --serial {{robot_serial_number}}"
            )

    config = {k.lower(): v for k, v in parser.items()}

    if serial is not None:
        serial = serial.lower()
        try:
            return config[serial]
        except KeyError:
            raise VectorConfigurationException(
                "Could not find matching robot info for given serial number: {}. "
                "Please check your serial number is correct.\n\n"
                "Example: ./01_hello_world.py --serial {{robot_serial_number}}",
                serial,
            )
    else:
        for keySerial in config:
            for key in config[keySerial]:
                if config[keySerial][key] == name:
                    return config[keySerial]
                if config[keySerial][key].lower() == name.lower():
                    return config[keySerial]

        raise VectorConfigurationException(
            "Could not find matching robot info for given name: {}. "
            "Please check your name is correct.\n\n"
            "Example: ./01_hello_world.py --name {{robot_name}}",
            name,
        )
