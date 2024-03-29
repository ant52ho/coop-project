const moment = require("moment");
const express = require("express");
const cors = require("cors");
const app = express();
const port = 5000;
const redis = require("redis");

const { TimeSeriesAggregationType } = require("@redis/time-series");

const redisClient = redis.createClient({
  socket: {
    host: "127.0.0.1",
    port: "6379", // The address of the replica
  },
  // password: '<password>' // not included for now
});

redisClient.connect().catch(console.error);

app.use(cors());

app.use("/login", (req, res) => {
  res.send({
    token: "test123",
  });
});

app.get("/api", async (req, res) => {
  try {
    const hello = await redisClient.get("hello");
    console.log(hello);
    await redisClient.set("key", "value");
    // insert body here

    var value = await redisClient.get("key");

    console.log(value);
    // value = await redisClient.ts.range("sensor2:rain", "-", "+", "+");
    // console.log(value);
    res.json({ users: [hello, "userOne", "userTwo", "userThree"] });
  } catch (e) {
    console.error(e);
  }
});

app.get("/favicon.ico", async (req, res) => {
  try {
    res.status(404).send("hello world");
  } catch (e) {
    console.error(e);
  }
});

app.get("/sensors", async (req, res) => {
  try {
    // gets all the keys but status

    var value = await redisClient.keys("sensor*:*[^status]");
    const sensors = new Set();

    console.log(value);

    var temp;
    for (var i = 0; i < value.length; i++) {
      temp = value[i].split(":")[1];
      sensors.add(temp);
    }
    console.log(Array.from(sensors));
    res.status(200).send(Array.from(sensors));
  } catch (e) {
    console.error(e);
  }
});

app.get("/status", async (req, res) => {
  var retval = [];
  try {
    // gets all status keys and sorts them
    // looks for keys with format: sensor*:status
    var value = await redisClient.keys("sensor*:status");
    value.sort(
      (a, b) =>
        parseInt(a.split(":")[0].slice(6, a.split(":")[0].length)) -
        parseInt(b.split(":")[0].slice(6, b.split(":")[0].length))
    );

    var temp;
    for (let i = 0; i < value.length; i++) {
      console.log(value[i]);
      temp = await redisClient.get(value[i]);
      retval.push({
        id: parseInt(value[i].slice(6, value[i].length - 7)),
        ip: "10.0.0." + parseInt(value[i].slice(6, value[i].length - 7)),
        status: temp,
      });
    }

    res.status(200).send(retval);
  } catch (e) {
    console.error(e);
  }
});

// DB query
// Sample input:
// http://localhost:5000/ips:10.0.0.1,10.0.0.2/sensor:tempLow/scope:1659243943,1659287143/entries:998
app.get("*", async (req, res) => {
  const url = req.originalUrl;
  console.log("url:", url);

  try {
    var query = url.split("/");

    // checks if the url is correctly formatted for db query
    if (query.length != 5) {
      res.status(400).send("error");
    }

    console.log(query);
    query.shift();

    // var ips = query[0].split(":")[1].split(",");
    // ips = ips.map((ip) => {
    //   var temp = ip.split(".");
    //   ip = temp[temp.length - 1];
    //   return "sensor" + ip;
    // });

    // gets a list of all the selected IDs
    // ie [sensor1, sensor2...]
    var ids = query[0].split(":")[1].split(",");
    ids = ids.map((id) => {
      return "sensor" + id;
    });

    // gets constants associated with the sensor
    const sensor = query[1].split(":")[1];
    var sensorLabel = await redisClient.get(sensor + ":label");
    var sensorUnit = await redisClient.get(sensor + ":unit");
    var sensorMin = await redisClient.get(sensor + ":min");
    var sensorMax = await redisClient.get(sensor + ":max");

    if (!sensorUnit) {
      //default
      sensorUnit = sensor + "Unit";
    }

    if (!sensorLabel) {
      //default
      sensorLabel = sensor + "Label";
    }

    if (!sensorMin || !sensorMax) {
      // default
      sensorMin = 0;
      sensorMax = "auto";
    } else {
      sensorMin = parseInt(sensorMin);
      sensorMax = parseInt(sensorMax);
    }

    var sensorConstants = {
      unit: sensorUnit,
      label: sensorLabel,
      min: sensorMin,
      max: sensorMax,
    };

    const scope = query[2].split(":")[1].split(",");
    const entries = query[3].split(":")[1];
    var startTime = scope[0];
    var endTime = scope[1];

    // console.log(ips);
    console.log(ids);
    console.log(sensor);
    console.log(startTime);
    console.log(endTime);
    console.log(entries);

    var data = [];
    var value;

    for (let sensorIndex = 0; sensorIndex < ids.length; sensorIndex++) {
      const sensorNumber = ids[sensorIndex];
      // const sensorNumber = ips[sensorIndex];
      // const cmd = ips[sensorIndex] + ":" + sensor;
      var cmd = ids[sensorIndex] + ":" + sensor;
      console.log("cmd:", cmd);

      // the key may or may not exist, use try
      try {
        var bucket;

        if (startTime === "-" && endTime === "+") {
          // if "all"
          bucket = 1;
        } else if (endTime - startTime <= 60 * 60 * 2) {
          // ideally should be "RETENTION" constant
          cmd = ids[sensorIndex] + ":" + sensor + ":all";
          bucket = Math.round((endTime - startTime) / entries);
        } else {
          bucket = Math.round((endTime - startTime) / entries);
        }
        console.log("cmd:", cmd, startTime, endTime);

        value = await redisClient.ts.range(cmd, startTime, endTime, {
          // value = await redisClient.ts.range(cmd, "-", "+", {
          COUNT: entries,
          // Group into 1 second averages.
          AGGREGATION: {
            type: TimeSeriesAggregationType.AVERAGE,
            // timeBucket: 1000,
            timeBucket: bucket,
          },
        });
        // console.log("value:", value);
      } catch (e) {
        console.log(e);
        value = [];
      }

      // console.log(value);

      data.push({
        sensor: sensorNumber,
        data: value,
        constants: sensorConstants,
      });
    }
    console.log(data[0]);

    res.status(200).send(data);
  } catch (e) {
    console.error(e);
  }
});

app.listen(port, () => {
  console.log("server started on port", port);
});
