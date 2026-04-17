from pprint import pprint

from imd_version import IMDClient
from modules.contants import IMDStatus

import time


IMD_1_ADDRESS_current = 3
IMD_1_ADDRESS_new = 1
IMD_2_ADDRESS_current = 4
IMD_2_ADDRRESS_new = 5


def main() -> None:
    """
    Example entrypoint for using the IMDClient.

    Adjust the serial port (and optionally baudrate/parity) to match your hardware.
    """
    # TODO: update this to the correct serial port on your system, e.g. "COM3"
    # port = "COM11"  # for windows
    port = "/dev/ttymxc1"  # for linux

    client = IMDClient(port="/dev/ttymxc1",  #com11 using it is for windows
                       baudrate=9600,
                       parity="N",
                       stopbits=1,
                       bytesize=8,
                       timeout=0.3)   

    if not client.connect():
        print("connection failed")
        return
    write_success = client._write_single_register(IMD_1_ADDRESS_current, client.REG_ADDRESS, IMD_1_ADDRESS_new)
    print(f"[INFO] Write success: {write_success}")
    
    write_success = client._write_single_register(IMD_2_ADDRESS_current, client.REG_ADDRESS, IMD_2_ADDRRESS_new)
    print(F"[INFO] write success: {write_success}")
    
    imd1_status: dict = {}
    imd2_status: dict = {}
    # comment out the following lines if you want to test with only one IMD connected (e.g. just address 1)

    try:
        while True:
            # for i in range(3): 
            # print("--------------------------------")
            # print(end= " ")
            # print("Attempt to enable insulation monitoring")
            # print("--------------------------------")

            #  Enable insulation monitoring on both channels
            
            status_1 = client.read_channel_status(IMD_1_ADDRESS_new) 
            if not imd1_status.get("monitoring_enabled", False):
                print("Enabling insulation monitoring for IMD1...")
                register_1 = client._write_single_register(IMD_1_ADDRESS_new , client.REG_INSULATION_CONTROL, 0x0011)
                # register_2 = client._write_single_register(IMD_2_ADDRESS , client.REG_INSULATION_CONTROL, 0x0012)
                            
                enabled_ch1 = client.enable_insulation_monitoring(IMD_1_ADDRESS_new)
                # enabled_ch2 = client.enable_insulation_monitoring(IMD_2_ADDRESS)
                
                # if client.enable_insulation_monitoring(IMD_1_ADDRESS):
                #     print("Successfully enabled insulation monitoring for IMD1.")
                # else:
                #     print("Failed to enable insulation monitoring for IMD1.")
            
            if not imd2_status.get("monitoring_enabled", False):
                print("Enabling insulation monitoring for IMD2...")
                # register_1 = client._write_single_register(IMD_1_ADDRESS , client.REG_INSULATION_CONTROL, 0x0011)
                register_2 = client._write_single_register(IMD_2_ADDRRESS_new , client.REG_INSULATION_CONTROL, 0x0012)
                            
                # enabled_ch1 = client.enable_insulation_monitoring(IMD_1_ADDRESS)
                enabled_ch2 = client.enable_insulation_monitoring(IMD_2_ADDRRESS_new)
                
                # if client.enable_insulation_monitoring(IMD_2_ADDRESS):
                #     print("Successfully enabled insulation monitoring for IMD2.")
                # else:
                #     print("Failed to enable insulation monitoring for IMD2.")

                                                                                                                                                                
            # print(f"Enable CH1 monitoring: {'success' if enabled_ch1 else 'failed'}")
            # print(f"Enable CH2 monitoring: {'success' if enabled_ch2 else 'failed'}")

    # try:
        # while True:# Read full status for IMD1 (address 1) and IMD2 (address 2)
            print("========== IMD1 status: ==========")
            imd1_status = client.IMD1StatusRequest(unit_id=IMD_1_ADDRESS_new)
            IMDStatus.IMD1Status = imd1_status
            # pprint(imd1_status)
            pprint(IMDStatus.IMD1Status)


            print("========== IMD2 status: ==========")
            imd2_status = client.IMD2StatusRequest(unit_id=IMD_2_ADDRRESS_new)
            IMDStatus.IMD2Status = imd2_status
            # pprint(imd2_status)
            pprint(IMDStatus.IMD2Status)

            time.sleep(0.2)

        # # Example: disable monitoring again
        #     disabled_ch1 = client.disable_insulation_monitoring(IMD_1_ADDRESS)
        #     disabled_ch2 = client.disable_insulation_monitoring(IMD_2_ADDRESS)
            
            # print(f"\nDisable CH1 monitoring: {'success' if disabled_ch1 else 'failed'}")
            # print(f"Disable CH2 monitoring: {'success' if disabled_ch2 else 'failed'}")
 
    finally:
        disabled_ch1 = client.disable_insulation_monitoring(IMD_1_ADDRESS_new)
        disabled_ch2 = client.disable_insulation_monitoring(IMD_2_ADDRRESS_new)
        client.close()
        
                   

if __name__ == "__main__":
    main()