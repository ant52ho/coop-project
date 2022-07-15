// this file tests js code.

console.log("hello world");

// today's task will be to query data from redis

// below is a sample json object that may be queryed from redis
const statusData = [
  { id: 1, ip: "10.0.0.1", status: "up", data1: 35, data2: 12, data3: 12 },
  { id: 2, ip: "10.0.0.2", status: "up", data1: 42, data2: 43, data3: 19 },
  { id: 3, ip: "10.0.0.3", status: "up", data1: 45, data2: 65, data3: 8 },
  { id: 4, ip: "10.0.0.4", status: "up", data1: 16, data2: 11, data3: 34 },
  { id: 5, ip: "10.0.0.5", status: "up", data1: 12, data2: 65, data3: 87 },
  { id: 6, ip: "10.0.0.6", status: "up", data1: 150, data2: 12, data3: 19 },
  { id: 7, ip: "10.0.0.7", status: "up", data1: 44, data2: 64, data3: 93 },
  { id: 8, ip: "10.0.0.8", status: "down", data1: 36, data2: 39, data3: 85 },
  { id: 9, ip: "10.0.0.9", status: "up", data1: 65, data2: 45, data3: 16 },
  { id: 10, ip: "10.0.0.10", status: "up", data1: 65, data2: 15, data3: 76 },
];

// to get all the values of a json object
// console.log(Object.values(data[0]));

// gets node status
const getNodeStatus = new Promise((resolve, reject) => {
  if (false) {
    return setTimeout(() => reject(new Error("Users not found")), 250);
  }
  setTimeout(function () {
    resolve(data);
  }, 1500);
});

getNodeStatus.then((retval) => {
  console.log(retval);
});
