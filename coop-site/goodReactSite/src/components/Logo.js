import { Box, Stack, Typography, IconButton } from "@mui/material";
import TrainIcon from "@mui/icons-material/Train";

export const Logo = () => {
  return (
    <Box sx={{ width: "100%" }} bgcolor="primary" py={4}>
      <Stack spacing={2} alignItems="center" p={2}>
        <IconButton edge="start" color="inherit" aria-label="logo">
          <TrainIcon color="primary" sx={{ fontSize: 75 }} />
        </IconButton>

        <Typography variant="h3">TEXT</Typography>
      </Stack>
    </Box>
  );
};
