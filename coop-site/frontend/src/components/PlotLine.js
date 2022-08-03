import React from "react";
import { useState, useEffect } from "react";
import axios from "axios";
import {
  ScatterChart,
  Scatter,
  CartesianGrid,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Box } from "@mui/material";

function toSeconds(scope, startDate, endDate) {
  const date = (new Date().getTime() / 1000) | 0; // gets the current time in seconds
  scope = scope.split(" ");

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

export const PlotLine = (props) => {
  const toggle = props.toggle;
  const cmd = props.cmd;
  var sensor = props.sensor;
  const ips = cmd.ips;
  var scope = cmd.scope;
  const entries = cmd.entries;
  var startDate = cmd.startDate;
  var endDate = cmd.endDate;

  // for DB querying
  const [backendData, setBackendData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
  var retval =
    "/" +
    [
      "ips:" + ips.join(),
      "sensor:" + sensor,
      "scope:" + scope[0] + "," + scope[1],
      "entries:" + entries,
    ].join("/");

  console.log(retval);

  // A one time useEffect render
  useEffect(() => {
    const getData = async () => {
      try {
        const response = await axios.get(retval);
        setBackendData(response.data);
        console.log(response.data);
        setError(null);
      } catch (err) {
        setError(err.message);
        setBackendData([]);
      } finally {
        setLoading(false);
      }
    };
    getData();
  }, [toggle]);
  return (
    <div>
      {props.sensor}
      {props.cmd.ips}
      {props.cmd.scope}
      <Box sx={{ width: 600, height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart
            width={500}
            height={400}
            margin={{
              top: 20,
              right: 20,
              bottom: 20,
              left: 20,
            }}
          >
            <CartesianGrid />
            <XAxis
              type="number"
              dataKey="timestamp"
              name="stature"
              domain={["dataMin", "dataMax"]}
              unit="s"
            />
            <YAxis type="number" dataKey="value" name="weight" unit="" />
            <ZAxis type="number" range={[100]} />
            <Tooltip cursor={{ strokeDasharray: "3 3" }} />
            <Legend />
            {backendData.map((node, i) => (
              <Scatter
                key={i}
                name={node.sensor}
                data={node.data}
                fill="#8884d8"
                line
                shape="circle"
              />
            ))}
          </ScatterChart>
        </ResponsiveContainer>
      </Box>
    </div>
  );
};

// const data01 = [
//   { timestamp: 1387601280, value: 74 },
//   { timestamp: 1387687680, value: 56 },
//   { timestamp: 1387774080, value: 58 },
//   { timestamp: 1387860480, value: 61 },
//   { timestamp: 1387946880, value: 58 },
// ];
