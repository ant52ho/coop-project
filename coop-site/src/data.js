const redis = require("redis");

async function hello() {
  const client = redis.createClient({
    socket: {
      host: "127.0.0.1",
      port: "7000", // The address of the replica
    },
    // password: '<password>' // not included for now
  });
  await client.connect();

  try {
    await client.set("key", "value");
    // insert body here

    var value = await client.get("key");

    console.log(value);
    value = await client.ts.range("sensor2:rain", "-", "+", "+");
    console.log(value);
  } catch (e) {
    console.error(e);
  }

  await client.quit();
}

hello();
