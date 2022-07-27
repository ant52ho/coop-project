import React from "react";

// const cmd = {
//     graphs: graphs,
//     ips: ips,
//     sensors: sensors,
//     scope: scope,
//     startDate: startDate,
//     endDate: endDate,
// };

{
  /* <LineChart
          width={730}
          height={250}
          data={data}
          margin={{ top: 0, right: 0, left: 0, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="pv" stroke="#8884d8" />
          <Line type="monotone" dataKey="uv" stroke="#82ca9d" />
          <Line type="monotone" dataKey="amt" stroke="#82ca9d" />
        </LineChart>
      )}
    </Stack> */
}
export const PlotLine = (props) => {
  const cmd = props.cmd;
  const sensor = props.sensor;
  const ips = cmd.ips;
  const scope = cmd.scope;
  var startDate = cmd.startDate;
  var endDate = cmd.endDate;

  if (scope === "Custom") {
    startDate = startDate.unix();
    endDate = endDate.unix();
    console.log(startDate, endDate);
  }

  return (
    <div>
      {props.sensor}
      {props.cmd.ips}
      {props.cmd.scope}
    </div>
  );
};
