import { Link, Outlet } from "react-router-dom";
import {
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from "@mui/material";

import ListIcon from "@mui/icons-material/List";
import TimelineIcon from "@mui/icons-material/Timeline";
import TextFormatIcon from "@mui/icons-material/TextFormat";
import QuestionMarkIcon from "@mui/icons-material/QuestionMark";

export const SidebarOptions = () => {
  return (
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
  );
};
