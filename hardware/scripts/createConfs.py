from projectConf import *
import fileinput
import sys
import os
import subprocess

# adjusts settings for the if that's going to be the AP
ipID = str(int(EDGE_SERVER.split(".")[0]) + 1)  # ie 21


def replacement(file, previousw, nextw):
    for line in fileinput.input(file, inplace=1):
        line = line.replace(previousw, nextw)
        sys.stdout.write(line)


def configDefaultHostapd():
    var1 = '#DAEMON_CONF=""'
    var2 = 'DAEMON_CONF="/etc/hostapd/hostapd.conf"'
    file = "/etc/default/hostapd"
    replacement(file, var1, var2)
    print("Added hostapd to daemon!")


def configSysctl():
    var1 = "#net.ipv4.ip_forward=1"
    var2 = "net.ipv4.ip_forward=1"
    file = "/etc/sysctl.conf"
    replacement(file, var1, var2)
    os.system('sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"')
    print("Enabled IPV4 forwarding!")


def insertAt(file, line, value):
    with open(file, "r") as f:
        contents = f.readlines()

    contents.insert(line, value)

    with open(file, "w") as f:
        contents = "".join(contents)
        f.write(contents)


def restoreIPTables():
    try:
        output = subprocess.check_output(
            "egrep '^iptables-restore < /etc/iptables.ipv4.nat$' /etc/rc.local", shell=True)
        return True
    except subprocess.CalledProcessError:
        pass

    try:
        output = subprocess.check_output(
            "egrep -n '^exit 0$' /etc/rc.local", shell=True).decode("utf-8")
        print(output)
        lineNumber = int(output.split(":")[0])
        insertAt("/etc/rc.local", lineNumber - 1,
                 "\niptables-restore < /etc/iptables.ipv4.nat\n\n")
        return True
    except subprocess.CalledProcessError:
        pass

    print("Restored IP tables!")

    return True


def natBetween(apInterface, clientInterface):
    open('/etc/iptables.ipv4.nat', 'w').close()  # deleting file contents
    os.system("sudo iptables -t nat -A POSTROUTING -o " +
              clientInterface + " -j MASQUERADE")
    os.system("sudo iptables -A FORWARD -i " + clientInterface + " -o " +
              apInterface + " -m state --state RELATED,ESTABLISHED -j ACCEPT")
    os.system("sudo iptables -A FORWARD -i " + apInterface +
              " -o " + clientInterface + " -j ACCEPT")
    os.system('sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"')
    os.system("iptables-restore < /etc/iptables.ipv4.nat")
    print(f"Added Nat between AP {apInterface} and Client {clientInterface}")


def createDhcpcdConf(id, apInterface):
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
    f.write("interface " + apInterface + '\n')
    # f.write("metric 0")
    f.write("nohook wpa_supplicant" + '\n')
    f.write("static ip_address=" + ipID + ".0." +
            str(id) + ".1/24" + '\n')  # 21.0.2.1
    f.write("static routers=" + ipID + ".0." + str(id) + ".0" + '\n')
    f.close()
    print(f"Configured DHCP server at {ipID}.0.{id}.1/24")
    return

# this is the DHCP server, and allocates IPs


def createDnsmasqConf(id, apInterface):
    f = open('/etc/dnsmasq.conf', "w")
    f.write("interface=" + apInterface + "\n")
    f.write("listen-address=" + ipID + ".0." + str(id) + ".1" + "\n")
    f.write("server=8.8.8.8\n")
    f.write("dhcp-range=" + ipID + ".0." + str(id) + ".2" +
            "," + ipID + ".0." + str(id) + ".255,12h\n")
    f.close()
    print(f"Configured Dnsmasq for the DHCP server at {ipID}.0.{id}.1")
    return


def createHostapdConf(id, apInterface):
    f = open("/etc/hostapd/hostapd.conf", "w")
    f.write("interface=" + apInterface + '\n')
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
    print(f"Configured AP credentials at APTest{id}")
    return


def createWpaSupplicantConf(id, clientInterface):  # need to add on beginning
    f = open("/etc/wpa_supplicant/wpa_supplicant-" +
             clientInterface + ".conf", "w")
    f.write("ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n")
    f.write("update_config=1\n")
    f.write("country=CA\n")
    f.write("network={" + '\n')
    f.write('ssid="APTest' + str(id - 1) + '"' + '\n')
    f.write('psk="12345678"' + '\n')
    f.write("}" + '\n')
    f.close()
    print(
        f"Configured wpa_supplicant for client {clientInterface} connecting to APTest{id - 1}")
    return


def createNetworkConf():
    f = open("/etc/network/interfaces", "w")
    f.write("source /etc/network/interfaces.d/*" + "\n")
    f.write("allow-hotplug wlan0" + "\n")
    f.write("iface wlan0 inet manual" + "\n")
    f.write("wpa-conf /etc/wpa_supplicant/wpa_supplicant-wlan0.conf" + "\n")
    f.close()
    print(f"Configured network conf for dev wlan0 ")


if __name__ == '__main__':
    createDnsmasqConf(1)
    createDhcpcdConf(1)
    # createHostapdConf(1)
    # createWpaSupplicantConf(1)
    print("Created new dnsmasq conf")
    print("Created new dhcpcd conf")
