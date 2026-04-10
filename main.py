from pprint import pprint

from imd_version import IMDClient

import time


IMD_1_ADDRESS = 1
IMD_2_ADDRESS = 2

def main() -> None:
    """
    Example entrypoint for using the IMDClient.

    Adjust the serial port (and optionally baudrate/parity) to match your hardware.
    """
    # TODO: update this to the correct serial port on your system, e.g. "COM3"
    port = "COM11"

    client = IMDClient(port="com11",
                       baudrate=9600,
                       parity="N",
                       stopbits=1.5,
                       bytesize=8,
                       timeout=2.0)   

    if not client.connect():
        print(f"Failed to connect to IMD on port {port}")
        return
    
    
    # comment out the following lines if you want to test with only one IMD connected (e.g. just address 1)

    try:
        while True:
            # for i in range(3): 
            print("--------------------------------")
            print(f"Attempt to enable insulation monitoring")
            print("--------------------------------")

            # Enable insulation monitoring on both channels
            
            status_1 = client.read_channel_status(IMD_1_ADDRESS)   
            register_1 = client._write_single_register(IMD_1_ADDRESS , client.REG_INSULATION_CONTROL, 0x0011)
            register_2 = client._write_single_register(IMD_2_ADDRESS , client.REG_INSULATION_CONTROL, 0x0012)


            # print(f"register_1 {IMD_1_ADDRESS}")
            # print(f"register_2 {IMD_2_ADDRESS}")
            
                        
            enabled_ch1 = client.enable_insulation_monitoring(IMD_1_ADDRESS)
            enabled_ch2 = client.enable_insulation_monitoring(IMD_2_ADDRESS)
         
            print(f"Enable CH1 monitoring: {'success' if enabled_ch1 else 'failed'}")
            print(f"Enable CH2 monitoring: {'success' if enabled_ch2 else 'failed'}")

            # Read full status for IMD1 (address 1) and IMD2 (address 2)
            print("\nIMD1 status:")
            imd1_status = client.IMD1StatusRequest(unit_id=IMD_1_ADDRESS)
            pprint(imd1_status)

            print("\nIMD2 status:")
            imd2_status = client.IMD2StatusRequest(unit_id=IMD_2_ADDRESS)
            pprint(imd2_status)

            time.sleep(1)

        # Example: disable monitoring again
            disabled_ch1 = client.disable_insulation_monitoring(IMD_1_ADDRESS)
       
            disabled_ch2 = client.disable_insulation_monitoring(IMD_2_ADDRESS)
            print(f"\nDisable CH1 monitoring: {'success' if disabled_ch1 else 'failed'}")
            print(f"Disable CH2 monitoring: {'success' if disabled_ch2 else 'failed'}")

    finally:
        client.close()
        
    

if __name__ == "__main__":
    main()