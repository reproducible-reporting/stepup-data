#!/usr/bin/env python3
from stepup.core.script import driver


def info():
    return {"static": "src.txt", "inp": "src.txt", "out": ["a.txt", "b.txt"]}


def run(inp, out):
    with open(inp, encoding="utf-8") as fh:
        text = fh.read()
    for path_out in out:
        with open(path_out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(f"{path_out}: {text}")


if __name__ == "__main__":
    driver()
