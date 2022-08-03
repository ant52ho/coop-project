import { useLocation } from "react-router-dom";
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
import axios from "axios";

export const DataDisplay = () => {
  // const ipsList = [
  //   "10.0.0.1",
  //   "10.0.0.2",
  //   "10.0.0.3",
  //   "10.0.0.4",
  //   "10.0.0.5",
  //   "10.0.0.6",
  //   "10.0.0.7",
  //   "10.0.0.8",
  //   "10.0.0.9",
  //   "10.0.0.10",
  // ];

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
  const [toggle, setToggle] = useState(false);
  const [errors, setErrors] = useState({
    graphs: { error: false, text: "Select a graph" },
    ips: { error: false, text: "Select an IP" },
    sensors: { error: false, text: "Select a sensor" },
    scope: { error: false, text: "Select a time" },
    entries: { error: false, text: "Select a non-zero value" },
    startDate: {
      error: false,
      text: "error",
    },
    endDate: {
      error: false,
      text: "error",
    },
  });
  const [statusData, setStatusData] = useState([]);
  const [ipsList, setIpsList] = useState([]);
  const [reloadToggle, setReloadToggle] = useState(false);

  // const [valid, setValid] = useState(false);

  var valid = false;

  const location = useLocation();
  if (location.state) {
    const id = location.state.id;
    console.log(id);
    console.log(ips);
    setIps(["10.0.0." + id]);
    location.state = null;
  }

  const handleStartDateChange = (newValue) => {
    setStartDate(newValue);
  };
  const handleEndDateChange = (newValue) => {
    setEndDate(newValue);
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
  };

  const handleIPChange = (event) => {
    const value = event.target.value;
    if (value[value.length - 1] === "all") {
      setIps(ips.length === ipsList.length ? [] : ipsList);
      return;
    }
    setIps(value);
  };

  const handleSensorChange = (event) => {
    const value = event.target.value;
    if (value[value.length - 1] === "all") {
      setSensors(sensors.length === sensorList.length ? [] : sensorList);
      return;
    }
    setSensors(value);
  };

  const handleScopeChange = (event, newValue) => {
    setScope(newValue);
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
      setToggle(!toggle);
      console.log("toggle:", toggle);
    }
  };

  const handleReload = () => {
    setReloadToggle(!reloadToggle);
    console.log("toggle:", reloadToggle);
  };

  useEffect(() => {
    console.log(entries);
    valid = !(
      ips.length === 0 ||
      graphs.length === 0 ||
      sensors.length === 0 ||
      entries == 0 ||
      scope === null ||
      scope === "" ||
      (scope == "Custom" &&
        (startDate > endDate || !startDate.isValid() || !endDate.isValid()))
    );

    // setValid(
    //   !(
    //     ips.length === 0 ||
    //     graphs.length === 0 ||
    //     sensors.length === 0 ||
    //     entries == 0 ||
    //     scope === null ||
    //     scope === "" ||
    //     (scope == "Custom" &&
    //       (startDate > endDate || !startDate.isValid() || !endDate.isValid()))
    //   )
    // );

    console.log("valid selection?", valid);
  });

  useEffect(() => {
    const getData = async () => {
      try {
        const response = await axios.get("/status");
        setStatusData(response.data);
        console.log(response.data);
      } catch (err) {
        setStatusData([]);
      }
    };
    getData();
  }, [reloadToggle]);

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

      <Stack direction="row" spacing={3}>
        <Box>
          <Button variant="contained" size="large" onClick={handleSubmit}>
            Go!
          </Button>
        </Box>

        <Box>
          <Button variant="contained" size="large" onClick={handleReload}>
            Reload!
          </Button>
        </Box>
      </Stack>

      <OutputGraphs cmd={cmd} toggle={toggle} />
    </Stack>
  );
};
