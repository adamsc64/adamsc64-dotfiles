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
    except json.JSONDecodeError:
        print("Clipboard does not contain valid JSON.", file=sys.stderr)
        return 1

    # Handle raw Splunk log
    candidate = candidate.get('exception', candidate)
    stacktrace = candidate.get('backtrace')
    if stacktrace:
        # if stacktrace is a tuple or list of strings, print each line
        if isinstance(stacktrace, (list, tuple)):
            for line in stacktrace:
                print(line)
        else:
            print(stacktrace)
        return 0

    # Handle other case
    try:
        candidate = candidate['exception_detail'][0]['stacktrace']
    except Exception:
        print("Not yet understood how to parse this.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Stacktrace:", file=sys.stderr)
        print("".join(traceback.format_exception(*sys.exc_info())), file=sys.stderr)
        return 1
    pprint.pprint(candidate)
    return 0


if __name__ == "__main__":
    exitcode = main()
    if not exitcode:
        sys.exit(0)
    sys.exit(exitcode)
