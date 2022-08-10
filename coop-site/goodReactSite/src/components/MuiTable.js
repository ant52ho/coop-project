import * as React from "react";
import { DataGrid } from "@mui/x-data-grid";
import { Link } from "react-router-dom";
import { Box, Stack, Button } from "@mui/material";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import { useState, useEffect } from "react";
import axios from "axios";

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

    const interval = setInterval(() => {
      getData();
    }, 10000);
    return () => clearInterval(interval);
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
