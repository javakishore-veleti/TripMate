const { spawn, spawnSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const isWin = process.platform === "win32";
const venvDir = path.resolve(".venv");
const binDir = path.join(venvDir, isWin ? "Scripts" : "bin");
const python = path.join(binDir, isWin ? "python.exe" : "python");

function run(command, args, options = {}) {
  const child = spawn(command, args, {
    stdio: "inherit",
    shell: false,
    ...options,
  });
  child.on("exit", (code, signal) => {
    if (signal) process.kill(process.pid, signal);
    process.exit(code ?? 1);
  });
  child.on("error", (err) => {
    console.error(err.message);
    process.exit(1);
  });
}

function ensureVenv() {
  const result = spawnSync("uv", ["sync"], {
    stdio: "inherit",
    shell: isWin,
  });
  if (result.status !== 0) {
    process.exit(result.status ?? 1);
  }
}

function shellQuote(value) {
  return `'${String(value).replace(/'/g, `'\\''`)}'`;
}

function writeActivateRc(activate) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "your-next-travel-venv-"));
  const rc = [
    `source ${shellQuote(activate)}`,
    `echo "Activated ${venvDir}"`,
    `echo "Python: ${shellQuote(python)}"`,
  ].join("\n");
  return { dir, rc };
}

function activateShell() {
  ensureVenv();

  if (isWin && !process.env.SHELL) {
    run("powershell.exe", [
      "-NoExit",
      "-ExecutionPolicy",
      "Bypass",
      "-File",
      path.join(binDir, "Activate.ps1"),
    ]);
    return;
  }

  const shell = process.env.SHELL || (isWin ? "bash" : "/bin/bash");
  const shellName = path.basename(shell);
  const activate = path.join(binDir, "activate");
  const { dir, rc } = writeActivateRc(activate);

  // Source the venv AFTER the user's interactive rc so PATH/PS1 are not overwritten.
  if (shellName === "zsh") {
    const home = process.env.HOME || os.homedir();
    fs.writeFileSync(
      path.join(dir, ".zshrc"),
      [
        `export ZDOTDIR=${shellQuote(home)}`,
        `[ -f ${shellQuote(path.join(home, ".zshrc"))} ] && source ${shellQuote(path.join(home, ".zshrc"))}`,
        rc,
        "",
      ].join("\n"),
    );
    run(shell, ["-i"], { env: { ...process.env, ZDOTDIR: dir } });
    return;
  }

  const bashRc = path.join(dir, "bashrc");
  const home = process.env.HOME || os.homedir();
  fs.writeFileSync(
    bashRc,
    [
      `[ -f ${shellQuote(path.join(home, ".bashrc"))} ] && source ${shellQuote(path.join(home, ".bashrc"))}`,
      rc,
      "",
    ].join("\n"),
  );
  run(shell, ["--rcfile", bashRc, "-i"]);
}

function runInVenv(command, args) {
  ensureVenv();

  const env = {
    ...process.env,
    VIRTUAL_ENV: venvDir,
    PATH: `${binDir}${path.delimiter}${process.env.PATH || ""}`,
  };

  const exe = isWin
    ? [path.join(binDir, `${command}.exe`), path.join(binDir, command)].find(
        (candidate) => fs.existsSync(candidate),
      )
    : path.join(binDir, command);

  run(exe && fs.existsSync(exe) ? exe : command, args, { env, shell: isWin });
}

const [command, ...args] = process.argv.slice(2);
if (!command) {
  activateShell();
} else {
  runInVenv(command, args);
}
