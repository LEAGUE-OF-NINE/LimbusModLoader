import io
import sys
import struct

from patch import *
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(stream=sys.stdout)
    ]
)

def read_int32(file) -> int:
    # Read the 4-byte length (little-endian 32-bit integer)
    length_data = file.read(4)
    if len(length_data) < 4:
        raise ValueError("File is corrupted or incomplete")

    return struct.unpack('<I', length_data)[0]

def read_chunk(file):
    # Read the 4-byte identifier
    identifier = file.read(4)
    if len(identifier) < 4:
        return None  # End of file reached

    # Read the 4-byte length (little-endian 32-bit integer)
    length = read_int32(file)

    # Read the chunk data
    chunk_data = file.read(length)
    if len(chunk_data) < length:
        raise ValueError("File is corrupted or incomplete")

    # Read the pad byte if the length is odd
    if length % 2 != 0:
        pad_byte = file.read(1)
        if len(pad_byte) < 1:
            raise ValueError("File is corrupted or incomplete")

    return identifier, length, chunk_data

def dump_chunks(file):
    while True:
        chunk = read_chunk(file)
        if chunk is None:
            break  # End of file reached

        identifier, length, chunk_data = chunk
        print(f"Identifier: {identifier.decode('ascii')}")
        print(f"Length: {length}")
        print(f"Data: {chunk_data[:min(20, len(chunk_data))]}...")  # Print only the first 20 bytes of data
        print()
        if identifier == b'RIFF':
            sub_file = io.BytesIO(chunk_data)
            dump_chunks(sub_file)

def dump_bank(file):
    # Read the 4-byte identifier
    identifier = file.read(4)
    if len(identifier) < 4:
        return None  # End of file reached

    assert identifier == b"RIFF"

    # Read the 4-byte length (little-endian 32-bit integer)
    length = read_int32(file)

    # Read the chunk data
    chunk_data = file.read(length)
    if len(chunk_data) < length:
        raise ValueError("File is corrupted or incomplete")

    sub_file = io.BytesIO(chunk_data)

    # Read the 4-byte identifier
    identifier = sub_file.read(4)
    if len(identifier) < 4:
        return None  # End of file reached

    assert identifier == b"FEV "
    dump_chunks(sub_file)

def __main__():
    with open(os.getenv("BANK_FILE"), 'rb') as f:
        dump_bank(f)

__main__()