import json
import sys
import traceback
import pprint


def get_from_pbcopy():
    """Return the contents of the macOS clipboard."""
    import subprocess
    try:
        result = subprocess.run(['pbpaste'], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return ""


def main():
    candidate = get_from_pbcopy()
    try:
        candidate = json.loads(candidate)
        candidate = candidate['exception_detail'][0]['stacktrace']
    except Exception:
        print("Not yet understood how to parse this:")
        print("")
        print(candidate)
        print("")
        print("Stacktrace:")
        print("".join(traceback.format_exception(*sys.exc_info())))
        exit(1)

    pprint.pprint(candidate)

main()