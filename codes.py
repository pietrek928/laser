
# USB transfer codes
from enum import Enum

class USBEp(Enum):
    HODI = 0x01  # endpoint for the "dog," i.e. dongle.
    HIDO = 0x81  # fortunately it turns out that we can ignore it completely.
    HOMI = 0x02  # endpoint for host out, machine in. (query status, send ops)
    HIMO = 0x88  # endpoint for host in, machine out. (receive status reports)

class LaserOp(Enum):
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
    WRITE_CORRECTION_LINE  = 0x0010 # 1 line of correction table (dx, dy, is_first 0x0000/0x0100)
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


# Job operation codes
class LaserJobOp(Enum):
    TRAVEL = 0x8001  # TRAVEL (y, x, angle, distance)
    NOP = 0x8002  # No operation
    WAIT = 0x8004  # WAIT (time)
    CUT = 0x8005  # CUT (y, x, angle, distance)
    SET_TRAVEL_SPEED = 0x8006  # SET TRAVEL SPEED (speed) speed = v * 1.9656 mm/s
    SET_ON_TIME_COMPENSATION = 0x8007  # SET ON TIME COMPENSATION (time us)
    SET_OFF_TIME_COMPENSATION = 0x8008  # SET OFF TIME COMPENSATION (time us)
    SET_CUTTING_SPEED = 0x800C  # SET CUTTING SPEED (speed) speed = v * 1.9656 mm/s
    ALTERNATE_TRAVEL = 0x800D  # ALTERNATE TRAVEL (y, x, angle, distance)
    POLYGON_DELAY = 0x800F  # POLYGON DELAY (time)
    SET_LASER_POWER = 0x8012  # SET LASER POWER (power) power = p / 40.960
    SET_Q_SWITCH_PERIOD = 0x801B # SET Q SWITCH PERIOD (period) period = t * 50 ns
    LASER_CONTROL = 0x8021  # LASER CONTROL (on/off)
    BEGIN = 0x8051  # BEGIN JOB

