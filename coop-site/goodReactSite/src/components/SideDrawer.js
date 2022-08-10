import React from "react";
import { Box, Drawer, Divider } from "@mui/material";

import { Logo } from "./Logo";
import { SidebarOptions } from "./SidebarOptions";

export const SideDrawer = (props) => {
  const drawer = (
    <div>
      <Logo />
      <Divider />
      <SidebarOptions />
    </div>
  );

  return (
    <Box
      component="nav"
      sx={{ width: { md: props.drawerWidth }, flexShrink: { md: 0 } }}
      aria-label="mailbox folders"
    >
      <Drawer
        container={props.container}
        variant="temporary"
        open={props.mobileOpen}
        onClose={props.handleDrawerToggle}
        ModalProps={{
          keepMounted: true,
        }}
        sx={{
          display: { sm: "block", md: "none" },
          "& .MuiDrawer-paper": {
            boxSizing: "border-box",
            width: props.drawerWidth,
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
            width: props.drawerWidth,
          },
        }}
        open
      >
        {drawer}
      </Drawer>
    </Box>
  );
};
