//import logo from './logo.svg';
import "./App.css";
import * as React from "react";
import { useState } from "react";
//import Button from "@mui/material/Button";
import { MuiTypography } from "./components/MuiTypography";
//import { MuiButton } from "./components/MuiButton";
//import { MuiTextField } from "./components/MuiTextField";
//import { MuiSelect } from "./components/MuiSelect";
import { MuiTable } from "./components/MuiTable";
//import { MuiAutocomplete } from "./components/MuiAutocomplete";
import { MuiDrawer } from "./components/MuiDrawer";
import { MuiNavbar } from "./components/MuiNavbar";
import { SearchAppBar } from "./components/SearchAppBar";
// import { MuiDrawerDemo } from "./components/MuiDrawerDemo";
import { MuiAvatar } from "./components/MuiAvatar";
import { SampleNavbar } from "./components/SampleNavbar";

import { Typography } from "@mui/material";

function App(props) {
  return (
    <div className="App">
      {/* <MuiTypography/> */}
      {/*<MuiButton />*/}
      {/*<MuiTextField /> */}
      {/*<MuiSelect />*/}
      {/* <MuiTable /> */}
      {/*<MuiAutocomplete />*/}
      {/* <MuiNavbar /> */}
      {/* <MuiAvatar /> */}
      {/* <SearchAppBar /> */}
      <MuiDrawer>{props.children}</MuiDrawer>
      {/* <MuiDrawerDemo /> */}
    </div>
  );
}

export default App;
