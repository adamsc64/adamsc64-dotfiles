#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import urllib3
from abc import ABC, abstractmethod

GSTATIC_204 = "http://www.gstatic.com/generate_204"


class WiFiNetwork(ABC):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Skip SSID validation for intermediate base class
        if cls.__name__ == "SkyAdminNetwork":
            return
        if not hasattr(cls, "SSID") or cls.SSID is None:
            raise TypeError(f"Class {cls.__name__} must define SSID class variable")

    @abstractmethod
    def get_credentials(self) -> dict:
        """Return dict mapping HTTP parameter names to credential values"""
        pass

    @abstractmethod
    def login(self) -> bool:
        """Perform network-specific login. Return True if successful."""
        pass


class Owl(WiFiNetwork):
    SSID = "OWL"

    def get_credentials(self):
        username = os.getenv("OWL_USERNAME")
        password = os.getenv("OWL_PASSWORD")
        if not (username and password):
            fail("OWL_USERNAME and OWL_PASSWORD environment variables must be set.")
        return {"auth_user": username, "auth_pass": password}

    def login(self):
        """Handle login for OWL network"""
        credentials = self.get_credentials()
        print("Attempting to log in to the OWL captive portal...")
        success = self.login_captive_portal(credentials)
        if success:
            print("OWL login attempt complete.")
        return success

    def login_captive_portal(self, credentials):
        LOGIN_URL = (
            "https://tawny-owl-captive-portal.it.ox.ac.uk:8003/index.php?zone=tawny_owl"
        )

        session = requests.Session()
        print(f"Login attempt...")
        try:
            resp = session.post(
                LOGIN_URL,
                data={
                    "auth_user": credentials["auth_user"],
                    "auth_pass": credentials["auth_pass"],
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
            print(f"Is username {credentials['auth_user']} still right?")
        return False


class Bodleian(WiFiNetwork):
    SSID = "Bodleian-Libraries"

    def get_credentials(self):
        username = os.getenv("BOD_USERNAME")
        password = os.getenv("BOD_PASSWORD")
        if not (username and password):
            fail("BOD_USERNAME and BOD_PASSWORD environment variables must be set.")
        return {"username": username, "password": password}

    def login(self):
        """Handle login for Bodleian Libraries network"""
        credentials = self.get_credentials()
        print("Attempting to log in to the Bodleian captive portal...")
        if not self.login_bodleian_portal(credentials):
            print("Failed to log in to Bodleian portal.")
            return False
        print("Bodleian login attempt complete.")
        return True

    def login_bodleian_portal(self, credentials):
        """Login to Bodleian Reader WiFi network"""
        session = requests.Session()
        print(f"Bodleian login attempt...")
        try:
            if self.make_attempt(session, credentials):
                return True
        except ConnectionError:
            print("Connection error during attempt.")
        return False

    def make_attempt(self, session, credentials):
        # Step 1: Make request to generate_204 to get redirect
        print("Making initial request to detect captive portal...")
        resp = session.get(GSTATIC_204, timeout=10, allow_redirects=False)
        if resp.status_code == 204:
            print("No captive portal detected; internet is accessible.")
            return True  # Already have internet
        if resp.status_code != 200:
            print("Initial request failed")
            return False

        if b"window.location" not in resp.content:
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
        form_data["username"] = credentials["username"]
        form_data["password"] = credentials["password"]

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


class SkyAdminNetwork(WiFiNetwork):
    """Base class for networks using SkyAdmin portal authentication"""

    # Subclasses must define these
    NSEID = None
    PROPERTY_ID = None
    VLAN_ID = None
    ENV_VAR = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # SkyAdminNetwork subclasses must define all these fields including SSID
        required = ["SSID", "NSEID", "PROPERTY_ID", "VLAN_ID", "ENV_VAR"]
        for attr in required:
            if not hasattr(cls, attr) or getattr(cls, attr) is None:
                raise TypeError(
                    f"Class {cls.__name__} must define {attr} class variable"
                )

    def get_credentials(self):
        access_code = os.getenv(self.ENV_VAR)
        if not access_code:
            fail(f"{self.ENV_VAR} environment variable must be set.")
        return {"access_code": access_code}

    def login(self):
        """Handle login for SkyAdmin-based network portal"""
        credentials = self.get_credentials()

        print(f"Attempting to log in to the {self.SSID} captive portal...")

        # Get dynamic network information
        mac_address = get_mac_address()
        ip_address = get_ip_address()

        if not mac_address:
            fail("Could not determine MAC address for network interface")

        if not ip_address:
            fail("Could not determine IP address for network interface")

        print(f"Using MAC address: {mac_address}")
        print(f"Using IP address: {ip_address}")

        # Build payload with network-specific configuration
        payload = {
            "nseid": self.NSEID,
            "property_id": self.PROPERTY_ID,
            "gateway_slug": None,
            "location_index": None,
            "ppli": None,
            "vlan_id": self.VLAN_ID,
            "mac_address": mac_address,
            "ip_address": ip_address,
            "registration_method_id": 4,
        }
        payload.update(credentials)

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

            # Check for invalid access code
            invalid = "This access code is invalid at this time." in str(
                response.content
            )
            if invalid:
                access_code = credentials.get("access_code", "")
                fail(f"Access code {access_code} needs to be rotated.")

            if response.status_code == 200:
                print(f"{self.SSID} portal registration successful.")
                # Wait a moment then check internet
                time.sleep(3)
                print("Checking internet...")
                if check_internet():
                    print(f"{self.SSID} login succeeded and internet is reachable.")
                    return True
                else:
                    print("Registration succeeded but internet not reachable yet.")
            else:
                print(f"{self.SSID} portal registration failed: {response.status_code}")
                print(f"Response: {response.text}")

        except requests.RequestException as exc:
            print(f"{self.SSID} login failed: {exc}")

        return False


class HarvardClub(SkyAdminNetwork):
    SSID = "Harvard Club"
    NSEID = "0a1000"
    PROPERTY_ID = 5175
    VLAN_ID = 10353
    ENV_VAR = "HARVARD_ACCESS_CODE"


class YaleClub(SkyAdminNetwork):
    SSID = "The Yale Club NYC"
    NSEID = "046064"
    PROPERTY_ID = 6106
    VLAN_ID = 20864
    ENV_VAR = "YALE_ACCESS_CODE"


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
def check_internet(timeout=3):
    JS_REDIRECT = 'window.location="https://bodreader.bodleian.ox.ac.uk'
    try:
        resp = requests.get(GSTATIC_204, timeout=timeout, allow_redirects=False)
        # Bodleian is sneaky; they return HTTP 200 with a javascript redirect
        # So we check for actual content.
        if JS_REDIRECT in resp.text:
            return False
        return resp.status_code == 204
    except requests.RequestException:
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

    # Build network handler mapping from classes
    networks = {
        Owl.SSID: Owl,
        Bodleian.SSID: Bodleian,
        HarvardClub.SSID: HarvardClub,
        YaleClub.SSID: YaleClub,
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
