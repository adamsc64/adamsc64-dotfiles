#!/usr/bin/env python3
import hashlib
import os
import re
import subprocess
import sys
import time
from abc import ABC, abstractmethod
from typing import Any, Optional
from urllib.parse import urlparse

import requests
import urllib3
from bs4 import BeautifulSoup

GSTATIC_204 = "http://www.gstatic.com/generate_204"
DEFAULT_TIMEOUT = 5


def safe_request(
    method: str,
    url: str,
    session: Optional[requests.Session] = None,
    error_msg: Optional[str] = None,
    **kwargs: Any,
) -> Optional[requests.Response]:
    """
    Wrapper for requests/session get/post with consistent error handling.
    """
    kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
    kwargs.setdefault("verify", False)  # mirrors -k

    try:
        requester = session if session else requests
        if method.lower() == "get":
            return requester.get(url, **kwargs)
        elif method.lower() == "post":
            return requester.post(url, **kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")
    except requests.RequestException as exc:
        prefix = error_msg if error_msg else "Request failed"
        print(f"{prefix}: {exc}")
        return None


def safe_get(*args, **kwargs) -> Optional[requests.Response]:
    return safe_request("get", *args, **kwargs)


def safe_post(*args, **kwargs) -> Optional[requests.Response]:
    return safe_request("post", *args, **kwargs)


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
        resp = safe_post(
            LOGIN_URL,
            session=session,
            error_msg="Login POST failed or timed out",
            data={
                "auth_user": credentials["auth_user"],
                "auth_pass": credentials["auth_pass"],
                "accept": "Continue",
                "redirurl": "http://www.gstatic.com/generate_204",
                "zone": "tawny_owl",
            },
        )
        if not resp:
            return False

        if check_internet():
            print("Login succeeded and internet is reachable.")
            return True
        else:
            print("Login POST succeeded but internet not reachable.")
            fail(f"Is username {credentials['auth_user']} still right?")
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
        # Set browser-like headers to avoid captive portal blocking
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )
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
        print(f"  Requesting: {GSTATIC_204}")
        resp = safe_get(
            GSTATIC_204,
            session=session,
            error_msg="Initial request failed",
            allow_redirects=False,
        )
        if not resp:
            return False

        print(f"Initial response status: {resp.status_code}")
        print(f"Initial response URL: {resp.url}")
        print(f"Initial response headers: {dict(resp.headers)}")
        print(f"Initial response body (first 500 chars): {resp.text[:500]}")

        # Store the actual captive portal URL that responded
        captive_portal_url = resp.url
        print(f"Captive portal responded from: {captive_portal_url}")

        if resp.status_code == 204:
            print("No captive portal detected; internet is accessible.")
            return True  # Already have internet

        # Handle HTTP redirects (302, 303, etc.)
        if resp.status_code in (301, 302, 303, 307, 308):
            redirect_url = resp.headers.get("Location")
            if redirect_url:
                print(f"HTTP redirect detected to: {redirect_url}")
                print(f"Following redirect to: {redirect_url}")
                resp = safe_get(
                    redirect_url,
                    session=session,
                    error_msg="Failed to follow redirect",
                )
                if not resp:
                    return False
                print(f"After HTTP redirect - status: {resp.status_code}")
                print(
                    f"After HTTP redirect - body (first 500 chars): {resp.text[:500]}"
                )
            else:
                print("HTTP redirect without Location header")
                return False
        # Handle JavaScript redirects
        elif resp.status_code == 200 and b"window.location" in resp.content:
            print("\n=== JavaScript redirect detected ===")
            tokenized_url = resp.content.split(b"window.location=")[1].split(b";")[0]
            redirect_url = tokenized_url.decode("utf-8")
            redirect_url = redirect_url.strip('"')
            print(f"Redirect URL from JS: {redirect_url}")
            print(f"Captive portal URL was: {captive_portal_url}")

            # Try to resolve the hostname to see what IP it points to
            parsed_redirect = urlparse(redirect_url)
            hostname = parsed_redirect.hostname
            print(f"\nChecking DNS resolution for: {hostname}")
            try:
                import socket

                ip_address = socket.gethostbyname(hostname)
                print(f"  Resolved to IP: {ip_address}")
            except socket.gaierror as e:
                print(f"  DNS resolution failed: {e}")
                ip_address = None

            # The JS redirect URL might not be accessible directly
            # Instead, try making another request to the captive portal that responded
            print(f"\nAttempt 1: Requesting the JS redirect URL directly...")
            print(f"  URL: {redirect_url}")
            resp = safe_get(
                redirect_url,
                session=session,
                error_msg="Failed to get login form via HTTPS",
                allow_redirects=True,
            )

            # If HTTPS fails and the URL was HTTPS, try HTTP
            if not resp and redirect_url.startswith("https://"):
                http_url = "http://" + redirect_url[8:]
                print(f"\nAttempt 2: HTTPS failed, trying HTTP fallback...")
                print(f"  URL: {http_url}")
                resp = safe_get(
                    http_url,
                    session=session,
                    error_msg="Failed to get login form via HTTP",
                    allow_redirects=True,
                )

            # If both failed, try requesting the captive portal URL with redirects
            if not resp:
                print(
                    f"\nAttempt 3: Requesting captive portal URL with redirects enabled..."
                )
                print(f"  URL: {captive_portal_url}")
                resp = safe_get(
                    captive_portal_url,
                    session=session,
                    error_msg="Failed to get captive portal with redirects",
                    allow_redirects=True,
                )
                if resp:
                    print(
                        f"  Got response - checking if it's the form or another redirect..."
                    )
                    print(
                        f"  Contains window.location: {b'window.location' in resp.content}"
                    )
                    print(f"  Contains <form>: {b'<form' in resp.content}")

            if not resp:
                print("\nAll attempts to get login form failed!")
                return False

            print(f"\n=== Got response ===")
            print(f"Status: {resp.status_code}")
            print(f"URL: {resp.url}")
            print(f"Headers: {dict(resp.headers)}")
            print(f"Body (first 1000 chars): {resp.text[:1000]}")
            print(f"Contains <form> tag: {b'<form' in resp.content}")
        # Handle direct form presentation (no redirect)
        elif resp.status_code == 200:
            print("Direct form presentation detected (no redirect)")
            # Response already contains the form, continue to parse it
        else:
            print(f"Unexpected response: status {resp.status_code}")
            return False

        # Step 2: Parse the form to extract hidden values
        print("\n=== Parsing login form ===")
        soup = BeautifulSoup(resp.text, "html.parser")
        form = soup.find("form", {"method": "post"})

        if not form:
            print("ERROR: Could not find login form")
            print(f"Available forms: {len(soup.find_all('form'))}")
            print(f"Full response body:\n{resp.text}")
            return False

        print(f"Form found!")
        print(f"  Action: {form.get('action')}")
        print(f"  Method: {form.get('method')}")

        # Extract hidden form values
        print("\n=== Extracting form fields ===")
        form_data = {}
        for input_tag in form.find_all("input", type="hidden"):
            name = input_tag.get("name", "")
            value = input_tag.get("value", "")
            if name:  # Only add if name is not empty
                form_data[name] = value
                print(f"  Hidden field: {name} = {value}")

        # Add username and password
        form_data["username"] = credentials["username"]
        form_data["password"] = "***REDACTED***"  # Don't log password
        print(f"  Added: username = {credentials['username']}")
        print(f"  Added: password = ***REDACTED***")

        # Restore actual password for submission
        form_data["password"] = credentials["password"]

        print(f"\n=== Preparing form submission ===")
        print(f"POST data keys: {list(form_data.keys())}")

        # Step 3: Submit the form
        action = form.get("action", "/")
        print(f"Form action: {action}")

        if action.startswith("/"):
            # Relative URL - construct full URL using response URL
            parsed_url = urlparse(resp.url)
            submit_url = f"{parsed_url.scheme}://{parsed_url.netloc}{action}"
            print(f"Relative action, constructing full URL:")
            print(f"  Scheme: {parsed_url.scheme}")
            print(f"  Netloc: {parsed_url.netloc}")
            print(f"  Action: {action}")
            print(f"  Full URL: {submit_url}")
        else:
            submit_url = action
            print(f"Absolute action URL: {submit_url}")

        print(f"\n=== Submitting login form ===")
        print(f"URL: {submit_url}")
        print(f"Method: POST")
        resp = safe_post(
            submit_url,
            session=session,
            error_msg="Failed to submit form",
            data=form_data,
        )
        if not resp:
            print("ERROR: Form submission failed")
            return False

        print(f"\n=== Login response ===")
        print(f"Status: {resp.status_code}")
        print(f"URL: {resp.url}")
        print(f"Headers: {dict(resp.headers)}")
        print(f"Body (first 1000 chars): {resp.text[:1000]}")

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
            invalid = ("invalid" in response.text.lower())
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


