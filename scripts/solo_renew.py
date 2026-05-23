#!/usr/bin/env python3
"""
Renew all eligible Oxford Library (SOLO) books via Bodleian SSO.

The script authenticates through the Bodleian SAML2 SSO identity provider,
navigates to the SOLO account loans page, and renews all loans that are
eligible for renewal.

Credentials
-----------
Set the following environment variables before running:

    export BOD_USERNAME=<your Oxford SSO username or library card number>
    export BOD_PASSWORD=<your Oxford SSO password>

Usage
-----
    python scripts/solo_renew.py

Notes
-----
SOLO is built on Ex Libris Primo NUI. After SSO login the script calls the
Primo v1 REST API to list loans and POST renewals. If the API paths change,
inspect the browser Network tab on the SOLO account page to find the correct
endpoints and adjust LOANS_API_PATH / RENEW_API_PATH below.
"""

import os
import sys
from typing import Optional
from urllib.parse import parse_qs, urlparse

import requests
import urllib3
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SOLO_BASE = "https://solo.bodleian.ox.ac.uk"
IDP_BASE = "https://idpj8-prd.bodleian.ox.ac.uk"

# Primo VID for SOLO
VID = "44OXF_INST:SOLO"

# SOLO private API — renews all eligible loans in one call
RENEW_ALL_URL = f"{SOLO_BASE}/primaws/rest/priv/myaccount/renew_all_loans"

# Primo JWT cache: GET /pub/loginJwtCache/{loginId}?vid={VID} -> JWT string
JWT_CACHE_URL = f"{SOLO_BASE}/primaws/rest/pub/loginJwtCache"

