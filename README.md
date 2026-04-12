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

The project takes advantage of [GNU Make](https://www.gnu.org/software/make/), but using `make` is optional.
Build details are available in the project's [`Makefile`](./Makefile).

### Building
There is a `docker-compose.yml` file that will bootstrap a database as well as the application itself.
Build the project by running `docker compose build`.

Alternatively, run `make build` if Make tools are installed on the system.

#### When to Rebuild
If new Python-level dependencies/libraries are installed (e.g., into [`requirements.txt`](requirements.txt)),
then the container will need to be rebuilt.  Simply issue your preferred build command again.

Keep in mind that requirements may change as a result of a merged PR or on a remote branch, etc. Review the code that is being pulled to determine this, or just rebuild for good measure.

### Running
Similar to building, run `docker compose up` or `make run`.  The application will now be available at http://localhost:8000/.
The database will be accessible at `localhost:5432` using the credentials specified in `docker-compose.yml`.

### Cleaning Up
The Docker definitions create isolated networks and volume stores.  To reset everything completely, 

### Testing
#### Unit
The unit test suite can be run inside the container (meaning Python does not need to be installed locally) by
executing `make test-unit`.  If Make is not installed, the local environment will need to have the correct version
of Python installed, as well as all dependencies, etc.

For more verbose output, use `make test-unit-v`.

See the [`Makefile`](./Makefile) for more details.


