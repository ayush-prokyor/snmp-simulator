# #!/bin/bash

# SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# PROJECT_ROOT="$SCRIPT_DIR/.."
# DATA_DIR="$PROJECT_ROOT/data"

# source "$PROJECT_ROOT/venv/bin/activate"

# # Kill old agents
# pkill -f snmpsim-command-responder || true

# # Device 1 (existing)
# snmpsim-command-responder \
#     --data-dir="$DATA_DIR" \
#     --agent-udpv4-endpoint=0.0.0.0:16100 \
#     --variation-module-options=writecache: \
#     --logging-method=stdout \
#     --log-level=debug &

# # Device 2
# snmpsim-command-responder \
#     --data-file="$DATA_DIR/device2.snmprec" \
#     --agent-udpv4-endpoint=0.0.0.0:16101 \
#     --variation-module-options=writecache: \
#     --logging-method=stdout \
#     --log-level=debug &

# # Device 3
# snmpsim-command-responder \
#     --data-file="$DATA_DIR/device3.snmprec" \
#     --agent-udpv4-endpoint=0.0.0.0:16102 \
#     --variation-module-options=writecache: \
#     --logging-method=stdout \
#     --log-level=debug &

# echo "Started 3 SNMP simulated agents on ports 16100, 16101, 16102"
#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."
DATA_DIR="$PROJECT_ROOT/data"

source "$PROJECT_ROOT/venv/bin/activate"

# Kill old agents
pkill -f snmpsim-command-responder || true

# Start agents on 3 ports
snmpsim-command-responder \
    --data-dir="$DATA_DIR" \
    --agent-udpv4-endpoint=0.0.0.0:16100 \
    --variation-module-options=writecache: \
    --logging-method=stdout \
    --log-level=debug &

snmpsim-command-responder \
    --data-dir="$DATA_DIR" \
    --agent-udpv4-endpoint=0.0.0.0:16101 \
    --variation-module-options=writecache: \
    --logging-method=stdout \
    --log-level=debug &

snmpsim-command-responder \
    --data-dir="$DATA_DIR" \
    --agent-udpv4-endpoint=0.0.0.0:16102 \
    --variation-module-options=writecache: \
    --logging-method=stdout \
    --log-level=debug &

echo "Started 3 SNMP simulated agents on ports 16100, 16101, 16102"
