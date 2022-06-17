"""Custom functions used for Vector communications."""
import configparser
import logging
import os
import platform
import socket
from pathlib import Path

import grpc
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

import anki_vector
from anki_vector import messaging

_LOGGER = logging.getLogger(__name__)


class ApiHandler:
    """Define API handler."""

    def __init__(self, headers: dict, url: str):
        self._headers = headers
        self._url = url

    @property
    def headers(self):
        """Return headers."""
        return self._headers

    @property
    def url(self):
        """Return URL."""
        return self._url


class Api:
    """Define API instance."""

    def __init__(self):
        """Initialize instance."""
        self._handler = ApiHandler(
            headers={
                "User-Agent": f"Vector-sdk/{anki_vector.__version__} {platform.python_implementation()}/{platform.python_version()}",
                "Anki-App-Key": "aung2ieCho3aiph7Een3Ei",
            },
            url="https://accounts.api.anki.com/1/sessions",
        )

    @property
    def name(self):
        """Return name."""
        return "Anki Cloud"

    @property
    def handler(self):
        """Return handler."""
        return self._handler


@staticmethod
async def async_get_cert(hass: HomeAssistant, serial: str) -> bytes:
    """Get Vector certificate."""
    client = async_get_clientsession(hass)
    res = await client.get(
        f"https://session-certs.token.global.anki-services.com/vic/{serial}"
    )
    if res.status != 200:
        raise Exception("Could not get Vector certificate")

    cert = await res.read()
    return cert


@staticmethod
def save_cert(cert, name, serial, anki_dir):
    """Write Vector's certificate to a file located in the user's home directory"""
    os.makedirs(str(anki_dir), exist_ok=True)
    cert_file = str(anki_dir / f"{name}-{serial}.cert")
    with os.fdopen(os.open(cert_file, os.O_WRONLY | os.O_CREAT, 0o600), "wb") as file:
        file.write(cert)
    return cert_file


@staticmethod
def validate_cert_name(cert_file, robot_name):
    """Validate the name on Vector's certificate against the user-provided name"""
    with open(cert_file, "rb") as file:
        cert_file = file.read()
        cert = x509.load_pem_x509_certificate(cert_file, default_backend())
        for fields in cert.subject:
            current = str(fields.oid)
            if "commonName" in current:
                common_name = fields.value
                if common_name != robot_name:
                    raise Exception(
                        f"The name of the certificate ({common_name}) does not match the name provided ({robot_name}).\n"
                        "Please verify the name, and try again."
                    )


@staticmethod
async def async_get_session_token(hass, api, username: str, password: str):
    """Get Vector session token."""
    payload = {"username": username, "password": password}

    client = async_get_clientsession(hass)
    res = await client.post(api.handler.url, data=payload, headers=api.handler.headers)
    if res.status != 200:
        raise Exception("Error fetching session token.")

    val = await res.json(content_type="text/json")
    _LOGGER.debug(val)
    return val


@staticmethod
def user_authentication(session_id: bytes, cert: bytes, ip: str, name: str) -> str:
    """Authenticate."""
    # Pin the robot certificate for opening the channel
    creds = grpc.ssl_channel_credentials(root_certificates=cert)

    channel = grpc.secure_channel(
        f"{ip}:443",
        creds,
        options=(
            (
                "grpc.ssl_target_name_override",
                name,
            ),
        ),
    )

    # Verify the connection to Vector is able to be established (client-side)
    try:
        # Explicitly grab _channel._channel to test the underlying grpc channel directly
        grpc.channel_ready_future(channel).result(timeout=15)
    except grpc.FutureTimeoutError as err:
        raise Exception(
            "\nUnable to connect to Vector\n"
            "Please be sure to connect via the Vector companion app first, and connect your computer to the same network as your Vector."
        ) from err

    try:
        interface = messaging.client.ExternalInterfaceStub(channel)
        request = messaging.protocol.UserAuthenticationRequest(
            user_session_id=session_id.encode("utf-8"),
            client_name=socket.gethostname().encode("utf-8"),
        )
        response = interface.UserAuthentication(request)
        if (
            response.code
            != messaging.protocol.UserAuthenticationResponse.AUTHORIZED  # pylint: disable=no-member
        ):
            raise Exception(
                "\nFailed to authorize request:\n"
                "Please be sure to first set up Vector using the companion app."
            )
    except grpc.RpcError as err:
        raise Exception(
            "\nFailed to authorize request:\n" "An unknown error occurred '{err}'"
        ) from err

    return response.client_token_guid


@staticmethod
def write_config(serial, cert_file=None, ip=None, name=None, guid=None, clear=True):
    """Write config to sdk_config.ini."""
    home = Path.home()
    config_file = str(home / ".anki_vector" / "sdk_config.ini")

    config = configparser.ConfigParser(strict=False)

    try:
        config.read(config_file)
    except configparser.ParsingError:
        if os.path.exists(config_file):
            os.rename(config_file, config_file + "-error")
    if clear:
        config[serial] = {}
    if cert_file:
        config[serial]["cert"] = cert_file
    if ip:
        config[serial]["ip"] = ip
    if name:
        config[serial]["name"] = name
    if guid:
        config[serial]["guid"] = guid.decode("utf-8")
    temp_file = config_file + "-temp"
    if os.path.exists(config_file):
        os.rename(config_file, temp_file)
    try:
        with os.fdopen(os.open(config_file, os.O_WRONLY | os.O_CREAT, 0o600), "w") as f:
            config.write(f)
    except Exception as err:
        if os.path.exists(temp_file):
            os.rename(temp_file, config_file)
        raise err
    else:
        if os.path.exists(temp_file):
            os.remove(temp_file)
