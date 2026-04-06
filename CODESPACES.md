# Development environment: GitHub Codespaces

Use **GitHub Codespaces** to edit, install **Python + Google ADK + FastAPI** dependencies, and run CLI tools **in the cloud**. Your laptop only needs a browser (or the GitHub/Codespaces client); nothing heavy is required locally.

Deploying to **Google Cloud Run** after you push is covered in [CLOUD_DEPLOY.md](CLOUD_DEPLOY.md).

---

## First time: open a Codespace

1. Open the repo on **GitHub**.
2. Click **Code** → **Codespaces** → **Create codespace on `main`** (or your working branch).
3. Wait for the container to build. The config lives in **`.devcontainer/devcontainer.json`**.

---

## What the dev container does

| Setting | Purpose |
|---------|---------|
| **Base image** | `mcr.microsoft.com/devcontainers/python:3.12` |
| **`PYTHONPATH`** | `${containerWorkspaceFolder}/src` so `import energy_task_manager` works |
| **`postCreateCommand`** | `pip3 install --user -r requirements.txt` after the workspace mounts |
| **Forwarded ports** | **8080** (FastAPI / uvicorn), **8000** (optional `adk web`) — VS Code will prompt to open in browser |

If `postCreateCommand` fails (e.g. network), run manually in the terminal:

```bash
pip3 install --user -r requirements.txt
```

---

## Secrets and environment variables

1. Copy **`/.env.example`** → **`.env`** in the repo root (file is gitignored).
2. Fill values such as **`GOOGLE_API_KEY`** for Gemini / ADK (see Google AI Studio).
3. For team or CI-style secrets, use **GitHub → Settings → Secrets and variables → Codespaces** and map names your app reads from the environment.

Never commit **`.env`** or API keys.

---

## Run the API locally in the Codespace

From the repository root:

```bash
export PYTHONPATH="${PWD}/src"
uvicorn energy_task_manager.main:app --host 0.0.0.0 --port 8080
```

Open the **“Ports”** tab, forward **8080**, and visit the forwarded URL (e.g. **`/health`**).

---

## Run ADK (`adk run`, `adk web`)

ADK runs in the same Linux environment as any other machine. Use the integrated terminal.

- **`adk run`** / **`adk web`**: follow the [ADK Python quickstart](https://google.github.io/adk-docs/get-started/python/) for the **directory layout** ADK expects (you may point it at a folder under `src/` or adjust as your project grows).
- For **`adk web`**, use port **8000** (already listed for forwarding in the devcontainer) or add another port in **`.devcontainer/devcontainer.json`** if needed.

---

## Optional: virtualenv instead of `pip install --user`

If you prefer a project **`.venv`**:

```bash
bash scripts/bootstrap-venv.sh
source .venv/bin/activate
```

Then run `uvicorn` / `adk` with that environment active.

---

## Git workflow: same repo as production

```bash
git status
git add -A
git commit -m "Describe change"
git push origin main
```

After you connect **Cloud Build** to this repo ([CLOUD_DEPLOY.md](CLOUD_DEPLOY.md)), a push to the configured branch can **build the Docker image and deploy Cloud Run** automatically.

---

## Persistence: you do not re-clone every session

- **Stopping** a Codespace keeps the disk; next time you open it, your clone, **`.venv`** (if you created one), and uncommitted files are still there.
- **Deleting** the Codespace removes that environment; anything not **pushed** to GitHub can be lost.
- **Habit:** `git push` when you finish a chunk of work.

---

## Troubleshooting

| Issue | What to try |
|--------|-------------|
| `ModuleNotFoundError: energy_task_manager` | `export PYTHONPATH="${PWD}/src"` or reopen the Codespace so devcontainer env applies. |
| `pip` / `adk` not found | Run `pip3 install --user -r requirements.txt` again; or activate `.venv` if you use the bootstrap script. |
| Port not reachable | **Ports** panel → set visibility to **Public** if you need a shareable URL (be careful with secrets). |

---

## Summary

| Step | Where |
|------|--------|
| Edit code, run ADK / FastAPI | **Codespaces** (browser or VS Code) |
| Dependencies | Installed **in the container** (not on your laptop) |
| Source of truth | **GitHub** (`git push`) |
| Deploy | **Cloud Build → Cloud Run** — [CLOUD_DEPLOY.md](CLOUD_DEPLOY.md) |
