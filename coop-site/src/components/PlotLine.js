import React from "react";
import { useState, useEffect } from "react";

{
  /* <LineChart
          width={730}
          height={250}
          data={data}
          margin={{ top: 0, right: 0, left: 0, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="pv" stroke="#8884d8" />
          <Line type="monotone" dataKey="uv" stroke="#82ca9d" />
          <Line type="monotone" dataKey="amt" stroke="#82ca9d" />
        </LineChart>
      )}
    </Stack> */
}

function toSeconds(scope, startDate, endDate) {
  const date = (new Date().getTime() / 1000) | 0; // gets the current time in seconds
  scope = scope.split(" ");

  // cuts scope variable

  var unit = scope[1];
  var duration = scope[0];

  if (!unit) {
    unit = "Custom";
  } else if (unit[unit.length - 1] === "s") {
    unit = unit.slice(0, unit.length - 1);
  }

  var end;
  var start = date;

  if (unit === "minute") {
    end = start + duration * 60;
  } else if (unit === "hour") {
    end = start + duration * 60 * 60;
  } else if (unit === "day") {
    end = start + duration * 60 * 60 * 24;
  } else if (unit === "week") {
    end = start + duration * 60 * 60 * 24 * 7;
  } else if (unit === "month") {
    end = start + duration * 60 * 60 * 24 * 30;
  } else if (unit === "Custom") {
    start = startDate;
    end = endDate;
  }

  return [start, end];
}

// const cmd = {
//     graphs: graphs,
//     ips: ips,
//     sensors: sensors,
//     scope: scope,
//     startDate: startDate,
//     endDate: endDate,
// };
export const PlotLine = (props) => {
  const cmd = props.cmd;
  var sensor = props.sensor;
  const ips = cmd.ips;
  var scope = cmd.scope;
  const entries = cmd.entries;
  const [data, setData] = useState();
  var startDate = cmd.startDate;
  var endDate = cmd.endDate;

  // we convert the sensor to a comprehensible format
  const dict = {
    Gas1: "tempHigh",
    Gas2: "tempLow",
    Gas3: "wind",
    Gas4: "rain",
  };
  if (sensor in dict) {
    sensor = dict[sensor];
  }

  scope = toSeconds(scope, startDate, endDate);
  var retval = [
    "ips:" + ips.join(),
    "sensor:" + sensor,
    "scope:" + scope[0] + "," + scope[1],
    "entries:" + entries,
  ].join("/");

  console.log(retval);

  console.log([sensor, ips, scope, startDate, endDate]);

  // Query data here
  // const redis = require("redis");

  // async function queryData() {
  //   const client = redis.createClient({
  //     socket: {
  //       host: "127.0.0.1",
  //       port: "7000", // The address of the replica
  //     },
  //     // password: '<password>' // not included for now
  //   });
  //   await client.connect();

  //   try {
  //     await client.set("key", "value");
  //     // insert body here

  //     var value = await client.get("key");

  //     console.log(value);
  //     value = await client.ts.range("sensor2:rain", "-", "+", "+");
  //     console.log(value);
  //   } catch (e) {
  //     console.error(e);
  //   }

  //   await client.quit();
  // }

  return (
    <div>
      {props.sensor}
      {props.cmd.ips}
      {props.cmd.scope}
    </div>
  );
};

// const data = [
//   {
//     name: "Page A",
//     uv: 4000,
//     pv: 2400,
//     amt: 2400,
//   },
//   {
//     name: "Page B",
//     uv: 3000,
//     pv: 1398,
//     amt: 2210,
//   },
