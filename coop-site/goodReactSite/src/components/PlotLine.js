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
import { Box, Stack, Typography, Card, CardContent } from "@mui/material";
import { interpolateColors } from "../scripts/generateColour";
import { interpolateRainbow } from "d3-scale-chromatic";
import moment from "moment";

function toSeconds(scope, startDate, endDate) {
  const date = (new Date().getTime() / 1000) | 0; // gets the current time in seconds
  scope = scope.split(" ");

  var unit = scope[1];
  var duration = scope[0];

  if (!unit) {
    unit = scope[0];
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
  } else if (unit === "All") {
    start = "-";
    end = "+";
    console.log("start, end", start, end);
    format = "MMMM D;M/D";
  } else if (unit === "Custom") {
    start = startDate / 1000;
    end = endDate / 1000;
    format = "Y/M/D;M/D";
  }

  return { start: start, end: end, format: format };
}

export const PlotLine = (props) => {
  const toggle = props.toggle;
  const cmd = props.cmd;
  var sensor = props.sensor;
  // const ips = cmd.ips;
  const ids = cmd.ids;
  var scope = cmd.scope;
  const entries = cmd.entries;
  var startDate = cmd.startDate;
  var endDate = cmd.endDate;

  // for DB querying
  const [backendData, setBackendData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // we convert the sensor to a comprehensible format -- done in cloudScript
  // const dict = {
  //   Gas1: "tempHigh",
  //   Gas2: "tempLow",
  //   Gas3: "wind",
  //   Gas4: "rain",
  // };

  // if (sensor in dict) {
  //   sensor = dict[sensor];
  // }

  var scopeDetails = toSeconds(scope, startDate, endDate);
  var retval =
    "/" +
    [
      "ids:" + ids.join(),
      // "ips:" + ips.join(),
      "sensor:" + sensor,
      "scope:" + scopeDetails.start + "," + scopeDetails.end,
      "entries:" + entries,
    ].join("/");

  // console.log(retval);

  const formatLong = scopeDetails.format.split(";")[0];
  const formatShort = scopeDetails.format.split(";")[1];

  startDate = scopeDetails.start;
  endDate = scopeDetails.end;

  const colorRangeInfo = {
    colorStart: 0,
    colorEnd: 1,
    useEndAsStart: false,
  };

  const colours = interpolateColors(
    ids.length,
    // ips.length,
    interpolateRainbow,
    colorRangeInfo
  );

  // A one time useEffect render
  useEffect(() => {
    const getData = async () => {
      try {
        const response = await axios.get(retval);
        setBackendData(response.data);
        console.log("data collected:", response.data);
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

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <Card variant="outlined" p={2}>
          <CardContent>
            {/* Time */}
            <p>{`${payload[0].name}: ${moment(payload[0].value * 1000).format(
              "Y/M/D kk:mm"
            )}`}</p>
            {/* Label */}
            <p>{`${payload[1].name}: ${payload[1].value}`}</p>
          </CardContent>
        </Card>
      );
    }

    return null;
  };

  return (
    <Box display={"inline-block"}>
      {backendData.length !== 0 && (
        <Stack
          display={"flex"}
          alignItems={"center"}
          direction={"column"}
          marginBottom={5}
        >
          {scope === "All" ? (
            <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>
              Line graph measuring {props.sensor} for all available points
            </Typography>
          ) : (
            <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>
              Line graph for: {props.sensor} from{" "}
              {moment(startDate * 1000).format(formatLong)} to{" "}
              {moment(endDate * 1000).format(formatLong)}
            </Typography>
          )}
          <Box sx={{ width: 800, height: 350 }}>
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart
                width={"100%"}
                height={"100%"}
                margin={{
                  top: 20,
                  right: 20,
                  bottom: 0,
                  left: 40,
                }}
              >
                <CartesianGrid />
                <XAxis
                  type="number"
                  dataKey="timestamp"
                  name="Time"
                  domain={["dataMin", "dataMax"]}
                  // unit=""
                  tickCount="10"
                  tickFormatter={(unixTime) =>
                    moment(unixTime * 1000).format(formatShort)
                  }
                />
                <YAxis
                  type="number"
                  dataKey="value"
                  domain={[
                    backendData[0].constants.min,
                    backendData[0].constants.max,
                  ]}
                  name={backendData[0].constants.label}
                  label={{
                    value: `${backendData[0].constants.label} (${backendData[0].constants.unit})`,
                    angle: -90,
                    position: "insideLeft",
                    dy: 70,
                  }}
                />
                <ZAxis type="number" range={[100]} />
                <Tooltip content={<CustomTooltip />} />
                {/* <Tooltip /> */}
                <Legend
                  layout="horizontal"
                  verticalAlign="top"
                  align="center"
                  wrapperStyle={{ paddingBottom: 15 }}
                />
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
          <Typography variant="subtitle1">Date ({formatShort})</Typography>
        </Stack>
      )}
      {/* <Stack> */}
    </Box>
  );
};

// const data01 = [
//   { timestamp: 1387601280, value: 74 },
//   { timestamp: 1387687680, value: 56 },
//   { timestamp: 1387774080, value: 58 },
//   { timestamp: 1387860480, value: 61 },
//   { timestamp: 1387946880, value: 58 },
// ];
