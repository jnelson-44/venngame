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

## Dictionary Management
The raw dictionary is stored in [`./src/data/dictionary.txt`](./src/data/dictionary.txt), but this project supports the
ability to import these words into the database for improved querying and performance.  The script file [`./src/scripts/dictionary.py`](./src/scripts/dictionary.py)
can be run to do this against any database using a standard `RFC-3986`-compliant URI of the form `dbtype://user:pass@host:port/dbname`.

Run `python -m src.scripts.dictionary --help` for more information about the script's usage.

### Importing to a Local or Remote Database
The `import` command will take a given `dictionary.txt` file and write it to the database. **Note** that this is destructive, so any
changes made directly in the database that do not exist in the dictionary file will be overwritten by this operation.

For example, to import the local dictionary file into a running version of the local database, run:
```shell
python -m src.scripts.dictionary import --dsn="postgres://root:passwordCity@localhost:5432/primary" ./src/data/dictionary.txt
```
The above would be the style of command to run against the production database whenever a change is made.

Run `python -m src.scripts.dictionary import --help` for more information about the import command's usage.

### Understanding Local Dictionary Fixturization
This application automatically applies all database schemas and seeds it with fixture data when starting fresh with Docker.
This is a process known as "seeding" the database. This ensures that the local code is always operating against a
correctly-defined local database.  The dictionary will be available in the database every time the application is brought up,
even when cleared (using `make clean`) and started anew.

To accomplish this, a "fixturization" file is necessary that is read every time Docker starts fresh - so this file must also
be updated once you are satisfied with the dictionary changes. Otherwise, this operation would have to be manually performed every
time the local application is cleaned and brought back up again.

For this reason, the convenience target `make dict-local-import` has been made that will both re-read the dictionary into the
local database, as well as update the local fixturization file so that all future runs of Docker will automatically use the latest change.

**This does not impact the state of the production database - the production database will always need to be explicitly updated,
as per best practices.**

### Summary: Updating the Dictionary
Combining the concepts from the above, a dictionary update workflow would look as follows:
1. Make the desired changes in [`dictionary.txt`](./src/data/dictionary.txt)
1. Apply them to the local database and fixture files by running `make dict-local-import`
1. Test the application to ensure you are pleased with the results
1. Apply them to the production database by running ```python -m src.scripts.dictionary import --dsn="PROD_DB_URI_HERE" ./src/data/dictionary.txt```
(making sure to paste in the production DB credentials)
1. Commit the changed [`dictionary.txt` file](./src/data/dictionary.txt) and the [dictionary fixture file](./container/db/primary/01-dictionary.sql) to Git

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

# Update local database with local dictionary
make dict-local-import
```
