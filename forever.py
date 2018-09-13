#!/usr/bin/python
from subprocess import Popen
import sys

filename = "src/data/_crawlers/mentions_crawler.py"
while True:
    print("\nStarting " + filename)
    p = Popen("python " + filename, shell=True)
    p.wait()