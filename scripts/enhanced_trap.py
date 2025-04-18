#!/usr/bin/env python3
# Enhanced SNMP trap sender with support for custom OIDs and values
# This script can send traps with specific OIDs from device records

import socket
import time
import struct
import argparse
import sys
import re
import os

def encode_oid(oid_str):
    """Encode an OID string into BER format"""
    if not oid_str:
        return b''
        
    parts = [int(part) for part in oid_str.split('.')]
    if len(parts) < 2:
        return b''
        
    result = bytes([40 * parts[0] + parts[1]])
    for part in parts[2:]:
        if part < 128:
            result += bytes([part])
        else:
            # Handle multi-byte encoding for larger values
            bytes_needed = []
            value = part
            while value > 0:
                bytes_needed.insert(0, value & 0x7F)
                value >>= 7
            
            for i in range(len(bytes_needed) - 1):
                bytes_needed[i] |= 0x80
                
            result += bytes(bytes_needed)
    return result

def encode_integer(value):
    """Encode an integer value into BER format"""
    # Convert to int if string
    if isinstance(value, str):
        try:
            value = int(value)
        except ValueError:
            return None
            
    if value < 128 and value >= -128:
        return bytes([0x02, 0x01, value & 0xFF])
    elif value < 32768 and value >= -32768:
        return bytes([0x02, 0x02]) + struct.pack('>h', value)
    else:
        return bytes([0x02, 0x04]) + struct.pack('>i', value)

def encode_string(value):
    """Encode a string value into BER format"""
    if not isinstance(value, str):
        value = str(value)
    value_bytes = value.encode('utf-8')
    return bytes([0x04, len(value_bytes)]) + value_bytes

def encode_value(value_type, value):
    """Encode a value based on its type"""
    if value_type == '2':  # INTEGER
        return encode_integer(value)
    elif value_type == '4':  # OCTET STRING
        return encode_string(value)
    else:
        # Default to string encoding
        return encode_string(value)

