"""Capture a real screenshot of the local dashboard using headless Chromium."""
import base64
import io
import subprocess
import sys
import time
from urllib.request import urlopen

from PIL import Image
from playwright.sync_api import sync_playwright


def main():
    process = subprocess.Popen(
        [sys.executable, "standalone_dashboard.py", "--port", "8765"],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
    )
    try:
        for _ in range(50):
            if process.poll() is not None:
                raise RuntimeError("Dashboard process exited unexpectedly")
            try:
                with urlopen("http://127.0.0.1:8765/health", timeout=1) as response:
                    if response.status == 200:
                        break
            except OSError:
                time.sleep(0.2)
        else:
            raise RuntimeError("Dashboard did not start on 127.0.0.1:8765")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1250, "height": 880}, device_scale_factor=1)
            page.goto("http://127.0.0.1:8765/", wait_until="networkidle")
            page.wait_for_function("document.getElementById('count').textContent === '10'")
            page.screenshot(path="docs/screenshot.png", full_page=True, animations="disabled")
            browser.close()
        image = Image.open("docs/screenshot.png")
        image.thumbnail((1100, 950))
        data = io.BytesIO()
        image.convert("P", palette=1, colors=96).save(data, "PNG", optimize=True)
        print("RESCUE_SCREENSHOT_BASE64=" + base64.b64encode(data.getvalue()).decode("ascii"))
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


if __name__ == "__main__":
    main()
