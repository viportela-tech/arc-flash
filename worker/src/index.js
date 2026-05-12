const http = require("node:http");

const port = Number(process.env.WORKER_PORT || 4000);

if (process.argv.includes("--check")) {
  console.log("worker check ok");
  process.exit(0);
}

const server = http.createServer((request, response) => {
  if (request.url === "/health") {
    response.writeHead(200, { "content-type": "application/json" });
    response.end(JSON.stringify({ status: "ok", service: "arcflash-worker" }));
    return;
  }

  response.writeHead(404, { "content-type": "application/json" });
  response.end(JSON.stringify({ error: "not_found" }));
});

server.listen(port, "0.0.0.0", () => {
  console.log(`arcflash-worker listening on ${port}`);
});
