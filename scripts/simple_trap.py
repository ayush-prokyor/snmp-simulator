#!/usr/bin/env python
# Simple SNMP trap sender

from pysnmp.hlapi import *
import time
import argparse

def send_simple_trap(target_host, target_port, community_string, device_name):
    """
    Send a simple SNMP trap to a target
    """
    print(f"Sending trap from {device_name} to {target_host}:{target_port}")
    
    # Create trap data
    system_uptime = int(time.time()) * 100  # Convert to centiseconds
    trap_oid = '1.3.6.1.6.3.1.1.5.3'  # linkDown
    interface_index = 1
    
    # Send trap
    errorIndication, errorStatus, errorIndex, varBinds = next(
        sendNotification(
            SnmpEngine(),
            CommunityData(community_string),
            UdpTransportTarget((target_host, target_port)),
            ContextData(),
            'trap',
            NotificationType(
                ObjectIdentity(trap_oid)
            ).addVarBinds(
                ('1.3.6.1.2.1.1.3.0', v2c.Integer32(system_uptime)),  # sysUpTime
                ('1.3.6.1.2.1.1.5.0', v2c.OctetString(device_name)),  # sysName
                ('1.3.6.1.2.1.2.2.1.1.1', v2c.Integer32(interface_index)),  # ifIndex
                ('1.3.6.1.2.1.2.2.1.7.1', v2c.Integer32(2)),  # ifAdminStatus down(2)
                ('1.3.6.1.2.1.2.2.1.8.1', v2c.Integer32(2))   # ifOperStatus down(2)
            )
        )
    )

    if errorIndication:
        print(f'Error: {errorIndication}')
    else:
        print('Trap sent successfully')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send SNMP traps')
    parser.add_argument('--target', '-t', default='127.0.0.1',
                        help='Target host address (default: 127.0.0.1)')
    parser.add_argument('--port', '-p', type=int, default=16200,
                        help='Target port (default: 16200)')
    parser.add_argument('--community', '-c', default='public',
                        help='SNMP community string (default: public)')
    parser.add_argument('--device', '-d', default='SimulatedDevice',
                        help='Device name (default: SimulatedDevice)')
    
    args = parser.parse_args()
    
    send_simple_trap(args.target, args.port, args.community, args.device)