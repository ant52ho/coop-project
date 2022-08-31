import {
  Stack,
  Typography,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Box,
} from "@mui/material";
import { useState } from "react";

import PersonOutlinedIcon from "@mui/icons-material/PersonOutlined";
import { blue } from "@mui/material/colors";

export const Nav = (props) => {
  //   const open = Boolean(props.anchorEl);
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
    console.log(event.currentTarget.id);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <Box display={"flex"} width={"100%"}>
      <Stack direction="row" spacing={2} sx={{ flexGrow: 1 }}>
        <Stack direction="column" py={2} sx={{ flexGrow: 1 }}>
          <Typography variant="h6">Project Dashboard</Typography>
          <Typography variant="subtitle2">Sample Text</Typography>
        </Stack>

        <Button color="inherit" onClick={handleClick} id="about">
          About
        </Button>
      </Stack>

      <IconButton
        id="profile"
        aria-controls={open ? "basic-menu" : undefined}
        aria-haspopup="true"
        aria-expanded={open ? "true" : undefined}
        onClick={handleClick}
      >
        <PersonOutlinedIcon fontSize="large" sx={{ color: blue[50] }} />
      </IconButton>

      <Menu
        id="basic-menu"
        anchorEl={anchorEl}
        open={open && anchorEl.id === "profile"}
        onClose={handleClose}
        MenuListProps={{
          "aria-labelledby": "basic-button",
        }}
      >
        <MenuItem onClick={handleClose}>Profile</MenuItem>
        <MenuItem onClick={handleClose}>My account</MenuItem>
        <MenuItem onClick={props.logout}>Logout</MenuItem>
      </Menu>
    </Box>
  );
};
