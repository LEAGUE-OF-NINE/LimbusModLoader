import glob
import io
import sys
import struct
from typing import Optional

import fsb5

from patch import *
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(stream=sys.stdout)
    ]
)

class Chunk:
    def __init__(self, identifier: bytes, padding: int, data: bytes):
        self.identifier = identifier
        self.padding = padding
        self.data = data

class Bank:
    def __init__(self, fmt_chunk: Chunk, list_chunk: Chunk, snd_chunks: [Chunk]):
        self.fmt_chunk = fmt_chunk
        self.list_chunk = list_chunk
        self.snd_chunks = snd_chunks

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

    # Read the pad byte if the length is odd
    if length % 2 != 0:
        file.read(1)

    return identifier, length, chunk_data

def skip_zeros(chunk_data):
    # Skip the padding zeros
    for i in range(len(chunk_data)):
        if chunk_data[i] != 0:
            return chunk_data[i:]

    return b""

def dump_chunks(file) -> [Chunk] :
    chunks = []
    while True:
        chunk = None

        try:
            chunk = read_chunk(file)
        except Exception as e:
            logging.debug("Error reading chunk: %s", e)
            pass

        if chunk is None:
            return chunks

        identifier, length, chunk_data = chunk
        chunk_data = skip_zeros(chunk_data)
        zero_pad = length - len(chunk_data)
        length = len(chunk_data)

        logging.debug(f"Identifier: {identifier.decode('ascii')}")
        logging.debug(f"Length: {length}")
        logging.debug(f"Zero padding: {zero_pad}")
        logging.debug(f"Data: {chunk_data[:min(20, len(chunk_data))]}...")  # Print only the first 20 bytes of data

        chunks.append(Chunk(identifier, zero_pad, chunk_data))

def dump_bank(file) -> Optional[Bank]:
    # Read the 4-byte identifier
    identifier = file.read(4)
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
    assert identifier == b"FEV "

    chunks = dump_chunks(sub_file)
    if len(chunks) < 2:
        raise ValueError("Invalid bank file, too little chunks")

    assert chunks[0].identifier == b"FMT "
    assert chunks[1].identifier == b"LIST"
    for chunk in chunks[2:]:
        assert chunk.identifier == b"SND "

    return Bank(chunks[0], chunks[1], chunks[2:])

def __main__():
    for path in glob.glob(os.getenv("BANK_FILE") + "/*.bank"):
        with open(path, 'rb') as f:
            try:
                bank = dump_bank(f)
                name = os.path.basename(path)
                i = 0
                logging.info(f"Processing {name}")
                for chunk in bank.snd_chunks:
                    logging.info(f"- Processing {name}, chunk {i}")
                    with open(f"dump/{name}_{i}.fsb", "wb") as fsb:
                        fsb.write(chunk.data)
                    i += 1

                    fsb = fsb5.FSB5(chunk.data)
                    ext = fsb.get_sample_extension()

                    # iterate over samples
                    for sample in fsb.samples:
                        # print sample properties
                        logging.info('''- {sample.name}.{extension}'''.format(sample=sample, extension=ext))
            except Exception as e:
                logging.info(f"- Error processing {path} {e}")

__main__()