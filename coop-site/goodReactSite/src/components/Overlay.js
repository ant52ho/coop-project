import {
  Stack,
  AppBar,
  Box,
  CssBaseline,
  IconButton,
  Toolbar,
} from "@mui/material";
import { useState } from "react";
import MenuIcon from "@mui/icons-material/Menu";
import { Nav } from "./Nav";
import { SideDrawer } from "./SideDrawer";

const drawerWidth = 240;

export const Overlay = (props) => {
  const { window } = props;
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

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

          <Nav logout={props.logout} />
        </Toolbar>
      </AppBar>
      <SideDrawer
        drawerWidth={drawerWidth}
        container={container}
        mobileOpen={mobileOpen}
        handleDrawerToggle={handleDrawerToggle}
      />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${drawerWidth}px)` },
        }}
      >
        <Toolbar />
        {/* All content goes here */}
        <Stack my={3.5}>{props.children}</Stack>
      </Box>
    </Box>
  );
};
