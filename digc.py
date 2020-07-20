#!/usr/bin/python3
#  diffigc: delta encoding for igc files
#  Copyright © 2020 Jannik Birk <birk.jannik@gmail.com>
#
#  Permission is hereby granted, free of charge, to any person obtaining
#  a copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
#  OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import fileinput
import re
import pprint
import sys

B_PATTERN = re.compile(r"^B(\d{6})(\d{7})(N|S)(\d{8})(E|W)(A|V)([0-9-]{5})(\d{5})(.*)$")

def record(match):
    time = int(match[1])
    lat = int(match[2]) if match[3] == 'N' else -int(match[2])
    lon = int(match[4]) if match[5] == 'N' else -int(match[4])
    validity = match[6]
    palt = int(match[7])
    galt = int(match[8])
    rest = match[9]

    return (time, lat, lon, validity, palt, galt, rest)

def record_diff(a, b):
    """The delta record between a and b. If no delta can be determined values from are used."""
    return (
            b[0] - a[0],
            b[1] - a[1],
            b[2] - a[2],
            b[3],
            b[4] - a[4],
            b[5] - a[5],
            b[6])

def print_record_diff(d):
    print(f"T{d[0]:06}{d[1]:07}{d[2]:08}{d[3]}{d[4]:05}{d[5]:05}{d[6]}")

def main():
    lastfix = None

    for line in fileinput.input():
        line = line.rstrip()
        if line[0] != 'B':
            print(line)
        else:
            matches = re.search(B_PATTERN, line)
            if not matches:
                print(line)
                print('===== ERROR parsing b record =====')
                sys.exit(-1)

            brec = record(matches)
            
            if lastfix:
                diff = record_diff(lastfix, brec)
                print_record_diff(diff)
            else:
                print(line)

            lastfix = brec


if __name__ == '__main__':
    main()
