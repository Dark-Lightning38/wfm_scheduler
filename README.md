# WFM Scheduler

Streamlit app that solves daily/weekly shift assignment for workforce on top of PuLP/CBC. Designed for ~8 internal users.

## Architecture at a glance

```
app.py                    # entry point: auth gate + multipage router
├── core/                 # pure-Python engine (no Streamlit imports)
│   ├── models.py         # Agent, Shift, ScheduleResult dataclasses
│   ├── constraints.py    # one business rule per function
│   └── scheduler.py      # orchestrator + solver wrapper
├── utils/                # I/O, validation, auth, state, audit
├── components/           # shared UI: theme, header, sidebar
├── pages/                # 4 Streamlit pages
├── tests/                # pytest suite (engine is testable without Streamlit)
├── data/                 # runtime artefacts (gitignored)
└── assets/               # CSS
```

Key principle: **the engine doesn't know Streamlit exists**. You can `pytest tests/` without ever launching the UI.

## Quick start (local)

```bash
git clone https://github.com/<you>/wfm_scheduler.git
cd wfm_scheduler

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Set up secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Generate bcrypt hashes for each user, paste into secrets.toml:
python -c "import bcrypt; print(bcrypt.hashpw(b'mypassword', bcrypt.gensalt()).decode())"

# Generate a cookie_key (≥32 chars):
python -c "import secrets; print(secrets.token_urlsafe(48))"

streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Push to a **private** GitHub repo (the .gitignore blocks secrets).
2. Visit `share.streamlit.io`, sign in with GitHub, grant private-repo access.
3. New app → pick the repo → main file `app.py`.
4. Advanced settings → Secrets → paste your `secrets.toml` content. Save.
5. Deploy. After it boots, click ⋮ → Settings → Sharing → add the 8 emails.
6. Smoke test in an incognito window.

Note: a free Community Cloud workspace allows **one private app** at a time.

## For non-developers using the app

- **Run a schedule** → Scheduler page → upload `need.xlsx` → click ▶️ Run solver.
- **Add a colleague** → Agents page → fill the form → Add.
- **Something looks wrong** → Settings → Audit log → ping the admin.

## Tests

```bash
pytest -q
```

The engine tests do not import Streamlit — they exercise `core/` directly.

## Where to extend

- A new business rule → new function in `core/constraints.py`, one line in `core/scheduler.py`.
- A new page → new file in `pages/`.
- A new I/O format → new function in `utils/data_loader.py`.

Cleanly extending without touching unrelated code is the whole point of the modular split.
