#!/bin/sh

# wait-for-it.sh

# Wait for a TCP service to be available
# Usage: wait-for-it.sh host:port [--timeout=seconds] [--strict] [--quiet] [--command cmd args...]

# Exit codes:
# 0: success
# 1: timeout
# 2: error

set -e

host=$1
shift
port=$1
shift

# Default timeout is 15 seconds
timeout=15
strict=0
quiet=0
shifted=0

usage() {
    cat << USAGE >&2
Usage: $0 host:port [--timeout=seconds] [--strict] [--quiet] [--command cmd args...]

-w, --waitfor         Wait for a TCP service to be available
--timeout             Timeout in seconds (default: 15)
--strict              Exit with error if timeout reached
--quiet              Don't output any status messages
--command            Execute command with args after the test finishes
USAGE
    exit 2
}

while [ $# -gt 0 ]
    do
    case $1 in
        --timeout)
            timeout=$2
            if [ $timeout -le 0 ]
            then
                echo "ERROR: timeout must be greater than 0" >&2
                usage
            fi
            shift 2
            ;;
        --strict)
            strict=1
            shift
            ;;
        --quiet)
            quiet=1
            shift
            ;;
        --command)
            shift
            command=$*
            break
            ;;
        --help)
            usage
            ;;
        *)
            echo "ERROR: unknown option: $1" >&2
            usage
            ;;
    esac
    done

if [ -z "$host" ] || [ -z "$port" ]; then
    echo "ERROR: host and port must be provided" >&2
    usage
fi

if [ $quiet -eq 0 ]; then
    echo "Waiting for $host:$port..."
fi

start_ts=$(date +%s)
while :
do
    (echo > /dev/tcp/$host/$port) >/dev/null 2>&1
    result=$?
    if [ $result -eq 0 ] ; then
        if [ $quiet -eq 0 ]; then
            end_ts=$(date +%s)
            echo "Connected to $host:$port after $((end_ts - start_ts)) seconds"
        fi
        break
    fi
    sleep 1

current_ts=$(date +%s)
if [ $((current_ts-start_ts)) -ge $timeout ]; then
    echo "ERROR: timeout reached while waiting for $host:$port" >&2
    exit 1
fi
done

if [ ! -z "$command" ]; then
    exec $command
fi

exit 0
