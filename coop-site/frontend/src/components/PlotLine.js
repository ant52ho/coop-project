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
import { Box, Stack, Typography } from "@mui/material";
import { interpolateColors } from "../scripts/generateColour";
import { interpolateRainbow } from "d3-scale-chromatic";
import moment from "moment";

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

  var end = date;
  var start = date;
  var format = "Y/M/D";

  if (unit === "minute") {
    start = end - duration * 60;
    format = "MMM D, h:mma;k:mm";
  } else if (unit === "hour") {
    start = end - duration * 60 * 60;
    format = "MMM D, h:mma;M/D k:mm";
  } else if (unit === "day") {
    start = end - duration * 60 * 60 * 24;
    format = "MMM D, h:mma;M/D kk:mm";
  } else if (unit === "week") {
    start = end - duration * 60 * 60 * 24 * 7;
    format = "MMMM D;M/D";
  } else if (unit === "month") {
    start = end - duration * 60 * 60 * 24 * 30;
    format = "MMM D, YYYY;M/D";
  } else if (unit === "Custom") {
    start = startDate;
    end = endDate;
    format = "Y/M/D";
  }

  return { start: start, end: end, format: format };
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
      "scope:" + scope.start + "," + scope.end,
      "entries:" + entries,
    ].join("/");

  const formatLong = scope.format.split(";")[0];
  const formatShort = scope.format.split(";")[1];
  startDate = scope.start;
  endDate = scope.end;

  console.log(retval);

  const colorRangeInfo = {
    colorStart: 0,
    colorEnd: 1,
    useEndAsStart: false,
  };
  const colours = interpolateColors(
    ips.length,
    interpolateRainbow,
    colorRangeInfo
  );

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
      <Stack display={"flex"} alignItems={"center"}>
        <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>
          Line graph for: {props.sensor} from{" "}
          {moment(startDate * 1000).format(formatLong)} to{" "}
          {moment(endDate * 1000).format(formatLong)}
        </Typography>
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
                unit=""
                tickCount="10"
                tickFormatter={(unixTime) =>
                  moment(unixTime * 1000).format(formatShort)
                }
                // tickFormatter={(val) => val}
              />
              <YAxis type="number" dataKey="value" name="weight" unit="unit" />
              <ZAxis type="number" range={[100]} />
              <Tooltip cursor={{ strokeDasharray: "3 3" }} />
              <Legend />
              {backendData.map((node, i) => (
                <Scatter
                  key={i}
                  name={node.sensor}
                  data={node.data}
                  fill={colours[i]}
                  line
                  shape="circle"
                />
              ))}
            </ScatterChart>
          </ResponsiveContainer>
        </Box>
      </Stack>
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
