# Client Tracker

by Azaria Lee


---

## Project Description

My project is about tracking clients and the jobs done for them, specifically targeted towards builders  you can:

- Manage Clients
- Track jobs
- Toggle billed and paid boxes
- Secure login
- Real time feedback


---

## Project Links

- [GitHub repo for the project](https://github.com/waimea-aalee/300dtd-client-tracker-project)
- [Project Documentation](https://waimea-aalee.github.io/300dtd-client-tracker-project/)
- [Live web app](https://three00dtd-client-tracker-project.onrender.com/login)


---

## Project Files

- Program source code can be found in the [app](app/) folder
- Project documentation is in the [docs](docs/) folder, including:
   - [Project requirements](docs/0-requirements.md)
   - Development sprints:
      - [Sprint 1](docs/1-sprint-1-prototype.md) - Development of a prototype
      - [Sprint 2](docs/2-sprint-2-mvp.md) - Development of a minimum viable product (MVP)
      - [Sprint 3](docs/3-sprint-3-refinement.md) - Final refinements
   - [Final review](docs/4-review.md)
   - [Setup guide](docs/setup.md) - Project and hosting setup

---

## Project Details

This is a digital media and database project for **NCEA Level 3**, assessed against standards [91902](docs/as91902.pdf) and [91903](docs/as91903.pdf).

The project is a web app that uses [Flask](https://flask.palletsprojects.com) for the server back-end, connecting to a SQLite database. The final deployment of the app is on [Render](https://render.com/), with the database hosted at [Turso](https://turso.tech/).

The app uses [Jinja2](https://jinja.palletsprojects.com/templates/) templating for structuring pages and data, and [PicoCSS](https://picocss.com/) as the starting point for styling the web front-end.

The project demonstrates a number of **complex database techniques**:
- Structuring the data using multiple tables
- Creating queries which insert, update or delete to modify data
- Creating customised data displays from multiple tables (e.g. web pages)
- Dynamically linking data between the database and a front-end display
- Applying data access permissions as appropriate to the outcome

The project demonstrates a number of **complex digital media (web) techniques**:
- Using non-core functionality
- Applying industry standards or guidelines
- Using responsive design for use on multiple devices
- Using dynamic data handling and interactivity


