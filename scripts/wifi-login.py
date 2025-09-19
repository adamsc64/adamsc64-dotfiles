#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import requests
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup

LOGIN_URL = "https://tawny-owl-captive-portal.it.ox.ac.uk:8003/index.php?zone=tawny_owl"
CHECK_URL = "https://www.google.com"
BOD_CHECK_URL = "http://www.gstatic.com/generate_204"

OWL_USERNAME = os.getenv("OWL_USERNAME")
OWL_PASSWORD = os.getenv("OWL_PASSWORD")
BOD_USERNAME = os.getenv("BOD_USERNAME")
BOD_PASSWORD = os.getenv("BOD_PASSWORD")

# Network constants
OWL_NETWORK = "OWL"
BODLEIAN_NETWORK = "Bodleian-Libraries"


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


def login_bodleian_portal(username, password, max_attempts=5, base_delay=2):
    """Login to Bodleian Reader WiFi network"""
    session = requests.Session()
    for attempt in range(1, max_attempts + 1):
        print(f"Bodleian login attempt {attempt} of {max_attempts}...")
        try:
            if make_attempt(session, username, password):
                return True
        except ConnectionError:
            print("Connection error during attempt.")
        if attempt < max_attempts:
            time.sleep(base_delay * attempt)
    return False


def make_attempt(session, username, password):
    # Step 1: Make request to generate_204 to get redirect
    print("Making initial request to detect captive portal...")
    resp = session.get(BOD_CHECK_URL, timeout=10, allow_redirects=False)

    if resp.status_code != 200:
        print("Initial request failed")
        return False

    if not b"window.location" in resp.content:
        print("HTTP 200 but no window.location")
        return False

    print("Redirect detected")
    tokenized_url = resp.content.split(b"window.location=")[1].split(b";")[0]
    redirect_url = tokenized_url.decode("utf-8")
    redirect_url = redirect_url.strip('"')
    print(f"Redirecting to: {redirect_url}")

    # Step 2: Follow redirect to get auth form
    if not redirect_url:
        return False

    print(f"Following redirect to: {redirect_url}")
    resp = session.get(redirect_url, timeout=10)

    # Step 3: Parse the form to extract hidden values
    soup = BeautifulSoup(resp.text, "html.parser")
    form = soup.find("form", {"method": "post"})

    if not form:
        print("Could not find login form")
        return False

    # Extract hidden form values
    form_data = {}
    for input_tag in form.find_all("input", type="hidden"):
        name = input_tag.get("name", "")
        value = input_tag.get("value", "")
        if name:  # Only add if name is not empty
            form_data[name] = value

    # Add username and password
    form_data["username"] = username
    form_data["password"] = password

    print(f"Submitting form...")

    # Step 4: Submit the form
    action = form.get("action", "/")
    if action.startswith("/"):
        # Relative URL - construct full URL
        parsed_url = urlparse(redirect_url)
        submit_url = f"{parsed_url.scheme}://{parsed_url.netloc}{action}"
    else:
        submit_url = action

    resp = session.post(submit_url, data=form_data, timeout=10)

    # Step 5: Check if login succeeded
    if check_internet():
        print("Bodleian login succeeded and internet is reachable.")
        return True
    else:
        print("Form submitted but internet not reachable yet.")


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


def login_to_owl():
    """Handle login for OWL network"""
    if not (OWL_USERNAME and OWL_PASSWORD):
        fail("OWL_USERNAME and OWL_PASSWORD environment variables must be set.")

    print("Checking if internet is already accessible...")
    if check_internet():
        print("Internet is already accessible.")
        return

    print("Attempting to log in to the OWL captive portal...")
    success = login_captive_portal(OWL_USERNAME, OWL_PASSWORD)
    if not success:
        fail("Failed to log in after attempts.")
    print("OWL login attempt complete.")


def login_to_bodleian():
    """Handle login for Bodleian Libraries network"""
    if not (BOD_USERNAME and BOD_PASSWORD):
        fail("BOD_USERNAME and BOD_PASSWORD environment variables must be set.")
    print("Attempting to log in to the Bodleian captive portal...")
    if not login_bodleian_portal(BOD_USERNAME, BOD_PASSWORD):
        fail("Failed to log in to Bodleian portal after attempts.")
    print("Bodleian login attempt complete.")


def main():
    print("Checking if internet is already accessible...")
    if check_internet():
        print("Internet is already accessible.")
        return

    print("Checking current Wi-Fi network...")
    ssid = get_ssid()
    if not ssid:
        print("No network seems available.")
        return

    # Network handler mapping
    networks = {
        OWL_NETWORK: login_to_owl,
        BODLEIAN_NETWORK: login_to_bodleian,
    }

    handler = networks.get(ssid)
    if not handler:
        supported = ", ".join(networks.keys())
        print(
            f"Not on a supported network (current: '{ssid}'). Supported: {supported}"
        )
        return
    handler()


if __name__ == "__main__":
    main()
