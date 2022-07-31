const ips = ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4"];
const sensor = "Gas 1";
var scope = "60 months";

// console.log(date);

console.log("ips:" + ips.join());

// This function converts a string input into a time (seconds) input
function toSeconds(scope) {
  const date = (new Date().getTime() / 1000) | 0; // gets the current time in seconds
  scope = scope.split(" ");

  // cuts scope variable

  var unit = scope[1];
  var duration = scope[0];

  if (!unit) {
    unit = "Custom";
  } else if (unit[unit.length - 1] === "s") {
    unit = unit.slice(0, unit.length - 1);
  }

  var end;
  var start = date;

  if (unit === "minute") {
    end = start + duration * 60;
  } else if (unit === "hour") {
    end = start + duration * 60 * 60;
  } else if (unit === "day") {
    end = start + duration * 60 * 60 * 24;
  } else if (unit === "week") {
    end = start + duration * 60 * 60 * 24 * 7;
  } else if (unit === "month") {
    end = start + duration * 60 * 60 * 24 * 30;
  } else if (unit === "Custom") {
    start = 0;
    end = 1000;
  }

  return [start, end];
}

console.log("scope:", scope[0]);

scope = toSeconds(scope);
var retval = [
  "ips:" + ips.join(),
  "sensor:" + sensor,
  "scope:" + scope[0] + "," + scope[1],
].join("/");

console.log(retval);
