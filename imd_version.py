from dataclasses import dataclass
from typing import Any, Dict, Optional

from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException


@dataclass
class IMDChannelStatus:
    unit_id: int
    voltage_raw: Optional[int]
    voltage_v: Optional[float]
    pos_resistance_raw: Optional[int]
    pos_resistance_kohm: Optional[float]
    pos_resistance_state: str
    neg_resistance_raw: Optional[int]
    neg_resistance_kohm: Optional[float]
    neg_resistance_state: str
    reverse_polarity: Optional[bool]
    monitoring_enabled: Optional[bool]
    resistance_valid: Optional[bool]
    version_raw: Optional[int]
    version: Optional[str]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "voltage_raw": self.voltage_raw,
            "voltage_v": self.voltage_v,
            "pos_resistance_raw": self.pos_resistance_raw,
            "pos_resistance_kohm": self.pos_resistance_kohm,
            "pos_resistance_state": self.pos_resistance_state,
            "neg_resistance_raw": self.neg_resistance_raw,
            "neg_resistance_kohm": self.neg_resistance_kohm,
            "neg_resistance_state": self.neg_resistance_state,
            "reverse_polarity": self.reverse_polarity,
            "monitoring_enabled": self.monitoring_enabled,
            "resistance_valid": self.resistance_valid,
            "version_raw": self.version_raw,
            "version": self.version,
            
            }
        


