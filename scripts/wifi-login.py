#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import requests
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import urllib3
from abc import ABC, abstractmethod


LOGIN_URL = "https://tawny-owl-captive-portal.it.ox.ac.uk:8003/index.php?zone=tawny_owl"
NEVERSSL = "http://neverssl.com/"
GSTATIC_204 = "http://www.gstatic.com/generate_204"

OWL_USERNAME = os.getenv("OWL_USERNAME")
OWL_PASSWORD = os.getenv("OWL_PASSWORD")
BOD_USERNAME = os.getenv("BOD_USERNAME")
BOD_PASSWORD = os.getenv("BOD_PASSWORD")
HARVARD_ACCESS_CODE = os.getenv("HARVARD_ACCESS_CODE")

# Network constants
OWL_NETWORK = "OWL"
BODLEIAN_NETWORK = "Bodleian-Libraries"
HARVARD_NETWORK = "Harvard Club"


class WiFiNetwork(ABC):
    @abstractmethod
    def get_credentials(self) -> tuple:
        """Return (username, password) or equivalent credentials"""
        pass

    @abstractmethod
    def login(self) -> bool:
        """Perform network-specific login. Return True if successful."""
        pass


class Owl(WiFiNetwork):
    def get_credentials(self):
        if not (OWL_USERNAME and OWL_PASSWORD):
            fail("OWL_USERNAME and OWL_PASSWORD environment variables must be set.")
        return OWL_USERNAME, OWL_PASSWORD

    def login(self):
        """Handle login for OWL network"""
        username, password = self.get_credentials()
        print("Attempting to log in to the OWL captive portal...")
        success = login_captive_portal(username, password)
        if success:
            print("OWL login attempt complete.")
        return success


class Bodleian(WiFiNetwork):
    def get_credentials(self):
        if not (BOD_USERNAME and BOD_PASSWORD):
            fail("BOD_USERNAME and BOD_PASSWORD environment variables must be set.")
        return BOD_USERNAME, BOD_PASSWORD

    def login(self):
        """Handle login for Bodleian Libraries network"""
        username, password = self.get_credentials()
        print("Attempting to log in to the Bodleian captive portal...")
        if not login_bodleian_portal(username, password):
            fail("Failed to log in to Bodleian portal after attempts.")
        print("Bodleian login attempt complete.")


class Harvard(WiFiNetwork):
    def get_credentials(self):
        if not HARVARD_ACCESS_CODE:
            fail("HARVARD_ACCESS_CODE environment variable must be set.")
        return (HARVARD_ACCESS_CODE,)

    def login(self):
        """Handle login for Harvard Club network using SkyAdmin portal"""
        (access_code,) = self.get_credentials()

        print("Attempting to log in to the Harvard Club captive portal...")

        # Get dynamic network information
        mac_address = get_mac_address()
        ip_address = get_ip_address()

        if not mac_address:
            fail("Could not determine MAC address for network interface")

        if not ip_address:
            fail("Could not determine IP address for network interface")

        print(f"Using MAC address: {mac_address}")
        print(f"Using IP address: {ip_address}")

        # The payload from the curl request
        payload = {
            "nseid": "0a1000",
            "property_id": 5175,
            "gateway_slug": None,
            "location_index": None,
            "ppli": None,
            "vlan_id": 10353,
            "mac_address": mac_address,
            "ip_address": ip_address,
            "registration_method_id": 4,
            "access_code": access_code,
        }

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://splash.skyadmin.io",
            "Referer": "https://splash.skyadmin.io/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            "api-token": "n0faQedrepaqusu2uzur1chisijuqAxe",
            "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
        }

        try:
            response = requests.post(
                "https://skyadmin.io/api/portalregistrations",
                json=payload,
                headers=headers,
                timeout=10,
            )

            if response.status_code == 200:
                print("Harvard Club portal registration successful.")
                # Wait a moment then check internet
                time.sleep(3)
                print("Checking internet...")
                if check_internet():
                    print("Harvard Club login succeeded and internet is reachable.")
                    return True
                else:
                    print("Registration succeeded but internet not reachable yet.")
            else:
                print(
                    f"Harvard Club portal registration failed: {response.status_code}"
                )
                print(f"Response: {response.text}")

        except requests.RequestException as exc:
            print(f"Harvard Club login failed: {exc}")

        return False


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
    except Exception:  # intentional broad catch
        return ""


def get_mac_address(interface="en0"):
    """Get the MAC address of the specified network interface"""
    try:
        out = subprocess.check_output(
            ["/sbin/ifconfig", interface],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        # Look for line containing "ether" followed by MAC address
        for line in out.split("\n"):
            if "ether" in line:
                mac = line.split()[1]
                # Remove colons and convert to uppercase to match expected format
                return mac.replace(":", "").upper()
    except Exception:
        pass
    return None


def get_ip_address(interface="en0"):
    """Get the IP address of the specified network interface"""
    try:
        out = subprocess.check_output(
            ["/usr/sbin/ipconfig", "getifaddr", interface],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return out.strip()
    except Exception:
        pass
    return None


# Confirm that we have actual internet access
def check_internet(url=NEVERSSL, timeout=3):
    try:
        resp = requests.get(url, timeout=timeout, allow_redirects=False)
        # Bodleian is sneaky; they return HTTP 200 with a javascript redirect
        # So we check for actual content.
        if "NeverSSL" in resp.text:
            return True
        return resp.status_code == 200
    except requests.RequestException:
        return False


def login_bodleian_portal(username, password):
    """Login to Bodleian Reader WiFi network"""
    session = requests.Session()
    print(f"Bodleian login attempt...")
    try:
        if make_attempt(session, username, password):
            return True
    except ConnectionError:
        print("Connection error during attempt.")
    return False


def make_attempt(session, username, password):
    # Step 1: Make request to generate_204 to get redirect
    print("Making initial request to detect captive portal...")
    resp = session.get(GSTATIC_204, timeout=10, allow_redirects=False)

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
    print("Form submitted, waiting to verify internet access...")
    time.sleep(5)

    # Step 5: Check if login succeeded
    if check_internet():
        print("Bodleian login succeeded and internet is reachable.")
        return True
    print("Form submitted but internet not reachable yet.")
    return False


def login_captive_portal(username, password):
    session = requests.Session()
    print(f"Login attempt...")
    try:
        resp = session.post(
            LOGIN_URL,
            data={
                "auth_user": username,
                "auth_pass": password,
                "accept": "Continue",
                "redirurl": "http://www.gstatic.com/generate_204",
                "zone": "tawny_owl",
            },
            timeout=5,
            verify=False,  # mirrors -k
        )
    except requests.RequestException as exc:
        print("Login POST failed or timed out.")
        return False
    if check_internet():
        print("Login succeeded and internet is reachable.")
        return True
    else:
        print("Login POST succeeded but internet not reachable.")
        print(f"Is username {username} still right?")
    return False


def disable_ssl_warnings():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    disable_ssl_warnings()

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
        OWL_NETWORK: Owl,
        BODLEIAN_NETWORK: Bodleian,
        HARVARD_NETWORK: Harvard,
    }

    klass = networks.get(ssid)
    if not klass:
        supported = ", ".join(networks.keys())
        print(f"Not on a supported network (current: '{ssid}'). Supported: {supported}")
        return

    network = klass()
    while True:
        print(f"Attempting to log into network: {ssid}")
        if network.login():
            break
        time.sleep(2)


if __name__ == "__main__":
    main()
