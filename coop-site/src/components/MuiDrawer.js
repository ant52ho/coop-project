import * as React from "react";
// import PropTypes from "prop-types";
import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import CssBaseline from "@mui/material/CssBaseline";
import Divider from "@mui/material/Divider";
import Drawer from "@mui/material/Drawer";
import IconButton from "@mui/material/IconButton";
import InboxIcon from "@mui/icons-material/MoveToInbox";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import MailIcon from "@mui/icons-material/Mail";
import MenuIcon from "@mui/icons-material/Menu";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import TrainIcon from "@mui/icons-material/Train";
import { Stack, Menu, MenuItem, Button } from "@mui/material";
import { useState } from "react";
import PersonOutlinedIcon from "@mui/icons-material/PersonOutlined";
import { blue } from "@mui/material/colors";
import { Link, Outlet } from "react-router-dom";
import ListIcon from "@mui/icons-material/List";
import TimelineIcon from "@mui/icons-material/Timeline";
import TextFormatIcon from "@mui/icons-material/TextFormat";
import QuestionMarkIcon from "@mui/icons-material/QuestionMark";

const drawerWidth = 240;

export const MuiDrawer = (props) => {
  const { window } = props;
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  const drawer = (
    <div>
      {/* <Toolbar /> */}
      {/* <Divider /> */}
      <Box sx={{ width: "100%" }} bgcolor="primary" py={4}>
        <Stack spacing={2} alignItems="center" p={2}>
          <IconButton edge="start" color="inherit" aria-label="logo">
            <TrainIcon color="primary" sx={{ fontSize: 75 }} />
          </IconButton>

          <Typography variant="h3">TEXT</Typography>
        </Stack>
      </Box>
      <Divider />

      <List>
        <ListItem key={"Status"} disablePadding>
          <ListItemButton component={Link} to={"/status"}>
            <ListItemIcon>
              <ListIcon />
            </ListItemIcon>
            <ListItemText primary={"Status"} />
          </ListItemButton>
        </ListItem>

        <ListItem key={"Data"} disablePadding>
          <ListItemButton component={Link} to={"/data"}>
            <ListItemIcon>
              <TimelineIcon />
            </ListItemIcon>
            <ListItemText primary={"Data"} />
          </ListItemButton>
        </ListItem>

        <ListItem key={"Text"} disablePadding>
          <ListItemButton component={Link} to={"/text"}>
            <ListItemIcon>
              <TextFormatIcon />
            </ListItemIcon>
            <ListItemText primary={"Text"} />
          </ListItemButton>
        </ListItem>
        <ListItem key={"Test"} disablePadding>
          <ListItemButton component={Link} to={"/test"}>
            <ListItemIcon>
              <QuestionMarkIcon />
            </ListItemIcon>
            <ListItemText primary={"Test"} />
          </ListItemButton>
        </ListItem>
      </List>
    </div>
  );

  const container =
    window !== undefined ? () => window().document.body : undefined;

  return (
    <Box sx={{ display: "flex" }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
        }}
        color="primary"
      >
        <Toolbar sx={{ backgroundColor: "secondary" }}>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: "none" } }}
          >
            <MenuIcon />
          </IconButton>
          <Stack direction="row" spacing={2} sx={{ flexGrow: 1 }}>
            <Stack direction="column" py={2} sx={{ flexGrow: 1 }}>
              <Typography variant="h6">Project Dashboard</Typography>
              <Typography variant="subtitle2">Sample Text</Typography>
            </Stack>

            <Button color="inherit" onClick={handleClick}>
              About
            </Button>
          </Stack>

          <IconButton
            id="basic-button"
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
            open={open}
            onClose={handleClose}
            MenuListProps={{
              "aria-labelledby": "basic-button",
            }}
          >
            <MenuItem onClick={handleClose}>Profile</MenuItem>
            <MenuItem onClick={handleClose}>My account</MenuItem>
            <MenuItem onClick={handleClose}>Logout</MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
        aria-label="mailbox folders"
      >
        {/* The implementation can be swapped with js to avoid SEO duplication of links. */}
        <Drawer
          container={container}
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { sm: "block", md: "none" },
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { sm: "none", md: "block" },
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              width: drawerWidth,
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${drawerWidth}px)` },
        }}
      >
        <Toolbar />

        <Stack my={3.5}>{props.children}</Stack>
      </Box>
    </Box>
  );
};
