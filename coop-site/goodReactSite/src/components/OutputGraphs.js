import React from "react";
import { PlotLine } from "./PlotLine";
import { Stack, Divider } from "@mui/material";
// const cmd = {
//     graphs: graphs,
//     ips: ips,
//     sensors: sensors,
//     scope: scope,
//     startDate: startDate,
//     endDate: endDate,
// };

export const OutputGraphs = (props) => {
  const cmd = props.cmd;
  const toggle = props.toggle;
  return (
    <div>
      {cmd.graphs.map((graph, i) => (
        <div key={i}>
          {graph === "Line" ? (
            <Stack spacing={3}>
              {cmd.sensors.map((sensor, i) => (
                <div key={i}>
                  <PlotLine
                    graph={graph}
                    sensor={sensor}
                    cmd={cmd}
                    toggle={toggle}
                  />
                  <Divider />
                </div>
              ))}
            </Stack>
          ) : null}
          {graph === "Graph 1" ? <div>This is Graph 1</div> : null}
          {graph === "Graph 2" ? <div>This is not Graph 2</div> : null}
        </div>
      ))}
    </div>
  );
};
