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

  // const sensorList = ["Gas1", "Gas2", "Gas3", "Gas4", "Gas5", "Gas6"];

  const timeList = [
    "60 minutes",
    "3 hours",
    "12 hours",
    "3 days",
    "1 week",
    "1 month",
    "All",
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
    graphs: { error: false, text: "" },
    ips: { error: false, text: "" },
    sensors: { error: false, text: "" },
    scope: { error: false, text: "" },
    entries: { error: false, text: "" },
    startDate: { error: false, text: "" },
    endDate: { error: false, text: "" },
  });
  const [statusData, setStatusData] = useState([]);
  const [ipsList, setIpsList] = useState([]);
  const [sensorList, setSensorList] = useState([]);
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
    if (newValue > endDate || !scope || !newValue.isValid()) {
      setErrors((prevState) => ({
        ...prevState,
        startDate: { error: true, text: "Select a valid time" },
      }));
    } else {
      setErrors((prevState) => ({
        ...prevState,
        startDate: { error: false, text: "" },
      }));
    }
    setStartDate(newValue);
  };
  const handleEndDateChange = (newValue) => {
    if (startDate > newValue || !scope || !newValue.isValid()) {
      setErrors((prevState) => ({
        ...prevState,
        endDate: { error: true, text: "Select a valid time" },
      }));
    } else {
      setErrors((prevState) => ({
        ...prevState,
        endDate: { error: false, text: "" },
      }));
    }
    setEndDate(newValue);
  };

  const handleGraphChange = (event) => {
    const value = event.target.value;
    if (
      value.length === 0 ||
      (value[value.length - 1] === "all" && graphs.length === graphList.length)
    ) {
      setErrors((prevState) => ({
        ...prevState,
        graphs: { error: true, text: "Select a graph" },
      }));
    } else {
      setErrors((prevState) => ({
        ...prevState,
        graphs: { error: false, text: "" },
      }));
    }
    if (value[value.length - 1] === "all") {
      setGraphs(graphs.length === graphList.length ? [] : graphList);
      return;
    }
    setGraphs(value);
  };

  const handleEntriesChange = (event) => {
    const value = event.target.value;
    if (value === null || value == 0) {
      setErrors((prevState) => ({
        ...prevState,
        entries: { error: true, text: "Enter a non-zero number" },
      }));
    } else {
      setErrors((prevState) => ({
        ...prevState,
        entries: { error: false, text: "" },
      }));
    }
    setEntries(value);
  };

  const handleIPChange = (event) => {
    const value = event.target.value;
    if (
      value.length === 0 ||
      (value[value.length - 1] === "all" && ips.length === ipsList.length)
    ) {
      setErrors((prevState) => ({
        ...prevState,
        ips: { error: true, text: "Select an IP" },
      }));
    } else {
      setErrors((prevState) => ({
        ...prevState,
        ips: { error: false, text: "" },
      }));
    }

    if (value[value.length - 1] === "all") {
      setIps(ips.length === ipsList.length ? [] : ipsList);
      return;
    }
    setIps(value);
  };

  const handleSensorChange = (event) => {
    const value = event.target.value;
    if (
      value.length === 0 ||
      (value[value.length - 1] === "all" &&
        sensors.length === sensorList.length)
    ) {
      setErrors((prevState) => ({
        ...prevState,
        sensors: { error: true, text: "Select a sensor" },
      }));
    } else {
      setErrors((prevState) => ({
        ...prevState,
        sensors: { error: false, text: "" },
      }));
    }

    if (value[value.length - 1] === "all") {
      setSensors(sensors.length === sensorList.length ? [] : sensorList);
      return;
    }
    setSensors(value);
  };

  const handleScopeChange = (event, newValue) => {
    if (newValue === null || newValue === "") {
      setErrors((prevState) => ({
        ...prevState,
        scope: { error: true, text: "Select a time" },
      }));
    } else {
      setErrors((prevState) => ({
        ...prevState,
        scope: { error: false, text: "" },
      }));
    }
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
  });

  useEffect(() => {
    console.log("collecting status data");
    const getData = async () => {
      try {
        var tempIpsList = [];

        // status query
        const status = await axios.get("/status");
        setStatusData(status.data);

        for (var i = 0; i < status.data.length; i++) {
          tempIpsList.push(status.data[i].ip);
        }
        setIpsList(tempIpsList);

        // sensor query
        const sensorsReq = await axios.get("/sensors");
        setSensorList(sensorsReq.data);
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
          error={errors.graphs.error}
          helperText={errors.graphs.text}
          options={graphList}
          value={graphs}
          handleChange={handleGraphChange}
        />
        <TextField
          id="entries"
          sx={{ width: 200 }}
          defaultValue={1000}
          error={errors.entries.error}
          helperText={errors.entries.text}
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
          error={errors.ips.error}
          helperText={errors.ips.text}
          handleChange={handleIPChange}
        />
        <MultiSelect
          label="Sensors"
          options={sensorList}
          value={sensors}
          error={errors.sensors.error}
          helperText={errors.sensors.text}
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
              error={errors.scope.error}
              helperText={errors.scope.text}
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
                  error={errors.startDate.error}
                  helperText={errors.startDate.text}
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
                  error={errors.endDate.error}
                  helperText={errors.endDate.text}
                />
              )}
            />
          </LocalizationProvider>
        </Stack>
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
