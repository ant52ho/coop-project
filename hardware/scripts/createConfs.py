CLIENT_INTERFACE = 'wlan0'
AP_INTERFACE = 'wlan1'

# adjusts settings for the if that's going to be the AP


def createDhcpcdConf(id):
    f = open("/etc/dhcpcd.conf", "w")
    f.write('hostname' + '\n')
    f.write('clientid' + '\n')
    f.write('persistent' + '\n')
    f.write('option rapid_commit' + '\n')
    f.write('option domain_name_servers, domain_name, domain_search, host_name' + '\n')
    f.write('option classless_static_routes' + '\n')
    f.write('option interface_mtu' + '\n')
    f.write('require dhcp_server_identifier' + '\n')
    f.write('slaac private' + '\n')
    f.write("interface " + AP_INTERFACE + '\n')
    # f.write("metric 0")
    f.write("nohook wpa_supplicant" + '\n')
    f.write("static ip_address=11.0." + str(id) + ".1/24" + '\n')  # 11.0.2.1
    f.write("static routers=11.0." + str(id) + ".0" + '\n')
    f.close()
    return

# this is the DHCP server, and allocates IPs


def createDnsmasqConf(id):
    f = open('/etc/dnsmasq.conf', "w")
    f.write("interface=" + AP_INTERFACE + "\n")
    f.write("listen-address=11.0." + str(id) + ".1" + "\n")
    f.write("server=8.8.8.8\n")
    f.write("dhcp-range=11.0." + str(id) + ".2" +
            ",11.0." + str(id) + ".255,12h\n")
    f.close()
    return


def createHostapdConf(id):
    f = open("/etc/hostapd/hostapd.conf", "w")
    f.write("interface=" + AP_INTERFACE + '\n')
    f.write("driver=nl80211" + '\n')
    f.write("hw_mode=g" + '\n')
    f.write("channel=1" + '\n')
    f.write("ieee80211n=1" + '\n')
    f.write("wmm_enabled=1" + '\n')
    f.write("ht_capab=[HT40][SHORT-GI-20][DSSS_CCK-40]" + '\n')
    f.write("macaddr_acl=0" + '\n')
    f.write("ignore_broadcast_ssid=0" + '\n')
    f.write("auth_algs=1" + '\n')
    f.write("wpa=2" + '\n')
    f.write("wpa_key_mgmt=WPA-PSK" + '\n')
    f.write("rsn_pairwise=CCMP" + '\n')
    f.write("ssid=APTest" + str(id) + '\n')
    f.write("wpa_passphrase=12345678" + '\n')
    f.close()
    return


def createWpaSupplicantConf(id):  # need to add on beginning
    f = open("/etc/wpa_supplicant/wpa_supplicant-" +
             CLIENT_INTERFACE + ".conf", "w")
    f.write("ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n")
    f.write("update_config=1\n")
    f.write("country=CA\n")
    f.write("network={" + '\n')
    f.write('ssid="APTest' + str(id - 1) + '"' + '\n')
    f.write('psk="12345678"' + '\n')
    f.write("}" + '\n')
    f.close()
    return


if __name__ == '__main__':
    createDnsmasqConf(1)
    createDhcpcdConf(1)
    # createHostapdConf(1)
    # createWpaSupplicantConf(1)
    print("created new dnsmasq conf")
    print("created new dhcpcd conf")
