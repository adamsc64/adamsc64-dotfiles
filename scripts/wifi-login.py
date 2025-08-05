#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import requests

LOGIN_URL = "https://tawny-owl-captive-portal.it.ox.ac.uk:8003/index.php?zone=tawny_owl"
CHECK_URL = "https://www.google.com"

OWL_USERNAME = os.getenv("OWL_USERNAME")
OWL_PASSWORD = os.getenv("OWL_PASSWORD")

def fail(msg, code=1):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(code)

def get_ssid():
    try:
        out = subprocess.check_output(
            ["/usr/sbin/networksetup", "-getairportnetwork", "en0"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        # Expected: "Current Wi-Fi Network: OWL"
        return out.split(": ", 1)[1].strip()
    except Exception:
        return ""

def check_internet(url=CHECK_URL, timeout=2):
    try:
        # HEAD request with status check
        resp = requests.head(url, timeout=timeout, allow_redirects=True)
        return resp.status_code >= 200 and resp.status_code < 300
    except requests.RequestException:
        return False

def login_captive_portal(username, password, max_attempts=5, base_delay=2):
    session = requests.Session()
    for attempt in range(1, max_attempts + 1):
        print(f"Login attempt {attempt} of {max_attempts}...")
        try:
            resp = session.post(
                LOGIN_URL,
                data={
                    "auth_user": username,
                    "auth_pass": password,
                    "accept": "Continue",
                    "redirurl": "",
                    "zone": "tawny_owl",
                },
                timeout=10,
                verify=False,  # mirrors -k
            )
        except requests.RequestException:
            print("Login POST failed or timed out.")
        else:
            if check_internet():
                print("Login succeeded and internet is reachable.")
                return True
            else:
                print("Login POST succeeded but internet not reachable.")
        if attempt < max_attempts:
            time.sleep(base_delay * attempt)
    return False

def main():
    if not (OWL_USERNAME and OWL_PASSWORD):
        fail("OWL_USERNAME and OWL_PASSWORD environment variables must be set.")

    print("Checking current Wi-Fi network...")
    ssid = get_ssid()
    if ssid != "OWL":
        print("Not on OWL network. Aborting.")
        return

    print("Checking if internet is already accessible...")
    if check_internet():
        print("Internet is already accessible.")
        return

    print("Attempting to log in to the OWL captive portal...")
    success = login_captive_portal(OWL_USERNAME, OWL_PASSWORD)
    if not success:
        fail("Failed to log in after attempts.")
    print("Login attempt complete.")

if __name__ == "__main__":
    main()