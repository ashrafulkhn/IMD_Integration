import time
import logging

from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException


# =====================================================
# LOGGING CONFIGURATION
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# =====================================================
# MODBUS CONFIGURATION
# =====================================================

PORT = "/dev/ttymxc1"
BAUDRATE = 9600
SLAVE_ID = 2


# =====================================================
# REGISTER MAP
# =====================================================

VERSION_REGISTER = 0x001A
STATUS_REGISTER = 0x001B

POSITIVE_RES_REGISTER = 0x0012
NEGATIVE_RES_REGISTER = 0x0013

ENABLE_REGISTER = 0x0102


# =====================================================
# CREATE MODBUS CLIENT
# =====================================================

client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=2
)


# =====================================================
# CONNECT TO DEVICE
# =====================================================

def connect_modbus():

    """
    Connect to Modbus RTU device.
    """

    if client.connect():

        logging.info("Connected to IMD device")
        return True

    logging.error("Failed to connect to IMD")
    return False


# =====================================================
# CLOSE CONNECTION
# =====================================================

def close_modbus():

    """
    Close serial connection.
    """

    client.close()

    logging.info("Connection closed")


# =====================================================
# READ REGISTER FUNCTION
# =====================================================

def read_register(address, count=1, retries=3):

    """
    Read holding register with retry logic.
    """

    for attempt in range(1, retries + 1):

        try:

            response = client.read_holding_registers(
                address=address,
                count=count,
                slave=SLAVE_ID
            )

            if response.isError():

                logging.warning(
                    f"Read failed: {hex(address)} "
                    f"(Attempt {attempt})"
                )

            else:

                logging.info(
                    f"Read success: {hex(address)}"
                )

                return response.registers

        except ModbusException as e:

            logging.error(f"Modbus exception: {e}")

        except Exception as e:

            logging.error(f"Unexpected error: {e}")

        time.sleep(1)

    logging.error(
        f"Failed to read register {hex(address)}"
    )

    return None


# =====================================================
# WRITE REGISTER FUNCTION
# =====================================================

def write_register(address, value):

    """
    Write single holding register.
    """

    try:

        response = client.write_register(
            address=address,
            value=value,
            slave=SLAVE_ID
        )

        if response.isError():

            logging.error(
                f"Write failed: {hex(address)}"
            )

            return False

        logging.info(
            f"Write success: {hex(address)}"
        )

        return True

    except Exception as e:

        logging.error(f"Write exception: {e}")
        return False


# =====================================================
# READ VERSION
# =====================================================

def read_version():

    """
    Read firmware version.
    """

    data = read_register(VERSION_REGISTER)

    if data is None:

        return None

    version = data[0]

    logging.info(f"Firmware Version: {version}")

    return version


# =====================================================
# READ STATUS
# =====================================================

def read_status():

    """
    Read IMD status register.
    """

    data = read_register(STATUS_REGISTER)

    if data is None:

        return None

    status = data[0]

    result = {

        "raw_status": status,

        "monitoring_enabled":
            bool(status & (1 << 12)),

        "measurement_valid":
            bool(status & (1 << 11)),

        "reverse_voltage_alarm":
            bool(status & (1 << 7))
    }

    logging.info(f"Status: {result}")

    return result


def enable_monitoring():

    """
    Enable insulation monitoring
    if currently disabled.
    """

    status = read_status()

    if status is None:

        return False

    # Check monitoring bit
    if status["monitoring_enabled"]:

        logging.info(
            "Monitoring already enabled"
        )

        return True

    logging.warning(
        "Monitoring disabled. Enabling now..."
    )

    try:

        response = client.write_register(
            address=ENABLE_REGISTER,
            value=0x11,
            slave=SLAVE_ID
        )

        if response.isError():

            logging.error(
                "Failed to enable monitoring"
            )

            return False

        logging.info(
            "Monitoring enabled successfully"
        )

        time.sleep(2)

        return True

    except Exception as e:

        logging.error(
            f"Enable monitoring error: {e}"
        )

        return False


# =====================================================
# READ INSULATION RESISTANCE
# =====================================================

def read_resistance():

    """
    Read positive and negative insulation
    resistance values.
    """

    pos_data = read_register(
        POSITIVE_RES_REGISTER
    )

    neg_data = read_register(
        NEGATIVE_RES_REGISTER
    )

    if pos_data is None or neg_data is None:

        logging.error(
            "Failed to read resistance values"
        )

        return None

    pos_raw = pos_data[0]
    neg_raw = neg_data[0]

    # 60000 means infinite resistance
    pos_value = (
        "Infinite"
        if pos_raw >= 60000
        else f"{pos_raw} KΩ"
    )

    neg_value = (
        "Infinite"
        if neg_raw >= 60000
        else f"{neg_raw} KΩ"
    )

    result = {

        "positive_resistance_raw": pos_raw,
        "negative_resistance_raw": neg_raw,

        "positive_resistance": pos_value,
        "negative_resistance": neg_value
    }

    logging.info(f"Resistance: {result}")

    return result