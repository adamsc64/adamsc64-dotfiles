#!/usr/bin/env python3
import datetime
import os
import sys
import requests
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from decimal import Decimal

OXCAM_CLUB_USER = os.getenv("OXCAM_CLUB_USER")
OXCAM_CLUB_PASSWORD = os.getenv("OXCAM_CLUB_PASSWORD")


def fail(msg):
    print(f"Error: {msg}")
    sys.exit(1)


def login_club(session):
    login_url = "https://oxfordandcambridgeclub.co.uk/membership/"
    payload = {
        "email_address": OXCAM_CLUB_USER,
        "password": OXCAM_CLUB_PASSWORD,
        "login": "Login",
    }
    resp = session.post(login_url, data=payload, verify=False)
    if "Logout" not in resp.text:  # crude check for login success
        fail("Login failed. Check credentials or login form structure.")
    print("[+] Logged into club site")
    return resp


def handoff_to_booking(session):
    redir_url = (
        "https://oxfordandcambridgeclub.co.uk/members/accommodation/book-a-room/"
    )
    resp = session.get(redir_url, verify=False)
    correct = (
        "Welcome to the Oxford and Cambridge Club online bookings system" in resp.text
    )
    if not correct:
        fail("Redirection to booking system failed. Check the URL or login status.")

    soup = BeautifulSoup(resp.text, "html.parser")
    booking_form = soup.find("form")
    if not booking_form:
        fail("Couldn't find date selection form on booking site.")

    print("[+] Redirected to booking system")
    return booking_form, resp.url


def select_date_and_query(session, booking_url, booking_form, day):
    action = urljoin(booking_url, booking_form["action"])
    # Build form fields from all inputs (hidden + text)
    form_fields = {
        i["name"]: i.get("value", "")
        for i in booking_form.find_all("input")
        if i.get("name")
    }

    # Parse date_str into components
    year_int, month_int, day_int = day.year, day.month, day.day

    # Update with correct date fields from HAR
    form_fields["ctl00$Main$f_ArrivalDay"] = str(day_int)
    form_fields["ctl00$Main$f_ArrivalMonth"] = str(month_int)
    form_fields["ctl00$Main$f_ArrivalYear"] = str(year_int)
    form_fields["ctl00$Main$f_ArrvDate"] = ""  # usually blank
    form_fields["ctl00$Main$f_Nights"] = "1"

    # Add the submit button
    form_fields["ctl00$Main$f_CheckAvailabilityButton"] = "Check availability"

    # Submit the form
    resp = session.post(action, data=form_fields, verify=False)
    print(f"[+] Queried booking system for {day}")

    # Parse results page
    soup = BeautifulSoup(resp.text, "html.parser")
    # Example: Find room availability table
    already = set()
    available_rooms = []
    for td in soup.find_all("td", class_="RadioLabelList", colspan="2"):
        room_name = td.get_text(strip=True)
        if not room_name:
            continue
        if room_name in already:
            continue
        already.add(room_name)
        # Find the second <td> in the parent row (usually price or similar)
        tds = td.parent.find_all("td")
        price = tds[1]
        price = price.get_text(strip=True)
        price = price.split("£")[1]
        price = Decimal(price)
        if price >= Decimal("200.00"):
            continue
        available_rooms.append((room_name, price))
    return available_rooms


def disable_ssl_warnings():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    disable_ssl_warnings()
    if not (OXCAM_CLUB_USER and OXCAM_CLUB_PASSWORD):
        fail("Set OXCAM_CLUB_USER and OXCAM_CLUB_PASSWORD in your environment.")

    with requests.Session() as session:
        login_club(session)
        booking_form, booking_url = handoff_to_booking(session)
        day = datetime.date.today()
        while True:
            rooms = select_date_and_query(
                session, booking_url, booking_form, day
            )
            if not rooms:
                print("No rooms found.")
            else:
                for room in rooms:
                    print("-", room)
            day += datetime.timedelta(days=1)


if __name__ == "__main__":
    main()
