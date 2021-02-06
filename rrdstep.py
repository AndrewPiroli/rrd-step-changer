import argparse
import re
import sys


def do(outfile, srclines, args):
    in_db = False
    idx = 0
    max_idx = len(srclines)
    input_step = 0
    requested_step = int(args.step)
    step_re = re.compile(r"<step>(\d*)")
    try:
        for line in srclines:
            match = step_re.search(line)
            if match:
                input_step = int(match.group(1))
                break
        else:
            sys.exit(1)  # No step found
    except:
        sys.exit(5)  # Error in step detection
    if requested_step >= input_step:
        sys.exit(
            2
        )  # Unsupported step change: requested step larger or equal to existing step
    if not input_step % requested_step == 0:
        sys.exit(
            3
        )  # Unsupported step change: requested step not multiple of existing step
    else:
        rowrepeat = input_step // int(requested_step)
    while True:
        if idx == max_idx:
            break
        if in_db:
            if "</database>" in srclines[idx]:
                in_db = False
                continue
            elif "<v>" in srclines[idx]:
                for _ in range(rowrepeat):
                    outfile.writelines(srclines[idx])
            else:
                outfile.writelines(
                    srclines[idx]
                )  # I've only studied RRD/RRA enough to know the basics, but this probably should never execute...
        elif "<step>" in srclines[idx]:
            outfile.writelines(f"<step>{requested_step}</step>\n")
        elif "minimal_heartbeat" in srclines[idx]:
            outfile.writelines(
                f"<minimal_heartbeat>{args.heartbeat}</minimal_heartbeat>\n"
            )
        elif "<database>" in srclines[idx]:
            in_db = True
            continue
        else:
            outfile.writelines(srclines[idx])
        idx += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("step")
    parser.add_argument("heartbeat")
    args = parser.parse_args()
    with open(args.input, "r") as infile:
        srclines = infile.readlines()
    with open(args.output, "w+") as outfile:
        do(outfile, srclines, args)
    sys.exit(0)


if __name__ == "__main__":
    main()
