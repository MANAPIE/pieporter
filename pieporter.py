from dotenv import load_dotenv
import datetime

import pieporter

load_dotenv()


def main():
    start = datetime.datetime.now()
    print(f"Start at {start.strftime('%Y-%m-%d %H:%M:%S')}")

    pieporter.search()

    end = datetime.datetime.now()
    print(f"Done in {end - start}")


if __name__ == "__main__":
    main()
