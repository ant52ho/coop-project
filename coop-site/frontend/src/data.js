const redis = require("redis");
const { TimeSeriesAggregationType } = require("@redis/time-series");

async function hello() {
  const client = redis.createClient({
    socket: {
      host: "127.0.0.1",
      port: "6379", // The address of the replica
    },
    // password: '<password>' // not included for now
  });
  await client.connect();

  try {
    await client.set("key", "value");
    // insert body here

    var value = await client.get("key");

    console.log(value);

    const count = 1000;
    // assume 30 days
    const frame = "30 days";
    const bucket = (60 * 60 * 24 * 30) / count;

    value = await client.ts.range("sensor2:rain", "-", "+", {
      COUNT: 1000,
      // Group into 1 second averages.
      AGGREGATION: {
        type: TimeSeriesAggregationType.AVERAGE,
        timeBucket: 1,
      },
    });

    console.log(value);
    console.log(value.length);
  } catch (e) {
    console.error(e);
  }

  await client.quit();
}

hello();
