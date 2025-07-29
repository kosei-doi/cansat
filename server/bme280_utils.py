import time
from typing import Union, List, Tuple
import pigpio
from collections import OrderedDict

def int_to_binary(n: int, bits: int = 8) -> str:
    return ''.join([str(n >> i & 1 ) for i in reversed(range(0, bits))])

def bytes_to_binary(data: Union[bytearray,bytes]) -> List[str]:
    return [int_to_binary(byte) for byte in data]

def write_register(pi, spi_handler, register_addr: int, data: int):
    write_data = (register_addr & 0b01111111) << 8 | data
    write_data = write_data.to_bytes(2, "big")
    pi.spi_xfer(spi_handler, write_data)

def read_register(pi, spi_handler, register_addr: int, num_bytes: int) -> bytes:
    write_data = (register_addr | 0b10000000) << (8 * num_bytes)
    write_data = write_data.to_bytes(num_bytes + 1, "big")
    cnt, read_data = pi.spi_xfer(spi_handler, write_data)
    if cnt != (num_bytes + 1):
        raise Exception(f"ReadError: cnt={cnt} (expected={num_bytes+1})")
    return read_data[1:]

def read_calibration_data(pi, spi_handler):
    cal_1 = read_register(pi, spi_handler, 0x88, 24)
    cal_2 = read_register(pi, spi_handler, 0xA1, 1)
    cal_3 = read_register(pi, spi_handler, 0xE1, 7)

    cal_data = OrderedDict([
        ("dig_T1", int.from_bytes(cal_1[0:2], "little")),
        ("dig_T2", int.from_bytes(cal_1[2:4], "little", signed=True)),
        ("dig_T3", int.from_bytes(cal_1[4:6], "little", signed=True)),
        ("dig_P1", int.from_bytes(cal_1[6:8], "little")),
        ("dig_P2", int.from_bytes(cal_1[8:10], "little", signed=True)),
        ("dig_P3", int.from_bytes(cal_1[10:12], "little", signed=True)),
        ("dig_P4", int.from_bytes(cal_1[12:14], "little", signed=True)),
        ("dig_P5", int.from_bytes(cal_1[14:16], "little", signed=True)),
        ("dig_P6", int.from_bytes(cal_1[16:18], "little", signed=True)),
        ("dig_P7", int.from_bytes(cal_1[18:20], "little", signed=True)),
        ("dig_P8", int.from_bytes(cal_1[20:22], "little", signed=True)),
        ("dig_P9", int.from_bytes(cal_1[22:24], "little", signed=True)),
        ("dig_H1", int.from_bytes(cal_2, "little")),
        ("dig_H2", int.from_bytes(cal_3[0:2], "little", signed=True)),
        ("dig_H3", cal_3[2]),
        ("dig_H4", cal_3[3] << 4 | (cal_3[4] & 0x0F)),
        ("dig_H5", cal_3[5] << 4 | (cal_3[4] >> 4)),
        ("dig_H6", int.from_bytes(cal_3[6:7], "little", signed=True)),
    ])
    return cal_data

def read_temp(pi, spi_handler, cal_data: OrderedDict) -> Tuple[int, float]:
    read_bytes = read_register(pi, spi_handler, 0xFA, 3)
    temp_raw = int.from_bytes(read_bytes, "big") >> 4
    var1 = (((temp_raw >> 3) - (cal_data["dig_T1"] << 1)) * cal_data["dig_T2"]) >> 11
    var2 = (((((temp_raw >> 4) - cal_data["dig_T1"]) * ((temp_raw >> 4) - cal_data["dig_T1"])) >> 12) * cal_data["dig_T3"]) >> 14
    t_fine = var1 + var2
    temp = ((t_fine * 5 + 128) >> 8) / 100
    return t_fine, temp

def read_pressure(pi, spi_handler, cal_data: OrderedDict, t_fine: int) -> float:
    read_bytes = read_register(pi, spi_handler, 0xF7, 3)
    pressure_raw = int.from_bytes(read_bytes, "big") >> 4
    var1 = t_fine - 128000
    var2 = var1 * var1 * cal_data["dig_P6"]
    var2 = var2 + ((var1 * cal_data["dig_P5"]) << 17)
    var2 = var2 + (cal_data["dig_P4"] << 35)
    var1 = ((var1 * var1 * cal_data["dig_P3"]) >> 8) + ((var1 * cal_data["dig_P2"]) << 12)
    var1 = (((1 << 47) + var1) * cal_data["dig_P1"]) >> 33
    if var1 == 0:
        return 0
    p = 1048576 - pressure_raw
    p = (((p << 31) - var2) * 3125) // var1
    var1 = (cal_data["dig_P9"] * (p >> 13) * (p >> 13)) >> 25
    var2 = (cal_data["dig_P8"] * p) >> 19
    p = ((p + var1 + var2) >> 8) + (cal_data["dig_P7"] << 4)
    return p / 256 / 100
