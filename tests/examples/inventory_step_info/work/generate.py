#!/usr/bin/env python3
from stepup.core.api import call, static
from stepup.core.call import driver
from stepup.core.stepinfo import dump_step_info


def plan(out):
    static("src.txt")
    info = call("./generate.py", "run", inp="src.txt", out=["a.txt", "b.txt"])
    dump_step_info(out[0], info)


def run(inp, out):
    with open(inp[0], encoding="utf-8") as fh:
        text = fh.read()
    for path_out in out:
        with open(path_out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(f"{path_out}: {text}")


if __name__ == "__main__":
    driver()
