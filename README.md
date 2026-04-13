# Intersection Game

## Project Structure
This project uses a FastAPI (Python) backend bootstrapped from the [`./src/server.py`](./src/server.py) file.
The front-end is standard HTML/JS/CSS arranged into the [`./public/`](./public) directory. These static files
are served by FastAPI, as well.

The [`./src/lib/`](./src/lib) directory contains the application's "domain" logic.

## Local Development
### Dependencies
This project is containerized using Docker, so Docker needs to be running on the host machine.
Otherwise, Python will need to be manually installed and managed on the local.

This project takes advantage of [GNU Make](https://www.gnu.org/software/make/).
While using `make` and related tooling is optional, it is highly recommended.
The following sections assume that the `make` utility is available on the local system.
Target details are available in the project's [`Makefile`](./Makefile).

### Building
There is a [`docker-compose.yml`](./docker-compose.yml) file that will bootstrap the application and a local database.
Look for configuration details within said [`docker-compose.yml`](./docker-compose.yml) file while running the local version of this application.

Build the project by running `make build`.

#### When to Rebuild
If new Python-level dependencies/libraries are installed (e.g., into [`requirements.txt`](requirements.txt)),
then the container will need to be rebuilt.  Simply issue the build command again.

Keep in mind that requirements may change as a result of a merged PR or on a remote branch, etc. Review the code that is being pulled to determine this, or just rebuild for good measure.

### Running
Similar to building, invoke the `make run` command to start the application.  Once started, the application will be available at http://localhost:8000/.
The database will be accessible at `localhost:5432` using the credentials specified in `docker-compose.yml`.
From _within_ the application containers, the database is available at `db:5432`.

### Cleaning Up
The Docker definitions create isolated networks and volume stores.  To reset everything completely, run `make clean`.
Note that this will completely wipe out the local database, requiring a reseed on the next startup.  It is often desirable
to start completely fresh - so use `make clean` to get there.

### Testing
#### Unit
The unit test suite can be run inside the container (meaning Python does not need to be installed locally) by
executing `make test-unit`.  If Make is not installed, the local environment will need to have the correct version
of Python installed, as well as all dependencies, etc.

For more verbose output, use `make test-unit-v`.

See the [`Makefile`](./Makefile) for more details.

## Summary of Commands
From the project root:
```shell
# Build the project
make build

# Run locally (using Docker)
make run

# Remove/Clean the application
make clean

# Run Unit Tests
make test-unit
```


