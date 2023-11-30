from cx_Freeze import setup, Executable
setup(
    name="Quant Biometric",
    version="1.0",
    description="This is Biometric sync app",
   executables=[Executable("app_gui.py", base="Win32GUI")],
)

