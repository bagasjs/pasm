"""
pasm_x86 - A simple incomplete assembler that target x86 architecture

REFERENCES:
[A] https://cdrdv2.intel.com/v1/dl/getContent/851063?fileName=325383-087-sdm-vol-2abcd.pdf
"""

# This is only for 16bit and 32bit registers
# Refer to table 2-1 at page 35 references A
AVAILABLE_REGISTERS = { 
   "ax": 0b000,
   "cx": 0b001,
   "dx": 0b010,
   "bx": 0b011,
   "sp": 0b100,
   "bp": 0b101,
   "si": 0b110,
   "di": 0b111,
}

def get_register_bits(r: str):
    if r[0] == "e":
        r = r[1:]
    return AVAILABLE_REGISTERS[r]

def is_valid_register(r: str):
    if r[0] == "e":
        r = r[1:]
    return r in AVAILABLE_REGISTERS

# Refer to figure 2-1 at page 31 references A
# Also Refer to figure 2-2 at page 34 references A for the calculation example
def modrm(dst: str, src: str, memory = False):
    assert is_valid_register(dst)
    assert is_valid_register(src)
    bits = 0b11
    if memory:
        bits = 0b00
    bits = bits << 6
    bits = bits | get_register_bits(src) << 3
    bits = bits | get_register_bits(dst)
    return bits

def assemble_source(source: str) -> bytes:
    lines = source.splitlines()
    binaries = []
    for i, line in enumerate(lines):
        line = line.strip()
        if len(line) == 0:
            continue
        if line.startswith("BITS"):
            continue

        inst = ""
        a = None
        b = None

        space_off = line.find(" ")
        if space_off == -1:
            inst = line
            line = ""
        else:
            inst = line[:space_off]
            line = line[space_off+1:]

        comma_off = line.find(",")
        if comma_off != -1:
            a = line[:comma_off]
            line = line[comma_off+1:]
        elif len(line) > 0:
            a = line
            line = ""

        line = line.strip()
        if len(line) > 0:
            b = line

        match inst:
            case "mov":
                assert isinstance(a, str)
                assert isinstance(b, str)
                if not is_valid_register(a):
                    print(f"ERROR: invalid register '{a}' at line {i+1}")
                    break

                if b.isdigit():
                    binaries.append(0xb8 + get_register_bits(a))
                    bpacked = int(b)
                    bunpacked = [
                         bpacked & 0xFF,
                        (bpacked >> 8) & 0xFF,
                        (bpacked >> 16) & 0xFF,
                        (bpacked >> 24) & 0xFF,
                    ]
                    binaries.extend(bunpacked)
                else:
                    binaries.append(0x89)
                    binaries.append(modrm(a, b))
            
            case "syscall":
                binaries.extend([0xF, 0x5])
                pass
            case _:
                print(f"ERROR: invalid or unsupported instruction {inst}({a}, {b}) at line {i+1}")

    return bytes(binaries)

import os
def output_file(filepath: str) -> str:
    basename = os.path.basename(filepath)
    filename = os.path.splitext(basename)[0]
    return f"{filename}.pasm.bin"

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("ERROR: Please provide an argument")

    input_file_path = sys.argv[1]
    with open(input_file_path, "r") as source_file:
        source = source_file.read()
        with open(output_file(input_file_path), "wb") as result_file:
            result_file.write(assemble_source(source))
