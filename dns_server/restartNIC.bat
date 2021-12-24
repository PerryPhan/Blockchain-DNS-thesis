
    netsh winsock reset
    netsh int ip reset
    netsh advfirewall reset 
    ipconfig /flushdns
    ipconfig /release
    ipconfig /renew
    netsh interface ipv4 set address name="Wi-Fi" static 192.168.43.7 255.255.255.0 192.168.43.1
    netsh advfirewall set publicprofile state off
    