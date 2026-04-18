from pprint import pprint
import time

from imd_version import IMDClient
from modules.contants import IMDStatus

# Current and new unit addresses for both IMD devices.
# The script rewrites each device address before monitoring.
IMD_1_ADDRESS_current = 1
IMD_1_ADDRESS_new = 6
IMD_2_ADDRESS_current = 2
IMD_2_ADDRRESS_new = 4



def main() -> None:
    """
    Example entrypoint for using the IMDClient.

    Adjust the serial port (and optionally baudrate/parity) to match your hardware.
    """
    # TODO: update this to the correct serial port on your system, e.g. "COM3"
    # port = "COM11"  # for windows
    port = "/dev/ttymxc1"  # for linux

    client = IMDClient(
        port=port,
        baudrate=9600,
        parity="N",
        stopbits=1,
        bytesize=8,
        timeout=0.3,
    )

    # Open the serial/Modbus connection to the IMD device.
    if not client.connect():
        print("Connection failed")
        return

    # Write the new unit address to each IMD device so they can be addressed properly.
    write_success = client._write_single_register(
        IMD_1_ADDRESS_current,
        client.REG_ADDRESS,
        IMD_1_ADDRESS_new,
    )
    print(f"[INFO] IMD1 address write success: {write_success}")

    write_success = client._write_single_register(
        IMD_2_ADDRESS_current,
        client.REG_ADDRESS,
        IMD_2_ADDRRESS_new,
    )
    print(f"[INFO] IMD2 address write success: {write_success}")

    imd1_status: dict = {}
    imd2_status: dict = {}



    try:
        while True:
            # Read current status from IMD1.
            status_1 = client.read_channel_status(IMD_1_ADDRESS_new)
            if not imd1_status.get("monitoring_enabled", False):
                print("Enabling insulation monitoring for IMD1...")
                client._write_single_register(
                    IMD_1_ADDRESS_new,
                    client.REG_INSULATION_CONTROL,
                    0x0011,
                )
                client.enable_insulation_monitoring(IMD_1_ADDRESS_new)

            # Read current status from IMD2.
            status_2 = client.read_channel_status(IMD_2_ADDRRESS_new)
            if not imd2_status.get("monitoring_enabled", False):
                print("Enabling insulation monitoring for IMD2...")
                client._write_single_register(
                    IMD_2_ADDRRESS_new,
                    client.REG_INSULATION_CONTROL,
                    0x0012,
                )
                client.enable_insulation_monitoring(IMD_2_ADDRRESS_new)

            # Request and display detailed status for each IMD channel.
            print("========== IMD1 status: ==========")
            imd1_status = client.IMD1StatusRequest(unit_id=IMD_1_ADDRESS_new)
            IMDStatus.IMD1Status = imd1_status
            pprint(IMDStatus.IMD1Status)

            print("========== IMD2 status: ==========")
            imd2_status = client.IMD2StatusRequest(unit_id=IMD_2_ADDRRESS_new)
            IMDStatus.IMD2Status = imd2_status
            pprint(IMDStatus.IMD2Status)

            # Wait briefly before the next poll to reduce bus traffic.
            time.sleep(0.2)

    finally:
        # Disable insulation monitoring and close the connection on exit.
        client.disable_insulation_monitoring(IMD_1_ADDRESS_new)
        client.disable_insulation_monitoring(IMD_2_ADDRRESS_new)
        client.close()
        
                   

if __name__ == "__main__":
    main()