def create_trap_packet(community, agent_ip, agent_port, oid, value_type, value):
    """Create a SNMP trap packet with the specified OID and value"""
    # SNMP version 1
    version = 0
    
    # PDU type 4 (trap)
    pdu_type = 4
    
    # Enterprise OID (use a standard enterprise OID)
    enterprise_oid = "1.3.6.1.4.1.50000"
    
    # Agent address (from parameter)
    if agent_ip == "localhost":
        agent_ip = "127.0.0.1"
    agent_addr = socket.inet_aton(agent_ip)
    
    # Generic trap type (6 = enterpriseSpecific)
    generic_trap = 6
    
    # Specific trap code (use something related to the OID if possible)
    specific_trap = 1
    
    # Timestamp
    timestamp = int(time.time())
    
    # Start building the packet
    packet = bytearray()
    
    # Add version
    packet += b'\x02\x01' + bytes([version])
    
    # Add community string
    packet += b'\x04' + bytes([len(community)]) + community.encode()
    
    # Start trap PDU
    trap_pdu = bytearray()
    
    # Add enterprise OID
    encoded_enterprise = encode_oid(enterprise_oid)
    trap_pdu += b'\x06' + bytes([len(encoded_enterprise)]) + encoded_enterprise
    
    # Add agent address
    trap_pdu += b'\x40\x04' + agent_addr
    
    # Add generic trap type
    trap_pdu += b'\x02\x01' + bytes([generic_trap])
    
    # Add specific trap code
    trap_pdu += b'\x02\x01' + bytes([specific_trap])
    
    # Add timestamp
    timestamp_bytes = struct.pack('>L', timestamp)
    trap_pdu += b'\x43\x04' + timestamp_bytes
    
    # Add variable bindings
    var_bindings = bytearray()
    
    # Add device OID and value
    encoded_oid = encode_oid(oid)
    encoded_value = encode_value(value_type, value)
    
    if encoded_oid and encoded_value:
        oid_varbind = bytearray()
        oid_varbind += b'\x06' + bytes([len(encoded_oid)]) + encoded_oid
        oid_varbind += encoded_value
        
        oid_seq = b'\x30' + bytes([len(oid_varbind)]) + oid_varbind
        var_bindings += oid_seq
    
    # Add source port information as another varbind
    port_oid = "1.3.6.1.4.1.50000.5.1"  # Custom OID for agent port
    encoded_port_oid = encode_oid(port_oid)
    encoded_port_value = encode_integer(agent_port)
    
    if encoded_port_oid and encoded_port_value:
        port_varbind = bytearray()
        port_varbind += b'\x06' + bytes([len(encoded_port_oid)]) + encoded_port_oid
        port_varbind += encoded_port_value
        
        port_seq = b'\x30' + bytes([len(port_varbind)]) + port_varbind
        var_bindings += port_seq
    
    # Add community info as another varbind
    community_oid = "1.3.6.1.4.1.50000.5.2"  # Custom OID for community
    encoded_community_oid = encode_oid(community_oid)
    encoded_community_value = encode_string(community)
    
    if encoded_community_oid and encoded_community_value:
        community_varbind = bytearray()
        community_varbind += b'\x06' + bytes([len(encoded_community_oid)]) + encoded_community_oid
        community_varbind += encoded_community_value
        
        community_seq = b'\x30' + bytes([len(community_varbind)]) + community_varbind
        var_bindings += community_seq
    
    # Wrap variable bindings in a sequence
    var_bindings_seq = b'\x30' + bytes([len(var_bindings)]) + var_bindings
    
    # Add variable bindings to trap PDU
    trap_pdu += var_bindings_seq
    
    # Wrap trap PDU with type and length
    trap_pdu_with_type = bytes([pdu_type + 0xA0]) + bytes([len(trap_pdu)]) + trap_pdu
    
    # Add trap PDU to packet
    packet += trap_pdu_with_type
    
    # Wrap whole packet in a sequence
    result = b'\x30' + bytes([len(packet)]) + packet
    
    return result

def load_device_oids(device_file):
    """Load OIDs from a device .snmprec file"""
    oids = {}
    
    if not os.path.exists(device_file):
        print(f"Error: Device file {device_file} not found")
        return oids
        
    try:
        with open(device_file, 'r') as f:
            for line in f:
                # Skip comments and empty lines
                if line.strip().startswith('#') or not line.strip():
                    continue
                    
                # Parse the line (OID|type|value)
                parts = line.strip().split('|', 2)
                if len(parts) == 3:
                    oid, value_type, value = parts
                    oids[oid] = (value_type, value)
    except Exception as e:
        print(f"Error reading device file: {e}")
        
    return oids

def print_available_oids(oids):
    """Display available OIDs with their values"""
    print("\nAvailable OIDs:")
    print("-" * 80)
    print(f"{'OID':<30} {'Type':<10} {'Value':<30}")
    print("-" * 80)
    
    for oid, (value_type, value) in sorted(oids.items()):
        type_name = "INTEGER" if value_type == "2" else "STRING"
        print(f"{oid:<30} {type_name:<10} {value:<30}")

def send_trap(target_ip, target_port, community, agent_ip, agent_port, oid, value_type, value):
    """Send a trap with the specified OID and value"""
    try:
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Create trap packet
        packet = create_trap_packet(community, agent_ip, agent_port, oid, value_type, value)
        
        # Send packet
        sock.sendto(packet, (target_ip, target_port))
        print(f"\nTrap sent successfully:")
        print(f"  From: {agent_ip}:{agent_port} (community: {community})")
        print(f"  To: {target_ip}:{target_port}")
        print(f"  OID: {oid}")
        print(f"  Value: {value} (type: {value_type})")
        
    except Exception as e:
        print(f"Error sending trap: {e}")
    finally:
        sock.close()

