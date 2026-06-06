import subprocess
import sys

class OcrResult:
    def __init__(self, text: str, confidence: float):
        self.text = text
        self.confidence = confidence

class OcrEngine:
    def recognize(self, image_path: str) -> OcrResult:
        raise NotImplementedError()

class TesseractEngine(OcrEngine):
    def recognize(self, image_path: str) -> OcrResult:
        try:
            result = subprocess.run(
                ["tesseract", image_path, "stdout", "-l", "jpn", "--psm", "6"],
                capture_output=True,
                text=True,
                check=True
            )
            text = result.stdout.strip()
            confidence = 1.0 if text else 0.0
            return OcrResult(text, confidence)
        except subprocess.CalledProcessError as e:
            print(f"Tesseract failed: {e.stderr}", file=sys.stderr)
            raise RuntimeError(f"Tesseract failed: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError("Failed to execute tesseract. Is it installed?")