# SOLO SAML entry point — kicks off the SSO redirect chain to the Bodleian IdP
SSO_ENTRY_URL = (
    f"{SOLO_BASE}/primaws/suprimaExtLogin"
    "?institution=44OXF_INST"
    "&lang=en"
    f"&target-url={SOLO_BASE}/discovery/search%3Fvid%3D44OXF_INST%3ASOLO"
    "&authenticationProfile=IDJ8-PRD"
    "&idpCode=IDJ8-PRD"
    "&auth=SAML"
    "&view=44OXF_INST%3ASOLO"
    "&isSilent=false"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def fail(msg: str, code: int = 1) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(code)


def get_credentials() -> tuple[str, str]:
    username = os.getenv("BOD_USERNAME")
    password = os.getenv("BOD_PASSWORD")
    if not username or not password:
        fail("BOD_USERNAME and BOD_PASSWORD environment variables must be set.")
    return username, password  # type: ignore[return-value]


def extract_csrf(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("input", {"name": "csrf_token"})
    if tag:
        return tag.get("value")  # type: ignore[return-value]
    return None


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


def login(session: requests.Session, username: str, password: str) -> str:
    """Authenticate via Bodleian SAML2 SSO and return the Primo loginId."""
    print("Logging in via Bodleian SSO...")
    resp = session.get(SSO_ENTRY_URL, allow_redirects=True)

    # Follow any auto-submit form (SAMLRequest) to reach the IdP login page.
    if IDP_BASE not in resp.url:
        soup = BeautifulSoup(resp.text, "html.parser")
        form = soup.find("form")
        if form:
            action = form.get("action", "")
            method = form.get("method", "post").lower()
            form_data = {
                inp.get("name"): inp.get("value", "")
                for inp in form.find_all("input")
                if inp.get("name") and inp.get("type") != "submit"
            }
            if method == "get":
                resp = session.get(action, params=form_data, allow_redirects=True)
            else:
                resp = session.post(action, data=form_data, allow_redirects=True)
        else:
            fail(
                f"Expected redirect or form toward Bodleian IdP ({IDP_BASE}) "
                f"but ended up at {resp.url} with no form."
            )

    if IDP_BASE not in resp.url:
        fail(
            f"Expected to reach Bodleian IdP ({IDP_BASE}) "
            f"but ended up at: {resp.url}"
        )

    # The e1s1 page is a localStorage-check that JavaScript auto-submits.
    # Submit the form as-is (empty localStorage) to advance to the login form.
    soup_s1 = BeautifulSoup(resp.text, "html.parser")
    form_s1 = soup_s1.find("form")
    if not form_s1:
        fail(f"No form found on IdP session-check page at {resp.url}")
    action_s1 = form_s1.get("action", "")
    if action_s1.startswith("/"):
        action_s1 = IDP_BASE + action_s1
    fields_s1 = {
        inp.get("name"): inp.get("value", "")
        for inp in form_s1.find_all("input")
        if inp.get("name") and inp.get("type") != "submit"
    }
    resp = session.post(action_s1, data=fields_s1, allow_redirects=True)

    login_url = resp.url
    csrf_token = extract_csrf(resp.text)
    if not csrf_token:
        fail("Could not find csrf_token on the IdP login page.")

    post_resp = session.post(
        login_url,
        data={
            "csrf_token": csrf_token,
            "j_username": username,
            "j_password": password,
            "_eventId_proceed": "",
        },
        headers={
            **HEADERS,
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": IDP_BASE,
            "Referer": login_url,
        },
        allow_redirects=True,
    )

    soup = BeautifulSoup(post_resp.text, "html.parser")
    saml_form = soup.find("form")
    has_saml = saml_form and saml_form.find("input", {"name": "SAMLResponse"})
    if has_saml:
        action = saml_form.get("action", "")
        form_data = {
            inp.get("name"): inp.get("value", "")
            for inp in saml_form.find_all("input")
            if inp.get("name") and inp.get("type") != "submit"
        }
        saml_resp = session.post(action, data=form_data, allow_redirects=True)
    elif IDP_BASE in post_resp.url:
        # Still on IdP with no SAMLResponse form — credentials were wrong.
        error_div = soup.find(class_=lambda c: c and "error" in c.lower())
        hint = (
            error_div.get_text(strip=True) if error_div else "(no error message found)"
        )
        fail(f"Login failed — credentials rejected by IdP. Hint: {hint}")
    else:
        saml_resp = post_resp

    if IDP_BASE in saml_resp.url:
        fail(f"Still on IdP after SAML handshake: {saml_resp.url}")

    qs = parse_qs(urlparse(saml_resp.url).query)
    login_id = qs.get("loginId", [""])[0]
    if not login_id:
        fail("Could not extract loginId from post-login redirect URL.")
    print("Logged in successfully.")
    return login_id


# ---------------------------------------------------------------------------
# JWT and renewal
# ---------------------------------------------------------------------------


def get_jwt(session: requests.Session, login_id: str) -> str:
    """Exchange the Primo loginId for a Bearer JWT via the loginJwtCache endpoint."""
    resp = session.get(
        f"{JWT_CACHE_URL}/{login_id}",
        params={"vid": VID},
        headers={**HEADERS, "Accept": "application/json"},
    )
    if resp.status_code != 200:
        fail(f"Failed to obtain JWT: HTTP {resp.status_code}\n{resp.text[:500]}")
    jwt = resp.json()  # response body is the JWT string (JSON-encoded)
    if not jwt:
        fail("Empty JWT returned from loginJwtCache.")
    return jwt


def renew_all_loans(session: requests.Session, jwt: str) -> None:
    """Call the renew_all_loans endpoint and report results."""
    print("Renewing all loans...")
    resp = session.get(
        RENEW_ALL_URL,
        params={"lang": "en"},
        headers={
            **HEADERS,
            "Accept": "application/json, text/plain, */*",
            "Authorization": f'Bearer "{jwt}"',
            "Referer": f"{SOLO_BASE}/discovery/account?vid={VID}&section=loans&lang=en",
        },
    )
    if resp.status_code != 200:
        fail(f"renew_all_loans failed: HTTP {resp.status_code}")
    data = resp.json()
    loans = data.get("data", {}).get("loans", {}).get("loan", [])
    if not loans:
        print("No loans found.")
        return
    renewed = [loan for loan in loans if loan.get("renewed") == "Y"]
    not_renewed = [loan for loan in loans if loan.get("renewed") != "Y"]
    print(f"Renewed {len(renewed)} of {len(loans)} loan(s).")
    for loan in renewed:
        due = loan.get("duedate", "")
        if len(due) == 8:
            due = f"{due[0:4]}-{due[4:6]}-{due[6:8]}"
        print(f"  [renewed]  id={loan['id']}  due={due}  {loan.get('loanstatus', '')}")
    for loan in not_renewed:
        due = loan.get("duedate", "")
        if len(due) == 8:
            due = f"{due[0:4]}-{due[4:6]}-{due[6:8]}"
        print(f"  [skipped]  id={loan['id']}  due={due}  {loan.get('loanstatus', '')}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    username, password = get_credentials()

    session = requests.Session()
    session.headers.update(HEADERS)

    login_id = login(session, username, password)

    jwt = get_jwt(session, login_id)
    renew_all_loans(session, jwt)


if __name__ == "__main__":
    main()
