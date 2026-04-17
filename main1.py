from imd_version import IMDClient
# from main import IMD_1_ADDRESS, main  

IMD_1_ADDRESS_current = 1
IMD_1_ADDRESS_new = 3
IMD_2_ADDRESS = 2

def main() -> None:
    port = "/dev/ttymxc1"  
    
    client = IMDClient(port="/dev/ttymxc1", 
                        baudrate=9600,
                        parity="N",
                        stopbits=1,
                        bytesize=8,
                        timeout=0.3)


    # First modify the address register
    write_success = client._write_single_register(IMD_1_ADDRESS_current, client.REG_ADDRESS, IMD_1_ADDRESS_new)
    
    # # Then read back the modified address
    # address_regs = client._read_holding_registers(IMD_1_ADDRESS_new, client.REG_ADDRESS, 1)
    # address_reg = address_regs[0] if address_regs else None
    
    print(f"[INFO] Write success: {write_success}")
    # print(f"[INFO] IMD1 Modified Address: {address_reg}")        



if __name__ == "__main__":
    main()
    
