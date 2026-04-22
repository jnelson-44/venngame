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

## Database Management
The table definitions for the database are stored in [`./container/db/primary/00-schema.sql`](./container/db/primary/00-schema.sql).
When a schema change is necessary, update that file with the latest definition(s) to ensure that the changes are picked up in the local
development environment.  Adding, changing, or deleting tables in the Production database will have to be done manually using `CREATE`,
`ALTER`, or `DROP` statements as needed in accordance with whatever strategy is appropriate for the live load.

*This application does not automatically apply schema changes to the Production database (nor should it).*

## CLI Tools
This project contains multiple CLI scripts that can be executed to assist in managing and evaluating the application.
These scripts are stored in the [`./src/scripts/`](./src/scripts) directory.

### Database Access
Several of these scripts require a database connection to perform their work. There are multiple ways to provide these to the scripts - the only
requirement is that the DSN strings used conform to the `RFC-3986` standard for database URIs, e.g. strings of the form `{dbtype}://{dbuser}:{dbpass}@{dbhost}:{dbport}/{dbname}`.

Use the `--help` switch for each script's subcommands to see if they require a DSN.  If they do, it may be provided using the
`--dsn` option, e.g., `--dsn="dbtype://user:pass@host:port/dbname"`.
As this can get quite cumbersome to provide repeatedly, it is also possible to set the environment variable `DATABASE_URL` and the script
will read from that instead.  To avoid collisions with any other applications, the `VENNGAME_DATABASE_URL` could also be used if desired.

For example, the following sets of commands each use the same script and connect to the same database, but use two different styles of specifying the DSN:
```shell
# Using --dsn flag
python -m src.scripts.puzzle get-region-hits --dsn="postgres://root:passwordCity@localhost:5432/primary" 2026-03-27

# Using environment variable
## Set it...
export VENNGAME_DATABASE_URL="postgres://root:passwordCity@localhost:5432/primary"
## Execute a command...
python -m src.scripts.puzzle get-region-hits 2026-03-27
## Execute another
python -m src.scripts.puzzle get-region-hits 2026-03-23
```
The latter is clearly much simpler, and the environment variable will remain set as long as the terminal session is active.
The environment variable can also be rewritten to the production database, another testing database, etc.  When using this approach, make sure to
`print $VENNGAME_DATABASE_URL` and/or `print $DATABASE_URL` to make sure you know which database is being used for the script's
execution.

### Puzzle Information CLI Tools
The [`./src/scripts/puzzle.py`](./src/scripts/puzzle.py) script can be used to get basic information about a configured puzzle in the system.
Run `python -m src.scripts.puzzle --help` for more information.

A DSN is assumed to be set in an environment variable as described above, otherise the `--dsn` switch must be provided for some subcommands.

#### Get Basic Puzzle Info
Use the command `python -m src.scripts.puzzle info {PUZZLE_ID}` to get basic information about a puzzle, if configured.

Example:
```shell
python -m src.scripts.puzzle info 2026-03-27

Puzzle Name: 2026-03-27

Region A: Ends with R
Region B: At least 8 letters
Region C: Has double letters
```
See `python -m src.scripts.puzzle info --help` for more information.

#### Get Region Hit Count
It may be helpful to see how many matches there are across a live (database) dictionary for a given puzzle.
Use the command `python -m src.scripts.puzzle get-region-hits {PUZZLE_ID}` to get this information for a configured puzzle.

Example:
```shell
python -m src.scripts.puzzle get-region-hits 2026-03-27
Compiling Region Hit information for Puzzle 2026-03-27...

Puzzle Name: 2026-03-27

Region A: Ends with R
Region B: At least 8 letters
Region C: Has double letters

Mask   Region:   Hits
(1)         A:   3399
(2)         B:  88453
(4)         C:   8703
(3)     A & B:   4176
(6)     B & C:  30736
(5)     C & A:   1042
(7) A & B & C:   1425
(0)      None:  40757
```
See `python -m src.scripts.puzzle get-region-hits --help` for more information.

#### Export Words for Region
There may be occasions to view the words in the dictionary that match a specific region.
For example, if a Region Hit Count shows that a region has unexpectedly high or unexpectedly low
numbers, it could be worth manually inspecting what words are being picked up by the Criteria.

By default, matching words will be printed to STDOUT but, because these datasets may be quite large, it is
often desirable to output them directly to a plaintext file. This can be done with the `--outfile` flag.

Example:
```shell
# Finds all words that match the intersection of regions A and C,
#  saving the results to the file "regions-ac.txt"
python -m src.scripts.puzzle export-region-words --outfile="regions-ac.txt" 2026-03-27 CA

Aggregating words for region(s) 'AC' with Criteria:
   - Ends with R
   - Has double letters

1042 results written to regions-ac.txt
```

See `python -m src.scripts.puzzle export-region-words --help` for more information.

### Dictionary CLI Tools
See the following section, Dictionary Management, for detailed information about the dictionary-related CLI tools.

## Dictionary Management
The raw dictionary is stored in [`./src/data/dictionary.txt`](./src/data/dictionary.txt), but this project supports the
ability to import these words into the database for improved querying and performance.  The script file [`./src/scripts/dictionary.py`](./src/scripts/dictionary.py)
can be run to do this against any database by passing in the desired DSN as described above.

Run `python -m src.scripts.dictionary --help` for more information about the script's usage.

The following sections assume an environment variable has been set and exported into the session, such as:
```shell
export DATABASE_URL="postgres://root:passwordCity@localhost:5432/primary" 
```
Change this to the local database (above, assuming Docker usage), or to the production database as desired.  Alternatively, provide
the `--dsn` flag, which will always take precedence.

### Importing to a Local or Remote Database
The `import` command will take a given `dictionary.txt` file and write it to the database. **Note** that this is destructive, so any
changes made directly in the database that do not exist in the dictionary file will be overwritten by this operation.

For example, to import the local dictionary file into a running version of the local database, run:
```shell
python -m src.scripts.dictionary import ./src/data/dictionary.txt
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

---

## Command Summaries
### Common Local Development Commands
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

