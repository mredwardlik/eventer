<div align="center">

# 🎟 Eventer

**A web app for creating and publishing your own events.**

Organizers create events with a rich-text editor in their personal cabinet.
Guests open the event page and sign up in one click.

[![tests](https://github.com/mredwardlik/eventer/actions/workflows/tests.yml/badge.svg)](https://github.com/mredwardlik/eventer/actions/workflows/tests.yml)
![React](https://img.shields.io/badge/React_18-20232A?style=flat-square&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Redux](https://img.shields.io/badge/Redux-764ABC?style=flat-square&logo=redux&logoColor=white)
![MUI](https://img.shields.io/badge/MUI_5-007FFF?style=flat-square&logo=mui&logoColor=white)
![Editor.js](https://img.shields.io/badge/Editor.js-000000?style=flat-square)
![Django](https://img.shields.io/badge/Django_5.2-092E20?style=flat-square&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-A30000?style=flat-square&logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

<img src="docs/screenshots/event.png" alt="Public event page" width="820" />

</div>

---

## ✨ Features

**For organizers**

- 🔐 Sign up and sign in with token authentication
- 📝 Create events with a name, start and end date, tags, city and cover image
- 🧱 Write rich descriptions in [Editor.js](https://editorjs.io/): headings,
  lists, tables, code, embeds, images and galleries
- 💾 Save your own description template as the editor's default
- 📊 See all your events in a table with registration and view counts
- 👥 See who signed up: name, email and contacts, visible only to you
- 🗑 Delete events (they are hidden, not erased)

**For guests**

- 🌄 Event page with a blurred cover, date, time, city and tags
- ✍️ Sign up for an event with name, email and contacts, no account needed
  (one email signs up once)
- 👁 Every page visit is counted

## 📸 Screenshots

| Sign in / Sign up | My events |
| :---: | :---: |
| <img src="docs/screenshots/auth.png" alt="Auth page" width="400" /> | <img src="docs/screenshots/cabinet-events.png" alt="Events table in cabinet" width="400" /> |
| **Create an event** | **Event page** |
| <img src="docs/screenshots/cabinet-create.png" alt="Event creation form" width="400" /> | <img src="docs/screenshots/event.png" alt="Public event page" width="400" /> |

## 🏗 Architecture

```mermaid
flowchart LR
    subgraph Client["frontend/ (React SPA, :3000)"]
        UI[Pages & MUI components] --> Store[Redux + thunks]
        Store --> Axios[Axios + Token header]
    end
    subgraph Server["backend/ (Django REST Framework, :8000)"]
        API["/api/v1/user/*<br/>/api/v1/event/*"] --> DB[(SQLite)]
        API --> Media["media/ (uploads)"]
    end
    Axios -- REST / JSON --> API
```

## 🚀 Getting started

### Requirements

- Python 3.10+
- Node.js 20+

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed           # optional: user "demo", password "eventer-demo", 3 events
python manage.py runserver      # → http://localhost:8000
```

Settings come from environment variables or `backend/.env`; nothing is needed
on a laptop. For a server copy [`backend/.env.example`](backend/.env.example):

| Variable               | Default                          | Meaning                               |
| ---------------------- | -------------------------------- | ------------------------------------- |
| `DJANGO_DEBUG`         | `1`                              | `0` on a server                       |
| `DJANGO_SECRET_KEY`    | a development key                | required when `DJANGO_DEBUG=0`        |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1`            | the domain of the API                 |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000`          | where the frontend is opened from     |

### Frontend

```bash
cd frontend
npm install --legacy-peer-deps
npm start                       # → http://localhost:3000
```

The frontend talks to `http://localhost:8000/api/v1/`. For a server, build it
with another address: `API_URL=https://api.example.com/api/v1/ npm run build`.

| Script              | Description                              |
| ------------------- | ---------------------------------------- |
| `npm start`         | Webpack dev server with hot reload       |
| `npm run build`     | Production build into `frontend/dist/`   |
| `npm test`          | Vitest: date formatting, notes, reducer  |
| `npm run typecheck` | TypeScript without building              |

## 🔌 REST API

Base URL: `/api/v1/`. Send authenticated requests with the header
`Authorization: Token <token>`.

<details>
<summary><b>User</b>: <code>/user/…</code></summary>

| Method | Endpoint                 | Description                                           |
| ------ | ------------------------ | ----------------------------------------------------- |
| `POST` | `/user/register`         | Sign up: `username`, `email`, `password`              |
| `POST` | `/user/login`            | Sign in. Returns `{ token }`                          |
| `POST` | `/user/logout`           | 🔒 Delete the token                                   |
| `GET`  | `/user/me`               | 🔒 The profile of the current user                    |
| `GET`  | `/user/editor`           | 🔒 Get the user's default editor template             |
| `POST` | `/user/editor`           | 🔒 Save the default editor template                   |

</details>

<details>
<summary><b>Event</b>: <code>/event/…</code></summary>

| Method   | Endpoint                 | Description                                                 |
| -------- | ------------------------ | ----------------------------------------------------------- |
| `GET`    | `/event/all`             | All active events, without the guest list                   |
| `GET`    | `/event/get?id=<uuid>`   | One event (adds one to its view count)                      |
| `GET`    | `/event/user`            | 🔒 Events of the current user, with the guests              |
| `POST`   | `/event/create`          | 🔒 Create an event (multipart, dates as Unix timestamps)    |
| `POST`   | `/event/image`           | 🔒 Upload an image for Editor.js                            |
| `PATCH`  | `/event/register/<id>`   | Sign up for an event: `name`, `email`, `contacts`           |
| `PATCH`  | `/event/like/<id>`       | 🔒 Like an event (not your own, once per user)              |
| `DELETE` | `/event/delete/<id>`     | 🔒 Hide your event                                          |
| `GET`    | `/event/special/cities`  | List of allowed cities                                      |
| `GET`    | `/event/special/tags`    | List of allowed tags                                        |

</details>

Allowed **cities** and **tags** are set in
[`backend/core/constant.py`](backend/core/constant.py), and the server checks
new events against them. 🔒 marks requests that need the token. View counts,
likes and guest lists are counted by the server and can't be sent by a client.

## 🧪 Tests

```bash
cd backend && python manage.py test     # the whole API: 21 tests
cd frontend && npm test
```

GitHub Actions runs the backend tests on Python 3.10–3.14 and type-checks,
tests and builds the frontend.

## 🗂 Project structure

```text
eventer/
├── backend/                 # Django project
│   ├── core/                # settings, root urls, constants (cities, tags)
│   ├── user/                # custom User model, auth & editor settings API
│   └── event/               # Event model, serializers, validators, API, seed command
├── frontend/                # React + TypeScript SPA (custom Webpack config)
│   └── src/
│       ├── pages/           # auth, cabinet (+ fragments), event, home, 404
│       ├── components/      # events table, notes, Editor.js wrappers, dialogs
│       ├── redux/           # user state, thunks
│       ├── services/        # Axios API clients
│       └── swal/            # SweetAlert2 dialogs
└── design/                  # Figma mockups & mind map
```

## 📄 License

[MIT](LICENSE) © Edward Lik