class IMDClient:
    """
    High-level client for the BLUE JAY JY1000-C2 IMD using Modbus RTU over RS485.

    - Exposes per-channel status queries (IMD1/IMD2).
    - Provides helpers to enable/disable insulation monitoring for a given channel address.
    """

    # Register addresses from the Reference.md
    REG_BUS_VOLTAGE = 0x0010
    REG_POS_RESISTANCE = 0x0012
    REG_NEG_RESISTANCE = 0x0013
    REG_VERSION = 0x001A
    REG_STATUS = 0x001B
    REG_INSULATION_CONTROL = 0x0102
    REG_ADDRESS = 0x0103
    REG_BAUDRATE = 0x0104
    REG_SLAVE_ID = 0x66

    INVALID_RESISTANCE = 0xFFFF
    INFINITE_RESISTANCE = 0xEA60

    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        parity: str = "None",
        stopbits: int = 1,
        bytesize: int = 8,
        timeout: float = 1.0,
    ) -> None:
        self._client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            parity=parity,
            stopbits=stopbits,
            bytesize=bytesize,
            timeout=timeout,
        )

    def connect(self) -> bool:
        """Open the serial connection."""
        return bool(self._client.connect())

    def close(self) -> None:
        """Close the serial connection."""
        self._client.close()

    # ---------- low-level helpers ----------

    def _read_holding_registers(
        self, unit_id: int, address: int, count: int = 1
    ) -> Optional[list[int]]:
        try:
            # Newer pymodbus API uses "device_id" instead of "unit"/"slave"
            response = self._client.read_holding_registers(
                address=address,
                count=count,
                device_id=unit_id,
            )
        except ModbusException:
            return None
                                                 
        if response.isError():
            return None

        # type: ignore[attr-defined]
        return list(response.registers)

    def _write_single_register(self, unit_id: int, address: int, value: int) -> bool:
        try:
            # Newer pymodbus API uses "device_id" instead of "unit"/"slave"
            response = self._client.write_register(
                address=address,
                value=value,
                device_id=unit_id,
            )
        except ModbusException:
            return False

        if response.isError():
            return False

        return True

    # ---------- public API ----------

    def read_channel_status(self, unit_id: int) -> IMDChannelStatus:
        """
        Read all key parameters for a given IMD channel (Modbus unit ID).

        Returns an IMDChannelStatus dataclass; use .as_dict() if you prefer a plain dict.
        """
        # Voltage
        voltage_regs = self._read_holding_registers(unit_id, self.REG_BUS_VOLTAGE, 1)
        # voltage_v = 0.1
        voltage_raw = voltage_regs[0] if voltage_regs else None
        # voltage_raw = 10.0
        voltage_v = (voltage_raw / 10.0) if voltage_raw is not None else None

        # Positive insulation resistance
        pos_regs = self._read_holding_registers(unit_id, self.REG_POS_RESISTANCE, 1)
        pos_raw = pos_regs[0] if pos_regs else None
        pos_state, pos_kohm = self._interpret_resistance(pos_raw)

        # Negative insulation resistance
        neg_regs = self._read_holding_registers(unit_id, self.REG_NEG_RESISTANCE, 1)
        neg_raw = neg_regs[0] if neg_regs else None
        neg_state, neg_kohm = self._interpret_resistance(neg_raw)

        # Version
        version_regs = self._read_holding_registers(unit_id, self.REG_VERSION, 1)
        version_raw = version_regs[0] if version_regs else None
        version = self._interpret_version(version_raw)
        # Status bits
        status_regs = self._read_holding_registers(unit_id, self.REG_STATUS, 1)
        status_raw = status_regs[0] if status_regs else None
        reverse_polarity = None
        monitoring_enabled = None
        resistance_valid = None
        if status_raw is not None:
            reverse_polarity = bool((status_raw >> 7) & 0x1)
            monitoring_enabled = bool((status_raw >> 2) & 0x1)
            resistance_valid = bool((status_raw >> 1) & 0x1)

        return IMDChannelStatus(
            unit_id=unit_id,
            voltage_raw=voltage_raw,
            voltage_v=voltage_v,
            pos_resistance_raw=pos_raw,
            pos_resistance_kohm=pos_kohm,
            pos_resistance_state=pos_state,
            neg_resistance_raw=neg_raw,
            neg_resistance_kohm=neg_kohm,
            neg_resistance_state=neg_state,
            reverse_polarity=reverse_polarity,
            monitoring_enabled=monitoring_enabled,
            resistance_valid=resistance_valid,
            version_raw=version_raw,
            version=version,
        )

    def enable_insulation_monitoring(self, unit_id: int) -> bool:
        """
        Enable insulation monitoring for a given channel (unit ID).

        Manual examples write:
        - Unit 1: value 0x0102
        - Unit 2: value 0x0012
        """
        if unit_id == 1:
            value = 0x0010
        elif unit_id == 2:
            value = 0x0012
        else:
            # Fallback: just enable bit 0x0011 for non-standard IDs.
            value = 0x0011

        return self._write_single_register(unit_id, self.REG_INSULATION_CONTROL, value)
    
    
    def read_insulation_data(self, ch):
        raw = self.client.read_holding_registers(10, 2)
        return raw

    def disable_insulation_monitoring(self, unit_id: int) -> bool:
        """
        Disable insulation monitoring for a given channel (unit ID).
        Manual examples write 0x0000.
        """
        return self._write_single_register(unit_id, self.REG_INSULATION_CONTROL, 0x0000)

    # ---------- convenience wrappers ----------

    def IMD1StatusRequest(self, unit_id) -> Dict[str, Any]:
        """Read all parameters for IMD channel 1 (unit ID 1) and return them as a dict."""
        return self.read_channel_status(unit_id=unit_id).as_dict()

    def IMD2StatusRequest(self, unit_id) -> Dict[str, Any]:
        """Read all parameters for IMD channel 2 (unit ID 2) and return them as a dict."""
        return self.read_channel_status(unit_id=unit_id).as_dict()

    # ---------- interpretation helpers ----------

    def _interpret_resistance(self, raw: Optional[int]) -> tuple[str, Optional[float]]:
        """
        Interpret a raw insulation resistance register value.

        Returns (state, value_kohm) where state is one of:
        - "invalid"
        - "infinite"
        - "valid"
        """
        if raw is None:
            return "invalid", None


        if raw == self.INVALID_RESISTANCE:
            return "invalid", None

        if raw == self.INFINITE_RESISTANCE:
            return "infinite", None

        return "valid", float(raw)

    def _interpret_version(self, raw: Optional[int]) -> Optional[str]:
        """
        Interpret version register.
        Manual example: raw value 0x2201 -> "V2201".
        """
        if raw is None:
            return None
        return f"V{raw:04X}"


__all__ = [
    "IMDClient",
    "IMDChannelStatus",
]