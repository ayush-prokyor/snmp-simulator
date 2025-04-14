# SNMP Agent Simulator

This project provides a simulation environment for SNMP agents to test your SNMP management application. It uses the Python `snmpsim` package to create multiple simulated SNMP agents.

## Prerequisites

- Python 3.6+
- Virtual environment (recommended)

## Setup

1. Clone this repository
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Directory Structure

- `data/`: Contains SNMP recording files (.snmprec) for simulated devices
- `config/`: Configuration files
- `scripts/`: Helper scripts for starting agents and sending traps

## Usage

### Starting Basic Agents

To start multiple agents on different ports:

```bash
cd scripts
chmod +x start_agents.sh
./start_agents.sh
```

This will start three agents on ports 16901, 16902, and 16903.

### Using the Advanced Agent Manager

The manager script provides more flexibility:

```bash
python manage_agents.py --num-agents 5 --base-port 16901 --trap-port 16200 --send-traps
```

Options:
- `--num-agents N`: Start N simulated agents (default: 5)
- `--base-port P`: Use port numbers starting from P (default: 16901)
- `--trap-port P`: Send traps to this port (default: 16200)
- `--send-traps`: Enable automatic random trap generation
- `--trap-interval S`: Average seconds between trap events (default: 60)

### Sending Manual Traps

To send a manual trap from a specific agent:

```bash
python send_trap.py <agent-port> <target-port> <community> <device-name>
```

Example:
```bash
python send_trap.py 16901 16200 public SimulatedDevice1
```

## Testing with Your Node.js App

1. Start the simulated agents
2. Configure your Node.js app to send requests to ports 16901-1690X
3. Set up trap receiver in your Node.js app on port 16200

## Creating Custom Device Data

You can create your own device recordings:

1. Create a .snmprec file in the data directory
2. Use the format: `OID|type-code|value`

Example:
```
1.3.6.1.2.1.1.1.0|4|Linux server
1.3.6.1.2.1.1.5.0|4|CustomDevice
```

See the snmpsim documentation for more details on recording formats.

## Troubleshooting

- If ports are already in use, change the port numbers in your configuration
- Make sure your firewall allows traffic on the specified ports
- Check Python and package versions if you encounter compatibility issues