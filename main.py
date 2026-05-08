import time
import serial
from imd import (
    connect_modbus,
    close_modbus,
    read_version,
    read_status,
    enable_monitoring,
    read_resistance
)
from ac_meter import (
    read_ac_meter,
    print_ac_meter_data
)
from imd import client

ser = serial.Serial(
    port="/dev/ttymxc1",
    baudrate=9600,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=2
)
# =====================================================
# MAIN FUNCTION
# =====================================================

def main():

    # ---------------------------------------------
    # CONNECT TO IMD
    # ---------------------------------------------

    if not connect_modbus():

        return

    try:
        while True:
            # -----------------------------------------
            # ENABLE MONITORING
            # -----------------------------------------

            # enable_monitoring()
            frame = bytes([0x02, 0x06, 0x01, 0x02, 0x00, 0x12, 0xA9, 0xC8])
            ser.write(frame)

            time.sleep(2)

            # -----------------------------------------
            # READ FIRMWARE VERSION
            # -----------------------------------------

            version = read_version()

            print("\n========== VERSION ==========")
            print(f"Firmware Version : {version}")

        

            # -----------------------------------------
            # READ STATUS
            # -----------------------------------------

            status = read_status()

            print("\n========== STATUS ==========")
            print(status)

            # -----------------------------------------
            # READ RESISTANCE
            # -----------------------------------------

            resistance = read_resistance()

            print("\n======= RESISTANCE =======")
            print(resistance)
            
            # -----------------------------------------
            # READ AC METER DATA
            # -----------------------------------------

            ac_data = read_ac_meter(client)

            print_ac_meter_data(ac_data)

    finally:

        # -----------------------------------------
        # CLOSE CONNECTION
        # -----------------------------------------

        close_modbus()


# =====================================================
# PROGRAM ENTRY
# =====================================================

if __name__ == "__main__":

    main()