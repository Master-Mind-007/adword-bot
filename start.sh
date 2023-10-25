#!/bin/bash

is_python_3() {
    python_version=$1
    if [[ "$python_version" == 3.* ]]; then
        return 0
    else
        return 1
    fi
}

if command -v python &>/dev/null; then
    python_version=$(python -c "import sys; print('{}.{}'.format(sys.version_info.major, sys.version_info.minor))")
    if is_python_3 "$python_version"; then
        python -m worker
        exit
    fi
fi

if command -v python3 &>/dev/null; then
    python3_version=$(python3 -c "import sys; print('{}.{}'.format(sys.version_info.major, sys.version_info.minor))")
    if is_python_3 "$python3_version"; then
        python3 -m worker
        exit
    fi
fi

echo "Python 3.XX not found!"
