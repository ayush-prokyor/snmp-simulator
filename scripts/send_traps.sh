#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."

source "$PROJECT_ROOT/venv/bin/activate"

# Default values
TARGET="127.0.0.1"
TARGET_PORT=16200
AGENT_IP="127.0.0.1"
SCRIPT="enhanced_trap.py"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --target)
            TARGET="$2"
            shift 2
            ;;
        --port)
            TARGET_PORT="$2"
            shift 2
            ;;
        --agent-ip)
            AGENT_IP="$2"
            shift 2
            ;;
        --script)
            SCRIPT="$2"
            shift 2
            ;;
        --list-devices)
            LIST_DEVICES="yes"
            shift
            ;;
        --list-oids)
            LIST_OIDS="yes"
            COMMUNITY="$2"
            shift 2
            ;;
        --community)
            COMMUNITY="$2"
            shift 2
            ;;
        --agent-port)
            AGENT_PORT="$2"
            shift 2
            ;;
        --oid)
            OID="$2"
            shift 2
            ;;
        --value)
            VALUE="$2"
            shift 2
            ;;
        --interactive)
            INTERACTIVE="yes"
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --target IP           Target IP address (default: 127.0.0.1)"
            echo "  --port PORT           Target port (default: 16200)"
            echo "  --agent-ip IP         Agent IP address (default: 127.0.0.1)"
            echo "  --community STRING    Community string (e.g., device2)"
            echo "  --agent-port PORT     Agent port (default: depends on community)"
            echo "  --oid OID             OID to send in the trap"
            echo "  --value VALUE         Value to send with the OID"
            echo "  --list-devices        List available devices"
            echo "  --list-oids           List available OIDs for the device"
            echo "  --interactive         Run in interactive mode"
            echo "  --help                Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Set default agent port based on community if not specified
if [ -z "$AGENT_PORT" ]; then
    case "$COMMUNITY" in
        "device2")
            AGENT_PORT=16100
            ;;
        "device3")
            AGENT_PORT=16102
            ;;
        *)
            AGENT_PORT=16100
            ;;
    esac
fi

# Check if we're supposed to list devices
if [ "$LIST_DEVICES" = "yes" ]; then
    python "$SCRIPT_DIR/$SCRIPT" --list-devices
    exit 0
fi

# Check if we're supposed to list OIDs
if [ "$LIST_OIDS" = "yes" ]; then
    if [ -z "$COMMUNITY" ]; then
        echo "Error: Community string must be specified with --list-oids"
        exit 1
    fi
    python "$SCRIPT_DIR/$SCRIPT" --community "$COMMUNITY" --list-oids
    exit 0
fi

# Check if we're supposed to run in interactive mode
if [ "$INTERACTIVE" = "yes" ]; then
    if [ -z "$COMMUNITY" ]; then
        echo "Error: Community string must be specified with --interactive"
        exit 1
    fi
    python "$SCRIPT_DIR/$SCRIPT" --target "$TARGET" --port "$TARGET_PORT" \
                               --agent-ip "$AGENT_IP" --agent-port "$AGENT_PORT" \
                               --community "$COMMUNITY" --interactive
    exit 0
fi

# Run with specific OID and value if provided
if [ -n "$OID" ]; then
    if [ -z "$COMMUNITY" ]; then
        echo "Error: Community string must be specified with --oid"
        exit 1
    fi
    python "$SCRIPT_DIR/$SCRIPT" --target "$TARGET" --port "$TARGET_PORT" \
                               --agent-ip "$AGENT_IP" --agent-port "$AGENT_PORT" \
                               --community "$COMMUNITY" --oid "$OID" --value "$VALUE"
    exit 0
fi

# If we get here, we need to show usage
echo "Error: No action specified"
echo "Use one of: --list-devices, --list-oids, --interactive, or --oid"
echo "Try '$0 --help' for more information"
exit 1