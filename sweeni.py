"""Test module which runs the first example in the README."""

import getpass
import json
from pathlib import Path

from ring_doorbell import Auth, AuthenticationError, Requires2FAError, Ring, RingGeneric
from ring_doorbell.const import (
    SETTINGS_ENDPOINT,
)

user_agent = "ring-doorbell-sweeni"  # Change this
cache_file = Path(user_agent + ".token.cache")


def token_updated(token) -> None:
    cache_file.write_text(json.dumps(token))


def otp_callback():
    return input("2FA code: ")


def do_auth():
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    auth = Auth(user_agent, None, token_updated)
    try:
        auth.fetch_token(username, password)
    except Requires2FAError:
        auth.fetch_token(username, password, otp_callback())
    return auth


def main() -> None:
    if cache_file.is_file():  # auth token is cached
        auth = Auth(user_agent, json.loads(cache_file.read_text()), token_updated)
        ring = Ring(auth)
        try:
            ring.create_session()  # auth token still valid
        except AuthenticationError:  # auth token has expired
            auth = do_auth()
    else:
        auth = do_auth()  # Get new auth token
        ring = Ring(auth)

    ring.update_data()

    # print(ring.devices())
    devices = ring.devices()
    device: RingGeneric | None = None
    for device in devices.doorbots:
        print(f"Doorbots      =>Name : {device.name} \t kind: {device.kind} \t ID: {device.id}")
    for device in devices.authorized_doorbots:
        print(f"Auth_Doorbots =>Name : {device.name} \t kind: {device.kind} \t ID: {device.id}")
    for device in devices.chimes:
        print(f"Chimes        =>Name : {device.name} \t kind: {device.kind} \t ID: {device.id}")
    for device in devices.stickup_cams:
        print(f"Stickup_Cams  =>Name : {device.name} \t kind: {device.kind} \t ID: {device.id}")
    for device in devices.other:
        print(f"Other         =>Name : {device.name} \t kind: {device.kind} \t ID: {device.id}")

    # sweeni@TX1-1010035SLT2:/mnt/c/d/code/python-ring-doorbell$ python3 sweeni.py 
    # Doorbots      =>Name : Front Door        kind: doorbell_v4       ID: 7349477
    # Chimes        =>Name : Upstairs          kind: chime_v2          ID: 86994969
    # Chimes        =>Name : Hallway   kind: chime     ID: 7868298
    # Chimes        =>Name : Patio     kind: chime_v2          ID: 86994197

    # sweeni@TX1-1010035SLT2:/mnt/c/d/code/python-ring-doorbell$ python3 ring_doorbell/cli.py list
    # ---------------------------------
    # Ring CLI
    # Front Door (doorbell_v4)
    # Upstairs (chime_v2)
    # Hallway (chime)
    # Patio (chime_v2)


    # sweeni@TX1-1010035SLT2:/mnt/c/d/code/python-ring-doorbell$ python3 ring_doorbell/cli.py motion_detection --device-name "Front Door" --on
    # ---------------------------------
    # Ring CLI
    # Front Door (doorbell_v4) already has motion detection on


    device = ring.get_device_by_name("Front Door")
    url = SETTINGS_ENDPOINT.format(device.device_api_id)
    # '/devices/v1/devices/7349477/settings'
    payload = {"motion_settings": {"motion_detection_enabled": True}}
    
    # payload = {"duration": 180}
    # CHIMES_ENDPOINT = "/clients_api/chimes/{0}"
    # url = "/clients_api/chimes/86994969/snooze"
    
    device._ring.query(url, method="PATCH", json=payload)
    device._ring.update_devices()



if __name__ == "__main__":
    main()




