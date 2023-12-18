from time import sleep
from traceback import print_exc
from typing import Tuple
import usb.core
import usb.util


# Marked with ? - currently not seen in the wild
DISABLE_LASER          = 0x0002
RESET                  = 0x0003
ENABLE_LASER           = 0x0004
EXECUTE_LIST           = 0x0005
SET_PWM_PULSE_WIDTH    = 0x0006 # ?
GET_REGISTER           = 0x0007
GET_SERIAL_NUMBER      = 0x0009 # In EzCAD mine is 32012LI43405B, Version 4.02, LMC V4 FIB
GET_LIST_STATUS        = 0x000A
GET_XY_POSITION        = 0x000C # Get current galvo position
SET_XY_POSITION        = 0x000D # Travel the galvo xy to specified position
LASER_SIGNAL_OFF       = 0x000E # ?
LASER_SIGNAL_ON        = 0x000F # ?
WRITE_CORRECTION_LINE  = 0x0010 # ?
RESET_LIST             = 0x0012
RESTART_LIST           = 0x0013
WRITE_CORRECTION_TABLE = 0x0015
SET_CONTROL_MODE       = 0x0016
SET_DELAY_MODE         = 0x0017
SET_MAX_POLY_DELAY     = 0x0018
SET_END_OF_LIST        = 0x0019
SET_FIRST_PULSE_KILLER = 0x001A
SET_LASER_MODE         = 0x001B
SET_TIMING             = 0x001C
SET_STANDBY            = 0x001D
SET_PWM_HALF_PERIOD    = 0x001E
STOP_EXECUTE           = 0x001F # Since observed in the wild
STOP_LIST              = 0x0020 # ?
WRITE_PORT             = 0x0021
WRITE_ANALOG_PORT_1    = 0x0022 # At end of cut, seen writing 0x07FF
WRITE_ANALOG_PORT_2    = 0x0023 # ?
WRITE_ANALOG_PORT_X    = 0x0024 # ?
READ_PORT              = 0x0025
SET_AXIS_MOTION_PARAM  = 0x0026
SET_AXIS_ORIGIN_PARAM  = 0x0027
GO_TO_AXIS_ORIGIN      = 0x0028
MOVE_AXIS_TO           = 0x0029
GET_AXIS_POSITION      = 0x002A
GET_FLY_WAIT_COUNT     = 0x002B # ?
GET_MARK_COUNT         = 0x002D # ?
SET_FPK_2E             = 0x002E # First pulse killer related, SetFpkParam2
                                # My ezcad lists 40 microseconds as FirstPulseKiller
                                # EzCad sets it 0x0FFB, 1, 0x199, 0x64
FIBER_CONFIG_1         = 0x002F #
FIBER_CONFIG_2         = 0x0030 #
LOCK_INPUT_PORT        = 0x0031 # ?
SET_FLY_RES            = 0x0032 # Unknown fiber laser parameter being set
                                # EzCad sets it: 0x0000, 0x0063, 0x03E8, 0x0019
FIBER_OPEN_MO          = 0x0033 # "IPG (i.e. fiber) Open MO" - MO is probably Master Oscillator
                                # (In BJJCZ documentation, the pin 18 on the IPG connector is
                                #  called "main oscillator"; on the raycus docs it is "emission enable.")
                                # Seen at end of marking operation with all
                                # zero parameters. My Ezcad has an "open MO delay"
                                # of 8 ms
FIBER_GET_StMO_AP      = 0x0034 # Unclear what this means; there is no
                                # corresponding list command. It might be to
                                # get a status register related to the source.
                                # It is called IPG_GETStMO_AP in the dll, and the abbreviations
                                # MO and AP are used for the master oscillator and power amplifier
                                # signal lines in BJJCZ documentation for the board; LASERST is
                                # the name given to the error code lines on the IPG connector.
GET_USER_DATA          = 0x0036 # ?
GET_FLY_PULSE_COUNT    = 0x0037 # ?
GET_FLY_SPEED          = 0x0038 # ?
ENABLE_Z_2             = 0x0039 # ? AutoFocus on/off
ENABLE_Z               = 0x003A # AutoFocus on/off
SET_Z_DATA             = 0x003B # ?
SET_SPI_SIMMER_CURRENT = 0x003C # ?
IS_LITE_VERSION        = 0x0040 # Tell laser to nerf itself for ezcad lite apparently
GET_MARK_TIME          = 0x0041 # Seen at end of cutting, only and always called with param 0x0003
SET_FPK_PARAM          = 0x0062 # Probably "first pulse killer" = fpk


USB_EP_HODI = 0x01  # endpoint for the "dog," i.e. dongle.
USB_EP_HIDO = 0x81  # fortunately it turns out that we can ignore it completely.
USB_EP_HOMI = 0x02  # endpoint for host out, machine in. (query status, send ops)
USB_EP_HIMO = 0x88  # endpoint for host in, machine out. (receive status reports)


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
def send_command(device: usb.core.Device, command, parameters: Tuple[int], read=True):
    values = [0] * 6
    values[0] = command
    values [1:1+len(parameters)] = parameters
    command_bytes = sum(v.to_bytes(2, byteorder='little') for v in values)
    if device.write(USB_EP_HODI, command_bytes, 100) != len(command_bytes):
        raise ValueError("Could not send command")

    if not read:
        return 0, 0, 0

    response_bytes = device.read(USB_EP_HIMO, 8, 100)
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
    status, _, _ = send_command(device, READ_PORT, (), read=True)
    if status != 0x0000:
        raise ValueError("Device not ready")
    return bool(status & 0x20)


def test_laser():
    device = find_device()
    laser_ready = check_device_ready(device)
    print('Laser device ready ' + str(laser_ready))
    if not laser_ready:
        return

    print('Get serial number', send_command(device, GET_SERIAL_NUMBER, (), read=True))
    print('Get xy position', send_command(device, GET_XY_POSITION, (), read=True))

    print('Enable laser', send_command(device, ENABLE_LASER, (), read=True))
    sleep(1)
    print('Disable laser', send_command(device, DISABLE_LASER, (), read=True))


if __name__ == '__main__':
    test_laser()
