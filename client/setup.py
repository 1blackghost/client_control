import subprocess
import sys
import os

def compile_to_executable(script_name, output_name, icon_path=None):
    command = ['pyinstaller', '--onefile', script_name, '-n', output_name]

    if icon_path:
        command.extend(['--icon', icon_path])

    subprocess.run(command, check=True)

if __name__ == "__main__":
    # Customize these variables
    script_to_compile = "main.py"
    output_executable_name = "Youtube Automation"
    icon_path = "icon.png"  # Replace with the actual path to your .ico file

    # Compile the script to an executable with an icon
    compile_to_executable(script_to_compile, output_executable_name, icon_path)
