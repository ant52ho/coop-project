var value = [
  { id: 1, ip: "10.0.0.1", status: "up" },
  { id: 2, ip: "10.0.0.2", status: "up" },
  { id: 3, ip: "10.0.0.3", status: "up" },
  { id: 4, ip: "10.0.0.4", status: "up" },
  { id: 5, ip: "10.0.0.5", status: "up" },
  { id: 6, ip: "10.0.0.6", status: "down" },
  { id: 7, ip: "10.0.0.7", status: "up" },
  { id: 8, ip: "10.0.0.8", status: "up" },
  { id: 9, ip: "10.0.0.9", status: "down" },
  { id: 10, ip: "10.0.0.10", status: "down" },
  { id: 11, ip: "10.0.0.11", status: "down" },
  { id: 12, ip: "10.0.0.12", status: "up" },
];

var ipsList = [];
var sensorList = [];
for (var i = 0; i < value.length; i++) {
  ipsList.append(value[i].ip);
}
console.log(value);
