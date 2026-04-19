import time
from imd_version import IMDClient

# Current and new unit addresses for both IMD devices.
# Slave ID 1 will be changed to 4
# Slave ID 2 will be changed to 5
IMD_1_ADDRESS_current = 1
IMD_1_ADDRESS_new = 4
IMD_2_ADDRESS_current = 2
IMD_2_ADDRESS_new = 5

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 0.5  # seconds


def change_and_verify_address(client, current_addr, new_addr, device_name):
    """
    Attempt to change device address and verify the change with retries.
    
    Returns:
        tuple: (success: bool, version_value: Optional[int])
    """
    print(f"\nChanging {device_name} from address {current_addr} to {new_addr}...")
    
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"  Attempt {attempt}/{MAX_RETRIES}...")
        
        # Write the new address
        write_success = client._write_single_register(
            current_addr,
            client.REG_ADDRESS,
            new_addr,
        )
        print(f"    Write status: {write_success}")
        
        if not write_success:
            print(f"    Write failed on attempt {attempt}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            continue
        
        # Add delay before verification to allow device to settle
        time.sleep(RETRY_DELAY)
        
        # Verify by reading version register
        version_regs = client._read_holding_registers(
            new_addr,
            client.REG_VERSION,
            1
        )
        
        if version_regs:
            version_raw = version_regs[0]
            print(f"    ✓ Address change verified!")
            print(f"    {device_name} responded at address {new_addr}")
            print(f"    Version Register Value: 0x{version_raw:04X} ({version_raw})")
            return True, version_raw
        else:
            print(f"    ✗ Device did not respond at new address on attempt {attempt}")
            if attempt < MAX_RETRIES:
                print(f"    Retrying...")
                time.sleep(RETRY_DELAY)
    
    # All retries exhausted
    print(f"    ✗ FAILED: {device_name} address change could not be verified after {MAX_RETRIES} attempts")
    return False, None


def main() -> None:
    """
    Change the address of Modbus slaves.
    
    Converts:
    - Slave ID 1 to Slave ID 4
    - Slave ID 2 to Slave ID 5
    
    Verifies the address change by reading the device version number
    from the new slave IDs (REG_VERSION = 0x001A).
    Retries up to MAX_RETRIES times if verification fails.
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

    print("="*60)
    print("Starting Slave Address Change Process")
    print("="*60)
    print(f"Configuration: MAX_RETRIES={MAX_RETRIES}, RETRY_DELAY={RETRY_DELAY}s")

    # Change and verify IMD1
    imd1_success, imd1_version = change_and_verify_address(
        client,
        IMD_1_ADDRESS_current,
        IMD_1_ADDRESS_new,
        "IMD1"
    )

    # Change and verify IMD2
    imd2_success, imd2_version = change_and_verify_address(
        client,
        IMD_2_ADDRESS_current,
        IMD_2_ADDRESS_new,
        "IMD2"
    )

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"IMD1 Address Change (1→4): {'✓ VERIFIED' if imd1_success else '✗ FAILED'}")
    if imd1_success:
        print(f"  Version: 0x{imd1_version:04X}")
    print(f"IMD2 Address Change (2→5): {'✓ VERIFIED' if imd2_success else '✗ FAILED'}")
    if imd2_success:
        print(f"  Version: 0x{imd2_version:04X}")
    
    if imd1_success and imd2_success:
        print("\n✓ All address changes verified successfully!")
    else:
        print("\n✗ Some address changes could not be verified after retries.")
        if not imd1_success:
            print("  - IMD1 may still be at address 1, or communication failed")
        if not imd2_success:
            print("  - IMD2 may still be at address 2, or communication failed")

    # Close the connection
    client.disconnect()


if __name__ == "__main__":
    main()
