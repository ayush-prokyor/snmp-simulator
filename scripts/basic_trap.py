#!/usr/bin/env python3
# Basic SNMP trap sender using socket directly
# This avoids pysnmp dependency issues

import socket
import time
import struct
import argparse

def send_basic_trap(target_ip, target_port, community, device_name):
    """Send a basic SNMP trap using raw UDP socket"""
    try:
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Create a simplified SNMPv1 trap packet
        # This is a very simplified version with minimal encoding
        current_time = int(time.time())
        
        # Simple SNMP trap packet (pre-encoded for simplicity)
        # Community string is inserted dynamically
        packet = bytearray([
            0x30, 0x3D,                     # SEQUENCE, length
            0x02, 0x01, 0x00,               # INTEGER, length, SNMPv1
        ])
        
        # Add community string
        community_bytes = community.encode()
        packet += bytearray([0x04, len(community_bytes)]) + community_bytes
        
        # Add trap PDU (partially pre-encoded for simplicity)
        packet += bytearray([
            0xA4, 0x30,                     # TRAP-PDU
            0x06, 0x0A, 0x2B, 0x06, 0x01, 0x04, 0x01, 0x81, 0x85, 0x67, 0x01, 0x00,  # Enterprise OID
            0x40, 0x04, 0x7F, 0x00, 0x00, 0x01,  # Agent address (127.0.0.1)
            0x02, 0x01, 0x06,               # Generic trap: enterpriseSpecific
            0x02, 0x01, 0x01,               # Specific trap code: 1
        ])
        
        # Add timestamp
        timestamp_bytes = struct.pack('>L', current_time % 0x7FFFFFFF)
        packet += bytearray([0x43, 0x04]) + timestamp_bytes
        
        # Add variable bindings with device name
        device_bytes = device_name.encode()
        
        # Variable bindings sequence
        var_bindings = bytearray([
            0x30, 0x12,                     # SEQUENCE
            0x30, 0x10,                     # SEQUENCE
            0x06, 0x08, 0x2B, 0x06, 0x01, 0x02, 0x01, 0x01, 0x05, 0x00,  # sysName OID
            0x04, len(device_bytes)
        ]) + device_bytes
        
        packet += var_bindings
        
        # Adjust packet length fields if needed
        # This is just a basic example - a production version would calculate lengths dynamically
        
        # Send packet
        sock.sendto(packet, (target_ip, target_port))
        print(f"Basic trap sent from {device_name} to {target_ip}:{target_port}")
        
    except Exception as e:
        print(f"Error sending trap: {e}")
    finally:
        sock.close()

def main():
    parser = argparse.ArgumentParser(description='Send a basic SNMP trap')
    parser.add_argument('--target', default='127.0.0.1', help='Target IP address')
    parser.add_argument('--port', type=int, default=16200, help='Target port')
    parser.add_argument('--community', default='public', help='SNMP community string')
    parser.add_argument('--device', default='SimulatedDevice', help='Device name')
    
    args = parser.parse_args()
    
    send_basic_trap(args.target, args.port, args.community, args.device)

if __name__ == '__main__':
    main()