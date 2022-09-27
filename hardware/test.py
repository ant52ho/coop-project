ip = "192.169.179.121"
print(ip.split(".")[0])
print(ip.split(".")[-1])
print(".".join(ip.split(".")[:3]))
print(".".join(ip.split(".")[:3]) + ".0/24")
print(int(ip.split(".")[-1]) + 1)
