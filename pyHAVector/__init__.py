"""Vector module."""

from pyHAVector.messaging import protocol
from .configure import Configure
from .connection import Connection, ControlPriorityLevel
from .events import EventHandler
from .exceptions import VectorConfigurationException
from .utils import read_configuration


class Robot:
    """Basic robot class."""

    def __init__(
        self,
        serial: str = None,
        ip: str = None,
        name: str = None,
        config: dict = None,
        email: str = None,
        password: str = None,
        settings_dir: str = None,
        behavior_activation_timeout: int = 10,
        cache_animation_lists: bool = True,
        enable_face_detection: bool = False,
        estimate_facial_expression: bool = False,
        enable_audio_feed: bool = False,
        enable_custom_object_detection: bool = False,
        enable_nav_map_feed: bool = None,
        show_viewer: bool = False,
        show_3d_viewer: bool = False,
        behavior_control_level: ControlPriorityLevel = ControlPriorityLevel.DEFAULT_PRIORITY,
    ):
        """Initialize Robot object."""

        config = config if config is not None else {}
        config = {**read_configuration(serial, name, settings_dir), **config}

        self._name = config["name"]
        self._ip = ip if ip is not None else config["ip"]
        self._cert_file = config["cert"]
        self._guid = config["guid"]
        self._port = "443"
        self._serial = serial

        self._conn = Connection(
            self._name,
            ":".join([self._ip, self._port]),
            self._cert_file,
            self._guid,
            behavior_control_level,
        )
        self._events = EventHandler(self)

    @property
    def conn(self) -> Connection:
        """A reference to the :class:`~anki_vector.connection.Connection` instance."""
        return self._conn

    @property
    def events(self) -> events.EventHandler:
        """A reference to the :class:`~anki_vector.events.EventHandler` instance."""
        return self._events

    def connect(self, timeout: int = 10) -> None:
        """Connect to Vector."""
        self.conn.connect(timeout=timeout)
        self.events.start(self.conn)

        self.events.subscribe(
            self._unpack_robot_state,
            events.Events.robot_state,
            _on_connection_thread=True,
        )

    def _unpack_robot_state(self, _robot, _event_type, msg):
        self._pose = utils.Pose(
            x=msg.pose.x,
            y=msg.pose.y,
            z=msg.pose.z,
            q0=msg.pose.q0,
            q1=msg.pose.q1,
            q2=msg.pose.q2,
            q3=msg.pose.q3,
            origin_id=msg.pose.origin_id,
        )
        self._pose_angle_rad = msg.pose_angle_rad
        self._pose_pitch_rad = msg.pose_pitch_rad
        self._left_wheel_speed_mmps = msg.left_wheel_speed_mmps
        self._right_wheel_speed_mmps = msg.right_wheel_speed_mmps
        self._head_angle_rad = msg.head_angle_rad
        self._lift_height_mm = msg.lift_height_mm
        self._accel = utils.Vector3(msg.accel.x, msg.accel.y, msg.accel.z)
        self._gyro = utils.Vector3(msg.gyro.x, msg.gyro.y, msg.gyro.z)
        self._carrying_object_id = msg.carrying_object_id
        self._head_tracking_object_id = msg.head_tracking_object_id
        self._localized_to_object_id = msg.localized_to_object_id
        self._last_image_time_stamp = msg.last_image_time_stamp
        self._status.set(msg.status)

    def disconnect(self) -> None:
        """Close the connection with Vector.

        .. testcode::

            import anki_vector
            robot = anki_vector.Robot()
            robot.connect()
            robot.anim.play_animation_trigger("GreetAfterLongTime")
            robot.disconnect()
        """
        # if self.conn.requires_behavior_control:
        #     self.vision.close()

        # # Stop rendering video
        # self.viewer.close()

        # # Stop rendering 3d video
        # self.viewer_3d.close()

        # # Shutdown camera feed
        # self.camera.close_camera_feed()

        # # TODO shutdown audio feed when available

        # # Shutdown nav map feed
        # self.nav_map.close_nav_map_feed()

        # # Close the world and cleanup its objects
        # self.world.close()

        # self.proximity.close()
        # self.touch.close()

        self.events.close()
        self.conn.close()

    async def async_speak(
        self, text: str, use_vector_voice: bool = True
    ) -> protocol.SayTextResponse:
        """Let Vector have a voice."""
        say_text_request = protocol.SayTextRequest(
            text=text, use_vector_voice=use_vector_voice,duration_scalar=1.0
        )
        return await self.conn.grpc_interface.SayText(say_text_request)
