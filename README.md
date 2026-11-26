# CHEMVERSE – Interactive Chemistry Learning Platform

A full-stack chemistry learning website built with **Python 3.10+, Django 5, SQLite3, HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js and JSON APIs** using Django's MVT architecture. It is organised into **15 Django apps**.

---

## 1. Quick start

```bash
# 1. go into the project folder
cd CHEMVERSE

# 2. (recommended) create a virtual environment
python -m venv venv
# Windows:      venv\Scripts\activate
# macOS/Linux:  source venv/bin/activate

# 3. install Django
pip install -r requirements.txt

# 4. create the SQLite database (database/db.sqlite3)
python manage.py migrate

# 5. load the sample data + demo accounts
python manage.py seed_data

# 6. (optional) create your own admin account for /admin/
python manage.py createsuperuser

# 7. run
python manage.py runserver
```

Open **http://127.0.0.1:8000/**

Shortcut: `setup.bat` (Windows) or `./setup.sh` (macOS/Linux) runs steps 3–5 for you.

### Sample login credentials (created by `seed_data`)

| User ID | Email | Password | Notes |
|---|---|---|---|
| `demo` | demo@chemverse.local | `ChemDemo@2026` | Verified email, sample quiz/game history, saved structures, favourites, community posts |
| `learner` | learner@chemverse.local | `Learner@2026` | Second verified account (for leaderboard and community) |

You can sign in with either the **User ID or the email**. Use `python manage.py seed_data --no-demo` to load only the reference data, without demo users.

---

## 2. Guest mode – no sign-in needed

Every tool works without an account: lessons, periodic table, compound search, boiling & melting points, Structure Lab (draw + PNG export), Reaction Builder (check & explain), balancer, games, quizzes, molecular weight, lab simulator, dictionary and reading the community.

Guests get a **guest dashboard** (`/dashboard/`) showing quiz scores, game points, completed lessons, experiments and recently used tools **for the current browser visit** (stored in the session).

A free account adds: permanent progress and XP, leaderboard entries, achievements, saving molecules/reactions/favourite compounds/comparisons, adding compounds, and posting in the community.

## 3. Email (verification & password reset)

* **No setup needed for local testing.** Emails (verification links, password-reset links) are printed in the terminal where `runserver` runs. Copy the link into your browser.
* **Real email (e.g. Gmail):** create a Google *App Password* (Google Account → Security → 2-Step Verification → App passwords), then set these before `runserver`:

```bash
# Windows PowerShell
$env:EMAIL_HOST_USER="you@gmail.com"; $env:EMAIL_HOST_PASSWORD="your app password"
# macOS / Linux
export EMAIL_HOST_USER=you@gmail.com EMAIL_HOST_PASSWORD="your app password"
```

New accounts can use the site immediately; a verified email is required to post or reply in the Community. Unverified users see a banner with a **Resend link** button.

---

## 4. The 15 apps

| # | App | What it does | URL |
|---|---|---|---|
| 1 | `accounts` | Register (unique User ID + email + password), login with User ID **or** email, logout, email verification, forgot/reset password, change password, profile, learning history, saved items | `/accounts/` |
| 2 | `dashboard` | Landing page, personal dashboard (Chart.js charts, progress, recent tools, searches, achievements), About, Contact, activity tracking middleware, `seed_data` command | `/`, `/dashboard/` |
| 3 | `chemistry_learning` | 12 lessons in 9 topics, search, progress tracking (+25 XP) | `/learn/` |
| 4 | `periodic_table` | All 118 elements, colour-coded categories, search/filter, element detail (mass, group, period, block, electron configuration, Bohr model), JSON API | `/periodic-table/` |
| 5 | `compound_search` | Search 50 compounds by name or formula, molecular weight, melting/boiling points, chemical properties, safety summary, favourites, autocomplete, add your own | `/compounds/` |
| 6 | `boiling_melting` | Filter by temperature ranges, state at any temperature, liquid range, compare up to 8 compounds on a Chart.js chart, save comparisons | `/boiling-melting/` |
| 7 | `molecular_structure` | Canvas 2D editor: C, H, O, N, S, P, halogens…, single/double/triple bonds, move, erase, undo, templates, fill hydrogens, valence warnings, save to account, PNG export, gallery | `/structure-lab/` |
| 8 | `reaction_builder` | Enter your own reactants/products, live balance check, auto-balancing help, reaction-type detection, conservation-of-mass table, 14 safe sample reactions | `/reactions/` |
| 9 | `reaction_balancer` | Balances any equation with a step-by-step explanation (atom counts → equations per element → solve → clear fractions → verify) | `/balancer/` |
| 10 | `chemistry_games` | 7 games: Guess the Element, Periodic Table Challenge, Formula Matching, Molecular Weight Challenge, Memory, Boiling Point Challenge, Timed Quiz | `/games/` |
| 11 | `chemistry_quiz` | 40 MCQs, topic + difficulty (easy/medium/hard), timer, review with explanations, leaderboards (quiz / games / XP) | `/quiz/` |
| 12 | `molecular_weight` | Molar mass, % composition (doughnut chart), grams ↔ moles, particles, brackets and hydrates | `/molecular-weight/` |
| 13 | `lab_simulator` | 5 safe virtual experiments: titration (pH curve), flame tests, pH indicators, gas laws (PV = nRT), heating curve of water; results saved to a lab notebook | `/lab/` |
| 14 | `chemistry_dictionary` | 65 terms, search, A–Z, categories, examples | `/dictionary/` |
| 15 | `community` | Forum posts (question / discussion / shared reaction / resource), replies, likes, edit/delete own posts | `/community/` |

