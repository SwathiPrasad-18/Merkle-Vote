from pyfingerprint.pyfingerprint import PyFingerprint

for baud in [57600, 115200, 19200, 38400, 9600]:
    try:
        print(f"Trying COM3 at {baud} baud...")
        f = PyFingerprint('COM3', baud, 0xFFFFFFFF, 0x00000000)
        if f.verifyPassword():
            print(f"✅ Fingerprint sensor detected at {baud} baud.")
            break
        else:
            print("❌ Wrong password or communication error.")
    except Exception as e:
        print(f"❌ Failed at baud {baud}:", e)
