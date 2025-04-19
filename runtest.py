import os
import subprocess

SILENT = True

if not os.path.isdir("build"):
    os.mkdir("build")

def cmd(command: list[str], show_stdout = False, show_stderr = True) -> bool:
    if not SILENT:
        print(command)
    result = subprocess.run(command, 
                            stdout=subprocess.PIPE if not show_stdout else None, 
                            stderr=subprocess.PIPE if not show_stderr else None,
                            text=True)
    return result.returncode == 0

def main():
    tests_dir = "tests"
    build_dir = "build"

    for file in os.listdir(tests_dir):
        basename = os.path.basename(file)
        filename = os.path.splitext(basename)[0]
        source_file = os.path.join(tests_dir, file)

        nasm_output = os.path.join(build_dir, f"{filename}.nasm.bin")
        pasm_output = os.path.join(build_dir, f"{filename}.pasm.bin")
        if not cmd(["nasm", "-fbin", "-o", nasm_output, source_file], show_stderr=True):
            return
        if not cmd(["python", "pasm_x86.py",  source_file], show_stderr=True):
            return 

        if cmd(["diff", nasm_output, pasm_output]):
            print(f"+ {file} passed")
        else:
            print(f"+ {file} error")
            print(f"Disassembled {nasm_output}")
            cmd(["ndisasm", "-b32", nasm_output], show_stdout=True)
            print(f"Disassembled {pasm_output}")
            cmd(["ndisasm", "-b32", pasm_output], show_stdout=True)
            
        os.replace(f"{filename}.pasm.bin", pasm_output)

if __name__ == "__main__":
    main()
    pass

