import subprocess
import fileinput
import sys


def replacement(file, previousw, nextw):
    for line in fileinput.input(file, inplace=1):
        line = line.replace(previousw, nextw)
        sys.stdout.write(line)


def restoreIPTables():
    try:
        output = subprocess.check_output(
            "egrep '^iptables-restore < /etc/iptables.ipv4.nat$' /etc/rc.local", shell=True)
        return True
    except subprocess.CalledProcessError:
        pass

    var1 = "exit 0"
    var2 = "iptables-restore < /etc/iptables.ipv4.nat\n\nexit 0"
    file = "/etc/rc.local"
    replacement(file, var1, var2)

    return True


restoreIPTables()
