import { useLocation } from "react-router-dom";
import {
  LineChart,
  Line,
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
import {
  Stack,
  Autocomplete,
  TextField,
  Box,
  Button,
  Typography,
} from "@mui/material";
import { AdapterMoment } from "@mui/x-date-pickers/AdapterMoment";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { DateTimePicker } from "@mui/x-date-pickers/DateTimePicker";
import { useState, useEffect } from "react";
import { MultiSelect } from "./MultiSelect";
import { OutputGraphs } from "./OutputGraphs";
import moment from "moment";

export const DataDisplay = () => {
  const ipsList = [
    "10.0.0.1",
    "10.0.0.2",
    "10.0.0.3",
    "10.0.0.4",
    "10.0.0.5",
    "10.0.0.6",
    "10.0.0.7",
    "10.0.0.8",
    "10.0.0.9",
    "10.0.0.10",
  ];

  const sensorList = ["Gas1", "Gas2", "Gas3", "Gas4", "Gas5", "Gas6"];

  const timeList = [
    "60 minutes",
    "3 hours",
    "12 hours",
    "24 hours",
    "3 days",
    "1 week",
    "1 month",
    "Custom",
    "",
  ];

  const graphList = [
    "Line",
    "Graph 1",
    "Graph 2",
    "Graph 3",
    "Graph 4",
    "Graph 5",
  ];

  const [startDate, setStartDate] = useState(moment());
  const [endDate, setEndDate] = useState(moment());
  const [scope, setScope] = useState("");
  const [ips, setIps] = useState([]);
  const [sensors, setSensors] = useState([]);
  const [graphs, setGraphs] = useState(["Line"]);
  const [entries, setEntries] = useState(1000);
  const [cmd, setCmd] = useState({
    graphs: graphs,
    ips: ips,
    sensors: sensors,
    scope: scope,
    startDate: startDate,
    endDate: endDate,
    entries: entries,
  });
  var valid = false;

  const location = useLocation();
  if (location.state) {
    const id = location.state.id;
    console.log(id);
    console.log(ips);
    setIps(["10.0.0." + id]);
    // location.state
    location.state = null;
  }

  const handleStartDateChange = (newValue) => {
    setStartDate(newValue);
    console.log(startDate);
    console.log(newValue);
  };
  const handleEndDateChange = (newValue) => {
    setEndDate(newValue);
    console.log(endDate);
    console.log(newValue);
  };

  const handleGraphChange = (event) => {
    const value = event.target.value;
    if (value[value.length - 1] === "all") {
      setGraphs(graphs.length === graphList.length ? [] : graphList);
      return;
    }
    setGraphs(value);
  };

  const handleEntriesChange = (event) => {
    const value = event.target.value;
    setEntries(value);
    console.log(entries);
  };

  const handleIPChange = (event) => {
    const value = event.target.value;
    if (value[value.length - 1] === "all") {
      setIps(ips.length === ipsList.length ? [] : ipsList);
      return;
    }
    setIps(value);
    console.log(ips);
  };

  const handleSensorChange = (event) => {
    const value = event.target.value;
    if (value[value.length - 1] === "all") {
      setSensors(sensors.length === sensorList.length ? [] : sensorList);
      return;
    }
    setSensors(value);
    console.log(sensors);
  };

  const handleScopeChange = (event, newValue) => {
    setScope(newValue);
    console.log(scope);
  };

  const handleSubmit = () => {
    if (valid) {
      setCmd({
        graphs: graphs,
        ips: ips,
        sensors: sensors,
        scope: scope,
        startDate: startDate,
        endDate: endDate,
        entries: entries,
      });
    }
  };

  useEffect(() => {
    console.log(entries);
    valid =
      ips.length !== 0 &&
      graphs.length !== 0 &&
      sensors.length !== 0 &&
      entries != 0 &&
      scope !== null &&
      scope !== "";

    if (
      scope &&
      scope == "Custom" &&
      (startDate > endDate || !startDate.isValid() || !endDate.isValid())
    ) {
      valid = false;
    }

    console.log(valid);
    // console.log(startDate.isValid());
  });

  return (
    <Stack direction="column" spacing={5}>
      <Stack direction="row" spacing={3} display={"border-box"}>
        <MultiSelect
          label="Graphs"
          error={graphs.length === 0}
          options={graphList}
          value={graphs}
          handleChange={handleGraphChange}
        />
        <TextField
          id="entries"
          sx={{ width: 200 }}
          defaultValue={1000}
          error={entries == 0}
          // value={entries}
          label="Max. Entries per Node"
          type="number"
          InputLabelProps={{
            shrink: true,
          }}
          onChange={handleEntriesChange}
        />
      </Stack>
      <Stack direction="row" spacing={3} display={"border-box"}>
        <MultiSelect
          label="IPs"
          options={ipsList}
          value={ips}
          error={ips.length === 0}
          handleChange={handleIPChange}
        />
        <MultiSelect
          label="Sensors"
          options={sensorList}
          value={sensors}
          error={sensors.length === 0}
          handleChange={handleSensorChange}
        />

        <Autocomplete
          id="Time"
          options={timeList}
          sx={{ width: 200 }}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Time"
              error={scope === "" || scope === null}
            />
          )}
          freeSolo={false}
          value={scope}
          onChange={handleScopeChange}
        />
      </Stack>
      {scope === "Custom" && (
        <Stack direction="row" spacing={2}>
          <LocalizationProvider dateAdapter={AdapterMoment}>
            <DateTimePicker
              label="Time Start"
              value={startDate}
              onChange={handleStartDateChange}
              renderInput={(params) => (
                <TextField
                  {...params}
                  error={startDate > endDate || !scope || !startDate.isValid()}
                />
              )}
            />
            <DateTimePicker
              label="Time End"
              value={endDate}
              onChange={handleEndDateChange}
              renderInput={(params) => (
                <TextField
                  {...params}
                  error={startDate > endDate || !scope || !endDate.isValid()}
                />
              )}
            />
          </LocalizationProvider>
        </Stack>
      )}
      {startDate > endDate && scope === "Custom" && (
        <Typography color="error"> Please enter a valid time </Typography>
      )}
      <Box>
        <Button
          variant="contained"
          size="large"
          onClick={handleSubmit}
          disabled={valid}
        >
          Go!
        </Button>
      </Box>

      <OutputGraphs cmd={cmd} />

      {graphs.includes("Line") && (
        <LineChart
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
            <XAxis type="number" dataKey="x" name="stature" unit="cm" />
            <YAxis type="number" dataKey="y" name="weight" unit="kg" />
            <ZAxis type="number" range={[100]} />
            <Tooltip cursor={{ strokeDasharray: "3 3" }} />
            <Legend />
            <Scatter
              name="A school"
              data={data01}
              fill="#8884d8"
              line
              shape="cross"
              // lineJointType="monotoneX"
            />
            <Scatter
              name="B school"
              data={data02}
              fill="#82ca9d"
              line
              shape="diamond"
              // lineJointType="monotoneX"
            />
          </ScatterChart>
        </ResponsiveContainer>
      </Box>
    </Stack>
  );
};

const data = [
  {
    name: 2,
    uv: 4000,
    pv: 2400,
    amt: 2400,
  },
  {
    name: 3,
    uv: 3000,
    pv: 1398,
    amt: 2210,
  },
  {
    name: 4,
    uv: 2000,
    pv: 9800,
    amt: 2290,
  },
  {
    name: 1,
    uv: 2780,
    pv: 3908,
    amt: 2000,
  },
  {
    name: 6,
    uv: 1890,
    pv: 4800,
    amt: 2181,
  },
  {
    name: 3,
    uv: 2390,
    pv: 3800,
    amt: 2500,
  },
  {
    name: 5,
    uv: 3490,
    pv: 4300,
    amt: 2100,
  },
];

const data01 = [
  { x: 10, y: 30 },
  { x: 30, y: 200 },
  { x: 45, y: 100 },
  { x: 50, y: 400 },
  { x: 70, y: 150 },
  { x: 100, y: 250 },
];
const data02 = [
  { x: 30, y: 20 },
  { x: 50, y: 180 },
  { x: 75, y: 240 },
  { x: 100, y: 100 },
  { x: 120, y: 190 },
];