---

## 5. Folder structure

```
CHEMVERSE/
├── manage.py, requirements.txt, README.md, setup.bat, setup.sh
├── config/              settings.py, urls.py, wsgi.py, asgi.py,
│                        chem.py (chemistry engine), bootstrap.py, http.py
├── <15 apps>/           models.py, views.py, urls.py, admin.py, forms.py,
│                        migrations/0001_initial.py, templates/<app>/
├── templates/           base.html, includes/, errors/
├── static/css/          chemverse.css
├── static/js/           chemverse.js, periodic.js, structure.js, games.js, lab.js
├── static/images/
├── media/
└── database/            db.sqlite3 (created by migrate) + seed/*.json
```

## 6. JSON APIs

| Endpoint | Purpose |
|---|---|
| `GET /periodic-table/api/elements/` · `/periodic-table/api/elements/Fe/` | Element data |
| `GET /compounds/api/search/?q=ethanol` | Compound search |
| `GET /boiling-melting/api/data/` | Melting/boiling data |
| `GET /molecular-weight/api/?formula=Ca(OH)2` | Molar mass + composition |
| `GET /balancer/api/?equation=H2+%2B+O2+->+H2O` | Balanced equation + steps |
| `GET /reactions/api/check/?reactants=2H2+%2B+O2&products=2H2O` | Reaction check |
| `GET /quiz/api/questions/?n=20` | Random questions (used by the Timed Quiz game) |
| `GET /dictionary/api/search/?q=acid` | Dictionary search |
| `POST /structure-lab/save/` | Save a structure (account needed) |
| `POST /games/api/submit/` · `/lab/<slug>/record/` | Save a score / experiment result – to the account, or to the visit for guests (CSRF protected) |

## 7. About the data

* Melting and boiling points are reference values in °C at 1 atm.
* Substances that **decompose or sublime** have no invented value – the field shows *n/a* with a note (e.g. CO₂ “sublimes at −78.5 °C”).
* Values that vary between sources are labelled **Approximate**; values entered by users are labelled **User submitted**.
* Element masses in **[brackets]** are mass numbers of the most stable isotope; melting/boiling points not in the dataset show *Not available*.
* Molecular weights are calculated from the formula using standard atomic weights.
* Safety notes are short summaries – always read the official Safety Data Sheet.

## 8. Security

Django password hashing (PBKDF2) and password validators, CSRF protection on every form and on JSON POST requests, signed time-limited email-verification tokens, Django's password-reset tokens, login required for anything that saves data, users can only edit/delete their own content, and secure cookies when `DJANGO_DEBUG=0`. SQLite is set with a 20-second lock timeout so several users can use the site at once during development.

For production: set `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY` and `DJANGO_ALLOWED_HOSTS`, run `python manage.py collectstatic`, and serve with a WSGI server such as gunicorn or waitress.

## 9. Troubleshooting

* **“No such table”** → run `python manage.py migrate`.
* **Empty pages / no elements** → run `python manage.py seed_data`.
* **Models changed?** → `python manage.py makemigrations` then `python manage.py migrate`.
* **Did not get the verification email?** → look in the runserver terminal, or click *Resend link*.

---

## Deployment (Render)

The repo includes a Render Blueprint (`render.yaml`) that creates a web service and a free PostgreSQL database.

1. Push this repo to GitHub.
2. On https://dashboard.render.com choose **New → Blueprint**, connect the GitHub repo and click **Apply**.
3. Render runs `build.sh` (install → `collectstatic` → `migrate` → `seed_data`) and starts `gunicorn config.wsgi:application`.
4. Create an admin account from the service's **Shell** tab: `python manage.py createsuperuser`.

Environment variables used in production:

| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | Secret key (generated by the Blueprint) |
| `DJANGO_DEBUG` | `0` in production |
| `DATABASE_URL` | PostgreSQL connection string (linked by the Blueprint); SQLite is used when unset |
| `DJANGO_ALLOWED_HOSTS` / `DJANGO_CSRF_TRUSTED_ORIGINS` | Extra hosts / origins, e.g. for a custom domain (`https://chemverse.example.com`) |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | Optional SMTP login for real verification / reset emails |
