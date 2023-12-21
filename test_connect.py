from time import sleep
from traceback import print_exc
from typing import Tuple, Union
from pydantic import BaseModel
import usb.core
import usb.util

from .codes import *

class LaserOp(BaseModel):
    command: int
    parameters: Tuple[int, ...] = ()

    def __init__(self, command: Union[int, Enum], *parameters):
        if isinstance(command, Enum):
            command = int(command.value)
        super().__init__(command=command, parameters=tuple(
            int(p) for p in parameters
        ))
        self.validate()
    
    def validate(self):
        if not 0 <= self.command <= 0xFFFF:
            raise ValueError(f"Invalid command {self.command}")
        if len(self.parameters) > 5:
            raise ValueError(f"Too many parameters {self.parameters}")
        for param in self.parameters:
            if not 0 <= param <= 0xFFFF:
                raise ValueError(f"Invalid parameter {param} of command {self.command}")

    def to_bytes(self):
        values = [0] * 6
        values[0] = self.command
        values [1:1+len(self.parameters)] = self.parameters
        return b''.join(v.to_bytes(2, byteorder='little') for v in values)


def find_device():
    print("Finding device...")
    for v in usb.core.find(find_all=True):
        print(f"Found device: {v}")

    devices = tuple(usb.core.find(find_all=True, idVendor=0x9588, idProduct=0x9899))
    print(f"Found {len(devices)} laser devices")
    if not devices:
        raise ValueError("Device not found")

    device = devices[0]
    device.set_configuration()
    try:
        device.reset()
    except usb.core.USBError:
        print_exc()
        raise ValueError("Could not reset device")

    print("Laser device works")
    return device


# send command as uint16_t[6] list
def send_command(device: usb.core.Device, command, *parameters, read=True):
    op = LaserOp(command, *parameters)
    command_bytes = op.to_bytes()
    print(command_bytes)
    if device.write(USBEp.HOMI.value, command_bytes, 100) != len(command_bytes):
        raise ValueError("Could not send command")

    if not read:
        return 0, 0, 0

    response_bytes = device.read(USBEp.HIMO.value, 8, 100)
    print(f"Response: {response_bytes}")
    if len(response_bytes) != 8:
        raise ValueError("Could not read correct response")

    return (
        int.from_bytes(response_bytes[6:8], byteorder='little'), # status
        int.from_bytes(response_bytes[2:4], byteorder='little'),
        int.from_bytes(response_bytes[4:6], byteorder='little'),
    )


def check_device_ready(device):
    print("Checking device ready...")
    status, _, _ = send_command(device, LaserOp.READ_PORT)
    return bool(status & 0x20)


def test_laser():
    device = find_device()
    laser_ready = check_device_ready(device)
    print('Laser device ready ' + str(laser_ready))
    if not laser_ready:
        return

    print('Get serial number', send_command(device, LaserOp.GET_SERIAL_NUMBER))
    print('Get xy position', send_command(device, LaserOp.GET_XY_POSITION))

    print('Enable laser', send_command(device, LaserOp.ENABLE_LASER))
    print('Set laser mode', send_command(device, LaserOp.SET_LASER_MODE))
    print('Set standby', send_command(device, LaserOp.SET_STANDBY))
    print('Set PWM half period', send_command(device, LaserOp.SET_PWM_HALF_PERIOD, 125))
    print('Set PWM', send_command(device, LaserOp.SET_PWM_PULSE_WIDTH, 125))
    print('Fiber open', send_command(device, LaserOp.FIBER_OPEN_MO))
    # print('Linght on', send_command(device, LaserOp.WRITE_PORT, (1 << 8, ), read=True))

    print('Set laser on', send_command(device, LaserJobOp.LASER_CONTROL, 1))
    print('Set laser power', send_command(device, LaserJobOp.SET_LASER_POWER, 125))
    print('Test cut', send_command(device, LaserJobOp.CUT, 0x8000, 0x8000, 10, 10))
    sleep(1)
    print('Disable laser', send_command(device, LaserOp.DISABLE_LASER))


if __name__ == '__main__':
    test_laser()
