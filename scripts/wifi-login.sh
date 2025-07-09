#!/bin/bash

set -euo pipefail

# 1Password shorthand account name
OP_ACCOUNT="github"

echo "Checking if ONEP_PASSWORD is set..."
# Check if ONEP_PASSWORD is set
if [[ -z "${ONEP_PASSWORD:-}" ]]; then
  echo "ONEP_PASSWORD is not set"
  exit 1
fi

echo "Signing in to 1Password CLI..."
# Sign in to 1Password CLI
eval $(echo "$ONEP_PASSWORD" | op signin)

echo "Fetching credentials from 1Password item 'OWL Oxford'..."
# Fetch credentials from 1Password item titled "OWL Oxford"
USERNAME=$(op item get "OWL Oxford" --field username)
PASSWORD=$(op item get "OWL Oxford" --field password)

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
if curl -s --head --request GET https://www.google.com | grep -qE "HTTP/[0-9.]+ 200"; then
  echo "Internet is already accessible."
  exit 0
fi

echo "Attempting to log in to the OWL captive portal..."
# Perform the login
curl -s -k -X POST "$LOGIN_URL" \
  -d "auth_user=$USERNAME" \
  -d "auth_pass=$PASSWORD" \
  -d "accept=Continue" \
  -d "redirurl=" \
  -d "zone=tawny_owl"

echo "Login attempt complete."
