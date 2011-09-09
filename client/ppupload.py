#!/usr/bin/env python

import sys

from application import Application


__all__ = []

if __name__ == '__main__':
    instance = Application()
    sys.exit(instance.run())
