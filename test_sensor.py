from pyfingerprint.pyfingerprint import PyFingerprint
import time

PORT = 'COM5'        # Change this to your working COM port
BAUDRATE = 115200     # Or 115200 if that worked for you

try:
    print(f"🔍 Connecting to fingerprint sensor on {PORT} at {BAUDRATE} baud...")
    f = PyFingerprint(PORT, BAUDRATE, 0xFFFFFFFF, 0x00000000)

    if f.verifyPassword():
        print("✅ Sensor initialized successfully!")
    else:
        print("❌ Wrong password or communication issue.")
        exit()

    print("\n👉 Please place your finger on the sensor...")
    while not f.readImage():
        time.sleep(0.2)
    print("✅ Finger detected!")

    # Optional: convert to template and check storage
    f.convertImage(0x01)
    print("📄 Fingerprint image captured successfully!")

    print("\nNow remove your finger...")
    while f.readImage():
        time.sleep(0.2)
    print("🧠 Finger removed. Test complete.")

except Exception as e:
    print("\n⚠️ Error:", e)
