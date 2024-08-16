#! /usr/bin/env python
import json
from pathlib import Path
from ekatra.tools.orderedyaml import load
from subprocess import call


def main():
    call('tar -C .spd -czf coolie/files/.spd-data.tgz .', shell=True)
    call('tar -C .rtdb -czf coolie/files/.rtdb-data.tgz .', shell=True)


if __name__=='__main__':
    main()
