// {(unixTime) => moment(unixTime).format('HH:mm Do')}

import moment from "moment";

const t1 = 1389602000;
const t2 = 1390602000;

console.log(moment(t1).format("HH:mm Do"));
console.log(moment(t2).format("HH:mm Do"));
