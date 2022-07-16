import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import ListItemText from "@mui/material/ListItemText";
import Select from "@mui/material/Select";
import Checkbox from "@mui/material/Checkbox";
import { useState } from "react";
import { OutlinedInput, InputLabel } from "@mui/material";

const options = [
  "10.0.0.1",
  "10.0.0.2",
  "10.0.0.3",
  "10.0.0.4",
  "10.0.0.5",
  "10.0.0.6",
  "10.0.0.7",
  "10.0.0.8",
  "10.0.0.9",
  "10.0.0.10",
];

export const MultiSelect = (props) => {
  const options = props.options;
  const selected = props.value;
  const label = props.label;

  return (
    <div>
      <FormControl sx={{ width: 200 }}>
        <InputLabel id={label + "labelID"}>{label}</InputLabel>
        <Select
          labelId="{label + 'labelID'}"
          input={<OutlinedInput label={label} />}
          multiple
          value={selected}
          onChange={props.handleChange}
          renderValue={(selected) => selected.join(", ")}
        >
          <MenuItem value="all" dense>
            <Checkbox
              checked={options.length > 0 && selected.length === options.length}
              indeterminate={
                selected.length > 0 && selected.length < options.length
              }
            />

            <ListItemText primary="Select All" />
          </MenuItem>
          {options.map((option) => (
            <MenuItem key={option} value={option} dense>
              <Checkbox checked={selected.indexOf(option) > -1} />
              <ListItemText primary={option} />
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </div>
  );
};
