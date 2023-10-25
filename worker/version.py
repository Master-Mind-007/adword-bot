#!/usr/bin/env python3
def get_version() -> str:
    MAJOR = '1'
    MINOR = '0'
    return f"v{MAJOR}.{MINOR}"

if __name__ == '__main__':
    print(get_version())
