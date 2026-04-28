from pprint import pprint

from imd_version import IMDClient
from modules.contants import IMDStatus

import time



IMD_1_ADDRESS = 1
IMD_2_ADDRESS = 2
SENSOR_ID = 7



def main() -> None:
    """
    Example entrypoint for using the IMDClient.

    Adjust the serial port (and optionally baudrate/parity) to match your hardware.
    """
    # TODO: update this to the correct serial port on your system, e.g. "COM3"
    # port = "COM11"  # for windows
    port = "/dev/ttymxc1"  # for linux

    client = IMDClient(port=port,  #com11 using it is for windows
                    #    method= "rtu",
                       baudrate=9600,
                       parity="N",
                       stopbits=1,
                       bytesize=8,
                       timeout=0.5)

    if not client.connect():
        print("connection failed. You dont want retry again")
        return
    
    imd1_status: dict = {}
    imd2_status: dict = {}
    # comment out the following lines if you want to test with only one IMD connected (e.g. just address 1)

    try:
        while True:
            #  Enable insulation monitoring on both channels
            # pprint(f"Before Enabling IMD1: {imd1_status}")
            # pprint(f"Before Enabling IMD2: {imd2_status}")
            if not imd1_status.get("monitoring_enabled", False):
                print("Enabling insulation monitoring for IMD1...")
                client.enable_insulation_monitoring(IMD_1_ADDRESS)
                time.sleep(1.0)  # let IMD1 complete first measurement cycle

            if not imd2_status.get("monitoring_enabled", False):
                print("Enabling insulation monitoring for IMD2...")
                client.enable_insulation_monitoring(IMD_2_ADDRESS)
                time.sleep(1.0)  # let IMD2 complete first measurement cycle

            print("========== IMD1 status: ==========")
            imd1_status = client.IMD1StatusRequest(unit_id=IMD_1_ADDRESS)
            IMDStatus.IMD1Status = imd1_status
            pprint(f"After Enabling IMD1: {IMDStatus.IMD1Status}")

            time.sleep(0.5)  # inter-slave gap on RS-485 bus

            print("========== IMD2 status: ==========")
            imd2_status = client.IMD2StatusRequest(unit_id=IMD_2_ADDRESS)
            IMDStatus.IMD2Status = imd2_status
            # pprint(imd2_status)
            pprint(f"After Enabling IMD2: {IMDStatus.IMD2Status}")

            read_sensor = client.read_sensor(slave_id= SENSOR_ID)
            print(read_sensor)
            time.sleep(2)
    
 
    finally:
        client.disable_insulation_monitoring(IMD_1_ADDRESS)
        client.disable_insulation_monitoring(IMD_2_ADDRESS)
        client.close()
        
if __name__ == "__main__":
    main()