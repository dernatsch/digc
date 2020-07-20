# digc: delta encoding for IGC files

IGC files consist mainly of _B records_. The records that describe the planes position at a time.
A B record saves the coordinates and timestamp in plain text in a single line that is at least 35 bytes wide (37 with CR LF).
The rate at which loggers produce B records is variable and may be subject to user settings, but 1 second between records is not unreasonable, especially near turnpoints.

Assuming this rate of 1 record per second a long flight of 10 hours produces 36000 B records or ~1.2 MiB of data.
Although an extreme example I wanted to explore how much delta encoding reduces the size of such a file.

## The Goal / Usage
The end product should be a way to perform a lossless encoding of IGC files.
In other words a program that produces some kind of file by
```sh
digc.py test.igc > test.digc
```
such that when reversed by
```sh
digc.py -d test.digc > out.igc
```
the files `test.igc` and `out.igc` are identical.

**I haven't implemented the decode functionality yet, oh well.**

## .digc and why this only works when compressed
The digc.py script produces an igc file containing a new record type that is built like this:
| Field                   | Length in bytes |
| ----------------------- | --------------- |
| Prefix (T)              | 1               |
| Time delta              | 6               |
| Latitude delta          | 7               |
| Longitude delta         | 8               |
| Validity                | 1               |
| Pressure altitude delta | 5               |
| GNSS altitude delta     | 5               |
| Rest of the record      | ?               |

The script currently only supports B records without extensions so the rest of the record is simply appended.
Now this T record takes up a similar space (33 bytes) as the original B record (35 bytes) so we do not gain much.
The potential in this encoding is only realised when compressing the file.
The compression program can replace parts of similar T records by beckreferences, thus saving space.

## Delta encoding a flight
Let's imagine a hypothetical flight where a pilots starts at the coordinates (0,0).
The pilot flies in a direction at a rate of 1/s and three B records are produced. The content of the B records could read:
```
0, 0
0, 1
0, 2
```
And all is well. Now let's say the flight continues and at some other point the pilot is at coordinates (10, 10) and flies in the same direction at the same speed.
At this point the file would read:
```
10, 10
10, 11
10, 12
```
The pilot essentially did the same thing at two places but the file contents are so different that they cannot be compressed well.
Using delta encoding we only save the differences between the fixes.
These differences should occurr more often than some particular coordinates as sailplanes often fly in the same way (speed/course wise) but not in the same place.

Using delta encoding the file could look more like this (delta records marked with a d):
```
0, 0 
0, 1 d
0, 1 d
...   
10, 10
0, 1 d
0, 1 d
```

Here same delta record occurrs 4 times, which can be efficiently compressed.

## What can we save?
I tested this with a large-ish IGC file:
| File         | Size in kB |
| ------------ | ---------- |
| test.igc     | 593        |
| test.digc    | 569        |
| test.igc.gz  | 201        |
| test.digc.gz | 132        |

Uncompressed we didn't gain a lot, as expected but the compressed delta encoded file is only ~66% of the plain compressed file.
In other words: We bumped the compression ratio from 2.83 to 4.3 .
In the end I would call this a success!

## Ideas that are probably better in a new project
- protobufs / flatbufs or similar
- splitting the single parts of the record into separate streams + delta encoding -> varints
  - varints could probably reduce the size of b records to about a fifth
- thinking of a modern file format
