var value = [
  "sensor10:status",
  "sensor1:status",
  "sensor9:status",
  "sensor8:status",
  "sensor3:status",
  "sensor6:status",
  "sensor4:status",
  "sensor7:status",
  "sensor5:status",
  "sensor2:status",
];

value.sort(
  (a, b) =>
    parseInt(a.split(":")[0].slice(6, a.split(":")[0].length)) -
    parseInt(b.split(":")[0].slice(6, b.split(":")[0].length))
);
console.log(value);
