#!/bin/bash

set -euo pipefail

if [[ -z "${OWL_USERNAME:-}" || -z "${OWL_PASSWORD:-}" ]]; then
  echo "Error: OWL_USERNAME and OWL_PASSWORD environment variables must be set."
  exit 1
fi

USERNAME="${OWL_USERNAME}"
PASSWORD="${OWL_PASSWORD}"

# Login URL for the captive portal
LOGIN_URL="https://tawny-owl-captive-portal.it.ox.ac.uk:8003/index.php?zone=tawny_owl"

echo "Checking current Wi-Fi network..."
# Check that you're on the OWL Wi-Fi
SSID=$(networksetup -getairportnetwork en0 | awk -F': ' '{print $2}')
if [[ "$SSID" != "OWL" ]]; then
  echo "Not on OWL network. Aborting."
  exit 0
fi

echo "Checking if internet is already accessible..."
# Check if internet is already accessible
if curl -s --head --request GET --max-time 2 https://www.google.com | grep -qE "HTTP/[0-9.]+ 200"; then
  echo "Internet is already accessible."
  exit 0
fi

echo "Attempting to log in to the OWL captive portal..."
# Perform the login
max_attempts=5
delay=2
login_success=false

for attempt in $(seq 1 $max_attempts); do
  echo "Login attempt $attempt of $max_attempts..."
  if curl -s -k -X POST "$LOGIN_URL" \
      -d "auth_user=$USERNAME" \
      -d "auth_pass=$PASSWORD" \
      -d "accept=Continue" \
      -d "redirurl=" \
      -d "zone=tawny_owl" \
      --max-time 10 >/dev/null; then
    if curl -s --head --request GET --max-time 2 https://www.google.com | grep -qE "HTTP/[0-9.]+ 200"; then
      echo "Login succeeded and internet is reachable."
      login_success=true
      break
    else
      echo "Login POST succeeded but internet not reachable."
    fi
  else
    echo "Login POST failed or timed out."
  fi

  if [ "$attempt" -lt "$max_attempts" ]; then
    sleep $((delay * attempt))
  fi
done

if ! $login_success; then
  echo "Failed to log in after $max_attempts attempts."
  exit 1
fi

echo "Login attempt complete."
