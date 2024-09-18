from dotenv import load_dotenv
import sys
import datetime

import pieporter

load_dotenv()


def main():
    start = datetime.datetime.now()
    print(f"Start at {start.strftime('%Y-%m-%d %H:%M:%S')}")

    pieporter.search()

    end = datetime.datetime.now()
    print(f"Done in {end - start}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
