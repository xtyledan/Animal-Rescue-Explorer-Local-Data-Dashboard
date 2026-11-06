# Animal Rescue Explorer

**A runnable, read-only Python dashboard for exploring shelter records.** The local application starts with a bundled *synthetic* dataset, so a reviewer can try it without MongoDB, Jupyter, cloud accounts, or private course files.

[![Python tests](https://github.com/xtyledan/Animal-Rescue-Explorer-Local-Data-Dashboard/actions/workflows/python-tests.yml/badge.svg)](https://github.com/xtyledan/Animal-Rescue-Explorer-Local-Data-Dashboard/actions/workflows/python-tests.yml)

![Actual Animal Rescue Explorer in Chromium, displaying the synthetic sample dataset](docs/screenshot.png)

*Actual browser screenshot captured from the running application by [GitHub Actions](https://github.com/xtyledan/Animal-Rescue-Explorer-Local-Data-Dashboard/actions/workflows/capture-demo.yml). No hosted deployment is claimed.*

## Run the local dashboard

Requires Python 3.11 or newer. The synthetic-data version uses only the Python standard library.

```bash
git clone https://github.com/xtyledan/Animal-Rescue-Explorer-Local-Data-Dashboard.git
cd Grazioso-Salvare-Dashboard-and-Database-Integration
python standalone_dashboard.py
```

Open **http://127.0.0.1:8080/**. Use the controls to filter animals by type, breed, or outcome. The dashboard displays summary counts, a breed distribution, a table, and map links for recorded coordinates.

To choose another port: `python standalone_dashboard.py --port 8081`.

The sample dataset contains ten clearly labeled fictional animal records. It is for demonstration and testing, not operational shelter data.

## Run tests

The dashboard and filtering tests need no extra Python packages:

```bash
python -m unittest discover -s tests -p 'test_standalone_dashboard.py' -v
```

To run **all** tests, including the MongoDB CRUD wrapper, install PyMongo first:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

GitHub Actions checks the CRUD module, filtering behavior, and local HTTP endpoints. It does **not** conduct browser-based visual tests or verify a real MongoDB connection.

## Optional MongoDB mode

The separate `crud.py` class uses PyMongo. Configure **MONGO_URI** outside the repository. For PowerShell:

```powershell
$env:MONGO_URI = "mongodb://USER:PASSWORD@HOST:27017/?authSource=admin"
python standalone_dashboard.py
```

For macOS/Linux:

```bash
export MONGO_URI='mongodb://USER:PASSWORD@HOST:27017/?authSource=admin'
python standalone_dashboard.py
```

These values are placeholders. Never commit credentials. The connection expects a MongoDB database named `AAC` with a collection named `animals` and fields such as `animal_type`, `breed`, and `outcome_type`. MongoDB mode is not necessary to run the demo.

## Architecture

| File | Purpose |
| --- | --- |
| `standalone_dashboard.py` | Local HTTP server, JSON API, filters, and responsive frontend |
| `sample_animals.csv` | Ten synthetic animal records |
| `crud.py` | Configurable MongoDB CRUD operations with guarded update/delete filters |
| `tests/test_standalone_dashboard.py` | Dashboard HTTP and filter regression tests |
| `tests/test_crud.py` | Mocked MongoDB CRUD regression tests |
| `ProjectTwoDashboard.ipynb` | Original coursework notebook retained for reference |
| `docs/INTERVIEW_NOTES.md` | Technical decisions, limitations, and interview discussion topics |

**Why two data modes?** The synthetic CSV makes the application immediately runnable and reproducible. An optional database adapter demonstrates persistent document storage without making a public demo depend on external infrastructure.

**Limitations:** The included server is intended for localhost use, not internet exposure. It has no authentication, rate limiting, pagination, hosted deployment, or production monitoring. The original notebook depends on unavailable course assets and is not the recommended way to run the demo.

See [engineering notes](docs/INTERVIEW_NOTES.md) for tradeoffs and suggested next steps.

## License

[MIT License](LICENSE). The sample data is synthetic and for demonstration.
