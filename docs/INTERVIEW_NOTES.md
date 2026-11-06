# Animal Rescue Explorer: architecture and interview notes

## What problem is being solved?
A user needs to filter animal records by type, breed, and outcome, then inspect distributions and recorded locations without writing database queries.

## What is actually implemented?
- `standalone_dashboard.py` serves a local HTML/CSS/JavaScript interface and a JSON endpoint using Python's standard library.
- Synthetic CSV data is bundled so the application starts without external services.
- `crud.py` provides validated MongoDB operations and reads `MONGO_URI` from the environment.
- The original course notebook remains as a historical implementation, dependent on its dataset and notebook packages.
- Automated tests exercise filters, HTTP endpoints, and the CRUD adapter with mocked database calls.

## Design decisions and tradeoffs
- **Standard-library HTTP instead of a framework:** Reduces install friction for a read-only demonstration. A framework would be more appropriate for authentication, large APIs, pagination, and production deployment.
- **Synthetic CSV instead of shipping course data:** Makes behavior reproducible without exposing historical records or course-only infrastructure.
- **Optional MongoDB:** Supports the original data-access design while keeping a working local demo.
- **Client-side charts:** Simple for small datasets; a large dataset should be aggregated or paginated on the server.
- **Read-only UI:** Prevents accidental data modifications. The underlying CRUD module deliberately requires non-empty filters for updates/deletes.

## Limitations
- The HTTP server is intended for localhost, not internet exposure.
- No authentication, authorization, external deployment, performance guarantees, or uptime monitoring.
- No automated browser tests. The HTTP and filtering tests do not prove visual usability.
- Database mode has no pagination and assumes the expected collection schema.
- Only a small, explicitly synthetic dataset is provided.

## Interview questions to prepare for
1. Why is a CSV useful as a fallback for a portfolio demonstration?
2. How do filtered MongoDB writes avoid accidental mass updates?
3. What happens if the database is unavailable?
4. How would you add pagination and indexes for a million documents?
5. What protections are required before deploying this publicly?
6. Which parts are automatically tested, and which are not?
