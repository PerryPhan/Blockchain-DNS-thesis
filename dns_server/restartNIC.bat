netsh winsock reset
netsh int ip reset
netsh advfirewall reset
ipconfig /flushdns
ipconfig /release
ipconfig /renew
netsh interface ipv4 set address name="Wi-Fi" static 192.168.1.7 255.255.255.0 192.168.1.1