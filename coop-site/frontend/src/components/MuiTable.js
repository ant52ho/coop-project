import * as React from "react";
import { DataGrid } from "@mui/x-data-grid";
import { Link } from "react-router-dom";
import { Box, Stack, Button } from "@mui/material";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import { useState, useEffect } from "react";
import axios from "axios";

// make this query actual data
// const statusData = [
//   { id: 1, ip: "10.0.0.1", status: "up", data1: 35, data2: 12, data3: 12 },
//   { id: 2, ip: "10.0.0.2", status: "up", data1: 42, data2: 43, data3: 19 },
//   { id: 3, ip: "10.0.0.3", status: "up", data1: 45, data2: 65, data3: 8 },
//   { id: 4, ip: "10.0.0.4", status: "up", data1: 16, data2: 11, data3: 34 },
//   { id: 5, ip: "10.0.0.5", status: "up", data1: 12, data2: 65, data3: 87 },
//   { id: 6, ip: "10.0.0.6", status: "up", data1: 150, data2: 12, data3: 19 },
//   { id: 7, ip: "10.0.0.7", status: "up", data1: 44, data2: 64, data3: 93 },
//   { id: 8, ip: "10.0.0.8", status: "down", data1: 36, data2: 39, data3: 85 },
//   { id: 9, ip: "10.0.0.9", status: "up", data1: 65, data2: 45, data3: 16 },
//   { id: 10, ip: "10.0.0.10", status: "up", data1: 65, data2: 15, data3: 76 },
// ];

const statusColumns = [
  { field: "id", headerName: "ID", width: 100, type: "number" },
  { field: "ip", headerName: "IP", width: 100 },
  { field: "status", headerName: "Status", width: 100 },
  { field: "data1", headerName: "Data 1", width: 100 },
  { field: "data2", headerName: "Data 2", width: 100 },
  { field: "data3", headerName: "Data 3", width: 100 },
  {
    field: "View",
    headerName: "View",
    width: 100,
    renderCell: (params) => (
      <strong>
        <Link to={`/data`} key={params.row.key} state={{ id: params.row.id }}>
          <ArrowForwardIcon color="primary" fontSize="small" />
        </Link>
      </strong>
    ),
  },
];

export const MuiTable = () => {
  const [statusData, setStatusData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reloadToggle, setReloadToggle] = useState(false);

  const handleReload = () => {
    setReloadToggle(!reloadToggle);
    console.log("toggle:", reloadToggle);
  };

  useEffect(() => {
    const getData = async () => {
      try {
        const response = await axios.get("/status");
        setStatusData(response.data);
        console.log(response.data);
        setError(null);
      } catch (err) {
        setError(err.message);
        setStatusData([]);
      } finally {
        setLoading(false);
      }
    };
    getData();
  }, [reloadToggle]);

  return (
    <Box
      sx={{ display: "flex", justifyContent: "center", alignItem: "center" }}
    >
      <Stack py={2}>
        <Box>
          <Button variant="contained" size="large" onClick={handleReload}>
            Reload!
          </Button>
        </Box>
        <div style={{ width: "720px", maxHeight: "75vh" }}>
          <DataGrid
            rows={statusData}
            columns={statusColumns}
            pageSize={10}
            rowsPerPageOptions={[10]}
            // density="compact"
            autoHeight
            // checkboxSelection
          />
        </div>
      </Stack>
    </Box>
  );
};
