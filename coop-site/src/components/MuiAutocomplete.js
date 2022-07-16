import { Stack, Autocomplete, TextField } from "@mui/material";
import { useState } from "react";

const skills = ["HTML", "CSS", "JavaScript", "Typescript", "React"];
const skillsOptions = skills.map((skill, index) => ({
  id: index + 1,
  label: skill,
}));

export const MuiAutocomplete = () => {
  const [value, setValue] = useState(null);
  const [skill, setSkill] = useState(null);
  console.log(value, skill);
  return (
    <Stack spacing={2} width="250px" sx={{ pt: 2 }}>
      <Autocomplete
        options={skills}
        renderInput={(params) => <TextField {...params} label="Skills" />}
        value={value}
        onChange={(event, newValue) => setValue(newValue)}
        freeSolo={false}
      />
      <Autocomplete
        options={skillsOptions}
        renderInput={(params) => <TextField {...params} label="Skills" />}
        value={skill}
        onChange={(event, newValue) => setSkill(newValue)}
        freeSolo={false}
      />
    </Stack>
  );
};
