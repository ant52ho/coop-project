import React from "react";
import { PlotLine } from "./PlotLine";
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
  console.log(cmd);
  return (
    <div>
      {cmd.graphs.map((graph, i) => (
        <div key={i}>
          {graph === "Line" ? (
            <div>
              This is a line
              {cmd.sensors.map((sensor, i) => (
                <div key={i}>
                  {sensor}
                  <PlotLine graph={graph} sensor={sensor} cmd={cmd} />
                </div>
              ))}
            </div>
          ) : null}
          {graph === "Graph 1" ? <div>This is Graph 1</div> : null}
          {graph === "Graph 2" ? <div>This is not Graph 2</div> : null}
        </div>
      ))}
    </div>
  );
};
