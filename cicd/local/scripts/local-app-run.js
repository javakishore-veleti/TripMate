const { spawn, spawnSync } = require("child_process");
const fs = require("fs");
const http = require("http");
const path = require("path");

const repoRoot = path.resolve(__dirname, "../../..");
const portalDir = path.join(repoRoot, "portals", "your-next-travel-app");
const isWin = process.platform === "win32";
const venvDir = path.join(repoRoot, ".venv");
const binDir = path.join(venvDir, isWin ? "Scripts" : "bin");
const python = path.join(binDir, isWin ? "python.exe" : "python");
const apiHost = "127.0.0.1";
const apiPort = "8000";
const apiUrl = `http://${apiHost}:${apiPort}`;

const children = [];
let shuttingDown = false;

function runSync(command, args, options = {}) {
  const result = spawnSync(command, args, {
    stdio: "inherit",
    shell: isWin,
    cwd: options.cwd || repoRoot,
    env: options.env || process.env,
  });
  if (result.status !== 0) {
    process.exit(result.status ?? 1);
  }
}

function start(command, args, options = {}) {
  const child = spawn(command, args, {
    stdio: "inherit",
    shell: isWin,
    cwd: options.cwd || repoRoot,
    env: options.env || process.env,
  });
  children.push(child);
  child.on("exit", (code, signal) => {
    if (!shuttingDown && signal !== "SIGTERM") {
      shutdown(code ?? 1);
    }
  });
  return child;
}

function shutdown(code = 0) {
  if (shuttingDown) {
    return;
  }
  shuttingDown = true;
  for (const child of children) {
    if (!child.killed) {
      child.kill("SIGTERM");
    }
  }
  process.exit(code);
}

function venvEnv() {
  return {
    ...process.env,
    VIRTUAL_ENV: venvDir,
    PATH: `${binDir}${path.delimiter}${process.env.PATH || ""}`,
  };
}

function thisRepoVenvActive() {
  const current = process.env.VIRTUAL_ENV || "";
  return path.resolve(current) === path.resolve(venvDir);
}

function waitForHealth(timeoutMs = 90_000) {
  const started = Date.now();
  return new Promise((resolve, reject) => {
    const attempt = () => {
      const request = http.get(`${apiUrl}/health`, (response) => {
        response.resume();
        if (response.statusCode === 200) {
          resolve();
          return;
        }
        retry();
      });
      request.on("error", retry);
    };
    const retry = () => {
      if (Date.now() - started > timeoutMs) {
        reject(new Error(`API did not become ready at ${apiUrl}/health`));
        return;
      }
      setTimeout(attempt, 400);
    };
    attempt();
  });
}

process.on("SIGINT", () => shutdown(0));
process.on("SIGTERM", () => shutdown(0));

if (!fs.existsSync(path.join(portalDir, "package.json"))) {
  console.error("Missing portals/your-next-travel-app.");
  process.exit(1);
}

console.log("Your Next Travel local run");
if (thisRepoVenvActive()) {
  console.log("1. Python venv already active for this repo");
} else {
  console.log("1. Activating this repo's .venv (uv sync)");
}
runSync("uv", ["sync"]);

if (!fs.existsSync(python)) {
  console.error("uv sync finished but .venv Python was not found.");
  process.exit(1);
}

if (!fs.existsSync(path.join(portalDir, "node_modules"))) {
  console.log("2. Installing Angular portal packages");
  runSync("npm", ["install"], { cwd: portalDir });
}

console.log(`3. Starting FastAPI at ${apiUrl} (Alembic schema upgrade on startup)`);
start(python, ["app.py", "--host", apiHost, "--port", apiPort], { env: venvEnv() });

waitForHealth()
  .then(() => {
    console.log("4. Starting Angular portal at http://127.0.0.1:4200");
    start("npm", ["start"], { cwd: portalDir });
  })
  .catch((error) => {
    console.error(error.message);
    shutdown(1);
  });
