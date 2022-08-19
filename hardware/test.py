msg = "f:status:sensor2:status:True"

if msg.split(":")[1] == "status":
    msg = msg.split(":")
    statusDict = {
        "True": "up",
        "False": "down",
    }

    msg[-1] = statusDict[msg[-1]]

    cmdKey = (':').join(msg[2:4])
    cmdValue = msg[-1]

    r.set(cmdKey, cmdValue)
