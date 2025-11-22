import serial.tools.list_ports
import base64, time
from pyfingerprint.pyfingerprint import PyFingerprint

class FingerScanner:
    def __init__(self, port="COM3", baudrate=57600):
        """Initialize fingerprint sensor — auto-detects ports if not specified"""
        available_ports = [str(p.device) for p in serial.tools.list_ports.comports()]

        if not available_ports:
            print("❌ No serial ports detected! Please check the USB connection.")
            self.f = None
            return

        if port is None:
            print("🔍 Available serial ports:", ", ".join(available_ports))
            port = available_ports[0]  # try the first available one automatically
            print(f"⚙️ Trying to connect to {port} ...")

        try:
            self.f = PyFingerprint(port, baudrate, 0xFFFFFFFF, 0x00000000)
            if not self.f.verifyPassword():
                raise ValueError("Fingerprint sensor password is wrong!")
            print(f"✅ Fingerprint sensor initialized successfully on {port}.")
        except Exception as e:
            print(f"❌ Failed to initialize fingerprint sensor on {port}: {e}")
            print("💡 Try unplugging and replugging the sensor, then re-run the program.")
            print("🔍 Available ports:", ", ".join(available_ports))
            self.f = None

    def enroll(self, user_id):
        """Enroll new fingerprint template"""
        if not self.f:
            return {"status": "fail", "message": "Fingerprint sensor not detected."}

        try:
            print("🖐️ Place your finger for enrollment...")
            while not self.f.readImage():
                pass

            self.f.convertImage(0x01)
            print("🖐️ Remove finger...")
            time.sleep(2)
            print("🖐️ Place the same finger again...")
            while not self.f.readImage():
                pass

            self.f.convertImage(0x02)

            if self.f.compareCharacteristics() == 0:
                print("❌ Fingers do not match.")
                return {"status": "fail", "message": "Fingers do not match."}

            self.f.createTemplate()
            template = self.f.downloadCharacteristics()
            encoded_template = base64.b64encode(bytes(template)).decode()

            position = self.f.storeTemplate()
            print(f"✅ Finger enrolled successfully at position {position}.")

            return {"status": "ok", "template": encoded_template}
        except Exception as e:
            return {"status": "fail", "message": f"Error enrolling: {e}"}

    def verify(self, user_id):
        """Verify fingerprint"""
        if not self.f:
            return {"status": "fail", "message": "Fingerprint sensor not detected."}

        try:
            print("🖐️ Place your finger for verification...")
            while not self.f.readImage():
                pass

            self.f.convertImage(0x01)
            result = self.f.searchTemplate()

            position = result[0]
            if position == -1:
                print("❌ No match found.")
                return {"status": "ok", "match": False}
            else:
                print(f"✅ Match found at position {position}.")
                return {"status": "ok", "match": True}
        except Exception as e:
            return {"status": "fail", "message": f"Verification error: {e}"}

    def close(self):
        """Close connection"""
        if self.f:
            print("🔌 Fingerprint scanner connection closed.")