def find_data_directory():
    """Find the data directory relative to this script"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, "data")
    
    if os.path.isdir(data_dir):
        return data_dir
    return None

def list_devices(data_dir):
    """List available device files"""
    devices = []
    
    if not data_dir or not os.path.isdir(data_dir):
        return devices
        
    for filename in os.listdir(data_dir):
        if filename.endswith('.snmprec'):
            devices.append(filename)
            
    return devices

def get_device_file_path(data_dir, community):
    """Get the path to a device file based on community string"""
    if not data_dir:
        return None
        
    device_file = os.path.join(data_dir, f"{community}.snmprec")
    
    if os.path.exists(device_file):
        return device_file
        
    # If exact match not found, try to find a matching device file
    for filename in os.listdir(data_dir):
        if filename.endswith('.snmprec') and filename.startswith(community):
            return os.path.join(data_dir, filename)
            
    return None

def main():
    parser = argparse.ArgumentParser(description='Send an SNMP trap with specific OID and value')
    parser.add_argument('--target', default='127.0.0.1', help='Target IP address')
    parser.add_argument('--port', type=int, default=16200, help='Target port')
    parser.add_argument('--community', default='device2', help='SNMP community string')
    parser.add_argument('--agent-ip', default='127.0.0.1', help='Agent IP address')
    parser.add_argument('--agent-port', type=int, default=16101, help='Agent port')
    parser.add_argument('--oid', help='OID to send in the trap')
    parser.add_argument('--value', help='Value to send with the OID')
    parser.add_argument('--list-devices', action='store_true', help='List available devices')
    parser.add_argument('--list-oids', action='store_true', help='List available OIDs for the device')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # Find data directory
    data_dir = find_data_directory()
    if not data_dir:
        print("Error: Could not find data directory")
        return
    
    # List devices if requested
    if args.list_devices:
        devices = list_devices(data_dir)
        if devices:
            print("\nAvailable devices:")
            for device in sorted(devices):
                print(f"  - {device}")
        else:
            print("No device files found")
        return
    
    # Get device file path
    device_file = get_device_file_path(data_dir, args.community)
    if not device_file:
        print(f"Error: No device file found for community '{args.community}'")
        return
    
    # Load OIDs from device file
    oids = load_device_oids(device_file)
    if not oids:
        print(f"Error: No OIDs found in device file '{device_file}'")
        return
    
    # List OIDs if requested
    if args.list_oids:
        print(f"\nDevice file: {os.path.basename(device_file)}")
        print_available_oids(oids)
        return
    
    # Interactive mode
    if args.interactive:
        print(f"\nDevice file: {os.path.basename(device_file)}")
        print_available_oids(oids)
        
        print("\nEnter the OID number from the list above (or 'q' to quit):")
        oid_input = input("> ")
        
        if oid_input.lower() == 'q':
            return
            
        # Find the OID
        selected_oid = None
        for oid in oids:
            if oid.endswith(oid_input) or oid == oid_input:
                selected_oid = oid
                break
                
        if not selected_oid:
            print(f"Error: OID '{oid_input}' not found")
            return
            
        value_type, current_value = oids[selected_oid]
        print(f"\nCurrent value for {selected_oid}: {current_value}")
        print("Enter the new value (or press Enter to use current value):")
        new_value = input("> ")
        
        if not new_value:
            new_value = current_value
            
        # Send the trap
        send_trap(
            args.target, 
            args.port, 
            args.community,
            args.agent_ip,
            args.agent_port,
            selected_oid,
            value_type,
            new_value
        )
        return
    
    # Command line mode with explicit OID and value
    if args.oid:
        # Check if OID exists
        if args.oid in oids:
            value_type, value = oids[args.oid]
            send_trap(
                args.target,
                args.port,
                args.community,
                args.agent_ip,
                args.agent_port,
                args.oid,
                value_type,
                args.value if args.value else value
            )
        else:
            print(f"Error: OID '{args.oid}' not found in device file")
            print_available_oids(oids)
    else:
        print("Error: No OID specified")
        print("Please use --oid or --interactive")

if __name__ == '__main__':
    main()