# #!/usr/bin/env python
# # Send SNMP trap example

# from pysnmp.hlapi import *
# from pysnmp.smi import builder, view, compiler, rfc1902
# import sys
# import time

# def send_trap(agent_port, target_port, community_string, device_name):
#     """
#     Send an SNMP trap to a target
#     """
#     print(f"Sending trap from {device_name} on port {agent_port} to target port {target_port}")
    
#     errorIndication, errorStatus, errorIndex, varBinds = next(
#         sendNotification(
#             SnmpEngine(),
#             CommunityData(community_string),
#             UdpTransportTarget(('127.0.0.1', target_port)),
#             ContextData(),
#             'trap',
#             NotificationType(
#                 ObjectIdentity('1.3.6.1.6.3.1.1.5.4')  # linkDown trap
#             ).addVarBinds(
#                 ('1.3.6.1.2.1.1.3.0', TimeTicks(int(time.time()) % 2147483647)),
#                 ('1.3.6.1.2.1.1.5.0', OctetString(device_name)),
#                 ('1.3.6.1.2.1.2.2.1.1.1', Integer(1)),
#                 ('1.3.6.1.2.1.2.2.1.7.1', Integer(2)),  # ifAdminStatus down(2)
#                 ('1.3.6.1.2.1.2.2.1.8.1', Integer(2))   # ifOperStatus down(2)
#             )
#         )
#     )

#     if errorIndication:
#         print(f'Error: {errorIndication}')
#     else:
#         print('Trap sent successfully')

# if __name__ == '__main__':
#     # Default parameters
#     agent_port = 16100
#     target_port = 16200  # Your Node.js app's trap listener port
#     community = 'public'
#     device = 'SimulatedDevice1'
    
#     # Allow command line arguments
#     if len(sys.argv) > 1:
#         agent_port = int(sys.argv[1])
#     if len(sys.argv) > 2:
#         target_port = int(sys.argv[2])
#     if len(sys.argv) > 3:
#         community = sys.argv[3]
#     if len(sys.argv) > 4:
#         device = sys.argv[4]
    
#     send_trap(agent_port, target_port, community, device)