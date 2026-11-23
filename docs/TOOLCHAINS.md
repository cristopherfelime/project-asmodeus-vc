# WSL2 Ubuntu Toolchain Setup Guide

This guide covers installing and verifying every toolchain checked by `asmodeus doctor` inside **WSL2 Ubuntu**.

Run `uv run asmodeus doctor` at any time to check what is currently discoverable on your `PATH` (as well as `~/.local/bin`, `~/.cargo/bin`, `/usr/local/go/bin`, and `~/.sdkman/candidates/*/current/bin`).

---

## 1. Prerequisites (`git`, `curl`, build essentials)

```bash
sudo apt-get update
sudo apt-get install -y git curl ca-certificates build-essential unzip zip
```

Verify:

```bash
git --version
```

---

## 2. Python 3.12 & `uv`

Install `uv` using the official Astral standalone installer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Ensure `~/.local/bin` is on your `PATH` (add to `~/.bashrc` or `~/.zshrc`):

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Install Python 3.12 via `uv` and verify:

```bash
uv python install 3.12
uv --version
python3 --version
```

---

## 3. Node.js & `npm` (for `ts-webui`)

### Option A: `nvm` (Recommended)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source "$HOME/.nvm/nvm.sh"
nvm install --lts
nvm use --lts
```

### Option B: NodeSource APT Repository (Ubuntu system-wide)

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
```

Verify:

```bash
node --version
npm --version
```

---

## 4. Rust (`rustup`, `rustc`, `cargo` — for `rust-service`)

Install the Rust toolchain via `rustup`:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
```

Verify:

```bash
rustc --version
cargo --version
```

---

## 5. Go (Official Tarball — for `go-service`)

Download and extract the official Linux `amd64` tarball into `/usr/local/go`:

```bash
GO_VERSION="1.23.4"
curl -LO "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz"
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf "go${GO_VERSION}.linux-amd64.tar.gz"
rm "go${GO_VERSION}.linux-amd64.tar.gz"
```

Add `/usr/local/go/bin` (and `$HOME/go/bin`) to `~/.bashrc` or `~/.zshrc`:

```bash
export PATH="/usr/local/go/bin:$HOME/go/bin:$PATH"
```

Verify:

```bash
go version
```

---

## 6. Java, Scala & `sbt` via SDKMAN! (for `scala-spark`)

Install SDKMAN!:

```bash
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"
```

Install Java 17 (Temurin LTS), Scala, and `sbt`:

```bash
sdk install java 17.0.13-tem
sdk install scala
sdk install sbt
```

Verify:

```bash
java -version
scala -version
sbt --version
```

---

## 7. Docker (for `compose` overlay)

### Option A: Docker Desktop for Windows (WSL2 Integration)

1. Install **Docker Desktop** on Windows with the **WSL 2 based engine** enabled.
2. Open **Settings → Resources → WSL Integration** and toggle **Ubuntu** on.
3. Restart your WSL2 shell if `docker` is not immediately available.

### Option B: Native Docker Engine inside WSL2 Ubuntu (systemd enabled)

Follow the official Docker Engine Ubuntu APT instructions if running without Docker Desktop, then add your user to the `docker` group:

```bash
sudo usermod -aG docker "$USER"
```

Verify:

```bash
docker --version
docker compose version
```

---

## 8. Final Verification

Inside `project-asmodeus-vc`:

```bash
uv run asmodeus doctor
```

Tools you plan to use for a specific flavor should show `[OK]`. Missing tools for unrelated flavors do not prevent running `asmodeus new` or the Python test suite.
