# =====================================================
# AC METER MODBUS FUNCTIONS
# =====================================================

import logging
import struct
# from imd import client

# =====================================================
# AC METER REGISTER MAP
# =====================================================

AC_METER_SLAVE_ID = 5

ADDRESS = 0X003C

AC_REGISTERS = {

    # S.No : (Name, Register)

    1: ("Import kWh", 0),
    11: ("Voltage L1-N", 60),
    13: ("Voltage L2-N", 64),
    15: ("Voltage L3-N", 68),

    27: ("Current L1", 92),
    29: ("Current L2", 96),
    31: ("Current L3", 100),

    43: ("System PF", 124),
    45: ("System Frequency", 128),
    46: ("Line 1 kW", 130),

    48: ("Line 2 kW", 134),
    50: ("Line 3 kW", 138)
}


# =====================================================
# CONVERT 2 REGISTERS TO FLOAT
# =====================================================

# =====================================================
# FLOAT WORD SWAP CONVERSION
# =====================================================

def registers_to_float(registers):

    """
    Convert:
    Float (32-bit little endian byte swap)
    """

    if len(registers) != 2:
        return None

    try:

        # Word swap
        word1 = registers[0]
        word2 = registers[1]

        swapped = struct.pack(
            '>HH',
            word2,
            word1
        )

        value = struct.unpack(
            '>f',
            swapped
        )[0]

        return round(value, 2)

    except Exception as e:

        logging.error(
            f"Float conversion error: {e}"
        )

        return None


# =====================================================
# READ AC METER PARAMETER
# =====================================================

def read_ac_parameter(client, address):

    """
    Read AC meter float parameter.
    """

    try:

        response = client.read_holding_registers(
            address=address,
            count=2,
            slave=AC_METER_SLAVE_ID
        )

        if response.isError():

            logging.error(
                f"AC Meter read failed: {address}"
            )

            return None

        return registers_to_float(
            response.registers
        )

    except Exception as e:

        logging.error(
            f"AC Meter exception: {e}"
        )

        return None


# =====================================================
# READ ALL AC METER DATA
# =====================================================

def read_ac_meter(client):

    """
    Read all required AC meter parameters.
    """

    ac_data = {}

    for sno, (name, register) in AC_REGISTERS.items():

        value = read_ac_parameter(
            client,
            register
        )

        ac_data[name] = value

    return ac_data



def print_ac_meter_data(ac_data):

    """
    Print AC meter values.
    """

    print("\n======= AC METER DATA =======")

    for key, value in ac_data.items():

        print(f"{key} : {value}")