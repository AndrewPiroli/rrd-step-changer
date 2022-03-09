import argparse
import re
import sys
from typing import BinaryIO, List, TextIO


def rewrite_rrd(
    output_file: BinaryIO,
    input_file: TextIO,
    requested_step: int,
    requested_heartbeat: int,
):
    # Determine the step of the input RRD dump
    step_re = re.compile(r"<step>(\d*)")
    try:
        for line in input_file:
            match = step_re.search(line)
            if match:
                input_step = int(match.group(1))
                break
        else:
            print("Error, unable to find step in existing RRD dump!", file=sys.stderr)
            sys.exit(-1)
        input_file.seek(0)
    except Exception as err:
        print(
            f"Exception while finding step in existing RRD dump: {err}", file=sys.stderr
        )
        sys.exit(-2)
    # Check which step (user supplied or existing) is larger and verify the math checks out with
    # the assumptions of the program, calculate the required amount of record skip/duplication
    going_up = input_step > requested_step
    if going_up:
        rowrepeat = input_step // requested_step
        if input_step % requested_step:
            print(
                "Error: Requested step and input step are not factors", file=sys.stderr
            )
            sys.exit(-3)
    else:
        rowrepeat = requested_step // input_step
        if requested_step % input_step:
            print(
                "Error: Existing step and requested step are not factors",
                file=sys.stderr,
            )
            sys.exit(-4)
    rrd_in_db = False
    skip = 0
    idx = 0
    for line in input_file:
        if rrd_in_db:
            if "</database>" in line:
                output_file.write(line.encode())
                skip = 0
                rrd_in_db = False
                continue
            elif "<row>" in line:
                if going_up:
                    for _ in range(rowrepeat):
                        output_file.write(line.encode())
                else:
                    if skip == rowrepeat:
                        output_file.write(line.encode())
                        skip = 0
                    else:
                        skip += 1
            else:
                output_file.write(line.encode())
        elif "<step>" in line:
            output_file.write(f"<step>{requested_step}</step>\n".encode())
        elif "minimal_heartbeat" in line:
            output_file.write(
                f"<minimal_heartbeat>{requested_heartbeat}</minimal_heartbeat>\n".encode()
            )
        elif "<database>" in line:
            output_file.write(line.encode())
            rrd_in_db = True
            continue
        else:
            output_file.write(line.encode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Path to the RRD dump")
    parser.add_argument(
        "output", help="Path to the output file. May be the same as the input file"
    )
    parser.add_argument("step", help="The new step value to write")
    parser.add_argument("heartbeat", help="The new heartbeat value to write")
    args = parser.parse_args()
    try:
        requested_step = int(args.step)
        requested_heartbeat = int(args.heartbeat)
        if requested_step < 1 or requested_heartbeat < 1:
            raise ValueError("Step or Heartbeat is not a positive integer")
    except Exception as err:
        print(f"Fatal error: {err}")
        sys.exit(-5)
    # Open the output in binary mode, even though we are only dealing with text
    # This is a much needed optimization found by profiling the original text version
    # In CPython implementation, TextIOWrapper is pure interpreted Python
    # The amount of string processing there slows us down *a lot* when dealing with
    # files with a lot of lines, even small RRD dumps fall into that category.
    #
    # The Python docs themselves also mention this: https://docs.python.org/3/library/io.html#id3
    # "Text I/O over a binary storage (such as a file) is significantly slower than binary I/O over the
    # same storage, because it requires conversions between unicode and binary data using a character
    # codec. This can become noticeable handling huge amounts of text data like large log files."
    with open(args.input, "r") as input_file, open(args.output, "wb") as output_file:
        rewrite_rrd(output_file, input_file, requested_step, requested_heartbeat)