class RandolphOxford(WiFiNetwork):
    SSID = "Randolph_Guest"

    def get_credentials(self):
        email = os.getenv("RANDOLPH_EMAIL")
        if not email:
            fail("RANDOLPH_EMAIL environment variable must be set.")
        return {"email": email}

    def _compute_chap_password(self, chap_id, chap_challenge, password=""):
        """
        Compute CHAP password response using MD5
        CHAP-Password = MD5(chap-id + password + chap-challenge)

        For guest networks with no password, use empty string
        """
        # chap_id and chap_challenge come as escaped strings from HTML
        # Need to decode them to bytes
        try:
            # Handle escape sequences in the challenge
            chap_id_bytes = (
                chap_id.encode("utf-8").decode("unicode_escape").encode("latin1")
            )
            chap_challenge_bytes = (
                chap_challenge.encode("utf-8").decode("unicode_escape").encode("latin1")
            )
        except:
            # If decoding fails, try as-is
            chap_id_bytes = chap_id.encode("latin1")
            chap_challenge_bytes = chap_challenge.encode("latin1")

        password_bytes = password.encode("utf-8")

        # Compute MD5(chap-id + password + chap-challenge)
        md5_hash = hashlib.md5()
        md5_hash.update(chap_id_bytes)
        md5_hash.update(password_bytes)
        md5_hash.update(chap_challenge_bytes)

        # Return hex digest
        return md5_hash.hexdigest()

    def _find_and_submit_form(self, session, resp, saved_chap_secret=None):
        """Parse HTML response for a form and submit it using the appropriate HTTP method

        Returns: (response, chap_secret) tuple
        """
        print(f"  Response URL: {resp.url}, Status: {resp.status_code}")

        bs = BeautifulSoup(resp.content, "html.parser")

        # Check if we've reached a success page
        if b"You are logged in" in resp.content or b"logged in" in resp.content.lower():
            print("  Success page detected - authentication complete")
            return None, None

        form = bs.find("form")
        if not form:
            print("  No form found in response")
            # Print page title for debugging
            title = bs.find("title")
            if title:
                print(f"  Page title: {title.get_text().strip()}")
            return None, None

        # Look for the CHAP secret in JavaScript (Mikrotik pattern)
        chap_secret = None
        scripts = bs.find_all("script", type="text/javascript")
        for script in scripts:
            if script.string and "hexMD5" in script.string:
                match = re.search(
                    r"hexMD5\(['\"]\\[0-9]{3}['\"] \+ ['\"]([\w]+)['\"]", script.string
                )
                if match:
                    chap_secret = match.group(1)
                    print(f"  Found CHAP secret in JavaScript")
                    break

        # Extract all form data
        form_data = {}
        has_chap_challenge = False

        for input_tag in form.find_all("input"):
            name = input_tag.get("name", "")
            value = input_tag.get("value", "")
            if name:
                form_data[name] = value
                if name == "chap-challenge":
                    has_chap_challenge = True

        action = form.get("action")
        method = form.get("method", "get").lower()

        # If no action, submit to current URL (common pattern)
        if not action:
            action = resp.url
            print(f"  No form action found, using current URL: {action}")

        # Check if this is an email input form that we need to fill
        email_input = form.find("input", attrs={"name": "email"}) or form.find(
            "input", attrs={"type": "email"}
        )
        if email_input and not form_data.get("email"):
            print("  Email form detected - filling in email address")
            credentials = self.get_credentials()
            form_data["email"] = credentials["email"]

        # Check if this is the JavaScript auto-submit form (has username, password, dst)
        # This form doesn't have chap-id/chap-challenge - those are in redirect forms
        # We just pass it through since we can't execute JavaScript
        if (
            form_data.get("username")
            and "password" in form_data
            and form_data.get("dst")
            and chap_secret
            and not has_chap_challenge
        ):
            print(f"  JS auto-submit form detected, passing through")
            # Submit as-is; the next redirect form will handle authentication
            if method == "post":
                return session.post(action, data=form_data), chap_secret
            else:
                return session.get(action, params=form_data), chap_secret

        # If this form has CHAP challenge AND a user token (redirect form), authenticate
        if has_chap_challenge and form_data.get("user"):
            print(f"  CHAP authentication form detected")
            secret_to_use = saved_chap_secret or chap_secret or ""
            chap_password = self._compute_chap_password(
                form_data["chap-id"],
                form_data["chap-challenge"],
                password=secret_to_use,
            )

            # For Mikrotik, POST to the uamip login endpoint with username and chap-password
            login_url = f"http://{form_data.get('uamip', '172.20.0.1:80')}/login"
            login_data = {
                "username": form_data.get("user", ""),
                "password": chap_password,
                "dst": form_data.get("userurl", ""),
                "popup": "true",
            }
            print(f"  Submitting CHAP auth to {login_url}")
            result = session.post(login_url, data=login_data)

            # Check for errors
            if b"ERROR" in result.content:
                error_match = re.search(b'value="([^"]*ERROR[^"]*)"', result.content)
                if error_match:
                    print(f"  ⚠️  Server error: {error_match.group(1).decode()}")

            return result, chap_secret

        # Regular form submission (initial redirect forms without user token)
        print(f"  Regular form submission via {method.upper()}")
        if method == "post":
            return session.post(action, data=form_data), chap_secret
        else:
            return session.get(action, params=form_data), chap_secret

    def login(self):
        """Handle login for Randolph_Guest network"""
        print("Attempting to log in to the Randolph_Guest captive portal...")
        session = requests.Session()

        # Initial request to captive portal
        resp = session.get(GSTATIC_204)
        if resp.status_code != 200:
            print("Initial request failed")
            return False

        print(f"Initial response redirected to: {resp.url}")

        # Process forms until authentication completes or no more forms found
        form_count = 0
        chap_secret = None
        max_forms = 10
        consecutive_errors = 0

        while form_count < max_forms:
            form_count += 1
            print(f"Processing form {form_count}...")

            resp, new_secret = self._find_and_submit_form(session, resp, chap_secret)

            if resp is None:
                # No more forms found
                print(f"No more forms found after {form_count - 1} form(s)")
                break

            # Update CHAP secret if discovered
            if new_secret:
                chap_secret = new_secret

            # Check for repeated authentication errors
            if b"ERROR Incorrect password" in resp.content:
                consecutive_errors += 1
                if consecutive_errors >= 3:
                    print("Authentication failed after multiple attempts")
                    break
            else:
                consecutive_errors = 0

        # Verify internet access
        print("Checking internet access...")
        if check_internet():
            print("Successfully authenticated!")
            return True

        print("Authentication completed but internet not accessible")
        print(f"Final URL was: {resp.url if resp else 'None'}")
        return False


