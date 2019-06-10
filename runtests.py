# Third party imports
import pytest


def main():
    """
    Run pytest tests.
    """
    errno = pytest.main(['-x', '../coalaspyder/tests',  '-v', '-rw', '--durations=10',
                         '--cov=../coalaspyder/tests', '--cov-report=term-missing'])

    # sys.exit doesn't work here because some things could be running
    # in the background (e.g. closing the main window) when this point
    # is reached. And if that's the case, sys.exit does't stop the
    # script (as you would expected).
    if errno != 0:
        raise SystemExit(errno)


if __name__ == '__main__':
    main()