def fail(msg, code=1):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(code)


def _get_ssid_from_networksetup():
    """Try to get SSID using networksetup (deprecated but fast, no sudo)."""
    try:
        out = subprocess.check_output(
            ["/usr/sbin/networksetup", "-getairportnetwork", "en0"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        # Check if we're not connected
        if "You are not associated" in out or "not associated" in out.lower():
            return None
        # Try to parse the SSID
        parts = out.split(": ", 1)
        if len(parts) == 2:
            ssid = parts[1].strip()
            if ssid:
                return ssid
    except Exception:
        pass
    return None


def _get_ssid_from_ipconfig():
    """Try to get SSID using ipconfig (requires sudo but reliable on modern macOS).

    Optional: To avoid password prompts:
        1. Run: sudo visudo -f /etc/sudoers.d/wifi-login
        2. Add: YOUR_USERNAME ALL=(ALL) NOPASSWD: /usr/sbin/ipconfig
    """
    try:
        # First enable verbose mode
        subprocess.run(
            ["sudo", "ipconfig", "setverbose", "1"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # Get summary and extract SSID
        out = subprocess.check_output(
            ["sudo", "ipconfig", "getsummary", "en0"],
            text=True,
            stderr=subprocess.PIPE,
        )
        for line in out.split("\n"):
            line = line.strip()
            if line.startswith("SSID"):
                # Line format: " SSID : NetworkName"
                parts = line.split(":", 1)
                if len(parts) == 2:
                    ssid = parts[1].strip()
                    print(f"  Found SSID from ipconfig: {ssid}")
                    return ssid
    except Exception as e:
        print(f"  ipconfig method failed: {e}")
    print("  ipconfig method failed to get SSID")
    return None


def get_ssid():
    """
    Get the current Wi-Fi SSID. First tries networksetup (fast but deprecated),
    then falls back to ipconfig if networksetup fails or returns "not associated".
    """
    # Try networksetup first (fast, no sudo required)
    ssid = _get_ssid_from_networksetup()
    if ssid:
        return ssid
    # Fallback to ipconfig (requires sudo but more reliable on modern macOS)
    ssid = _get_ssid_from_ipconfig()
    if ssid:
        return ssid
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
        RandolphOxford.SSID: RandolphOxford,
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
