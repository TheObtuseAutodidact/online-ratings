# Online Ratings

[![Travis Build Status](https://travis-ci.org/usgo/online-ratings.svg?branch=master)](https://travis-ci.org/usgo/online-ratings)

AGA Online Ratings protocol and implementation

The goal of the AGA Online Ratings Protocol is to provide Go Servers with a
standard way to report results between AGA members that happen on their servers
to us for computing a cross-server rating.

Other goals of the project can be found on the [implementation plan here](https://docs.google.com/document/d/1XOcpprw0Y8xhHTroYnUU7tt0rN6F3-T4_9sgOeifqwI)

## Using the API (Go Server implementers)

All api endpoints accept and return JSON.
Available endpoints:
  - `POST /api/v1/games` Report a game result.
  - `GET /api/v1/games/<game_id>` Get a game result by ID
  - `GET /api/v1/games/<game_id>/sgf` Get a game's SGF file by ID
  - `GET /api/v1/players/<player_id>` Get a player by ID
  - `GET /api/v1/players?token=<token>` Get a player by their secret token.

Here's an example request to create a game:

```
POST /api/v1/games
  ?server_tok=secret_kgs
  &b_tok=player_1_token
  &w_tok=player_2_token
{
  "black_id": 1,
  "white_id": 2,
  "game_server": "KGS",
  'rated': True,
  'result': 'W+R',
  'date_played': '2015-02-26T10:30:00',
  'game_record': '(;FF[4]GM[1]SZ[19]CA[UTF-8]BC[ja]WC[ja]EV[54th Japanese Judan]PB[Kono Takashi]BR[8p]PW[O Meien]WR[9p]KM[6.5]DT[2015-02-26]RE[W+R];B[qd];W[dp];B[pq];W[od])'
}
```

You can also submit a `game_url` in lieu of the `game_record` field.
`server_tok` is the game server's secret token, and `b_tok`, `w_tok` are the
player's secret tokens. 

## Getting Started (Online Ratings backend developers)

### Overview

Before you get started working on Online Ratings, you'll need to do some setup:

* Choose your package manager
* Install Python3 and the relevant dependencies
* Install the Docker command line tools.
* Get set up with a VM to use with Docker
* Build and run the app on the VM with Docker
* log in using the fake login credentials found in `web/create_db.py`

## Package Managers

This dev guide assumes a POSIX tool chain. Most developers on this project use OSX.

* OSX: Install [homebrew](http://brew.sh/)
* Linux/Ubuntu: You should already apt-get installed

## Python and Dependencies

1.  Install Python3
    * OSX: `brew install python3`
    * Linux: You probably already have Python3 installed. If not: `sudo apt-get
      install python3`
4.  Install [pip](https://en.wikipedia.org/wiki/Pip_(package_manager))
    * `curl https://bootstrap.pypa.io/get-pip.py | python3`
5.  Install postgres
    * OSX: `brew install postgresql`
    * Linux: [See here](https://www.postgresql.org/download/linux/ubuntu/)
6.  Install the python dependencies with pip.
    * cd to `online-ratings/web` directory and run: `pip install -r requirements.txt`
7.  Run the tests!
    * cd to `online-ratings/web` directory and run: `python3 -m unittest
      discover`

**[Optional]**

Optionally, you can install VirtualEnv, which makes working with python versions
a little easier.

1.  Install Virtual Environment: mkvirtualenv
    * `pip install virtualenvwrapper`
    * Add `source /usr/local/bin/virtualenvwrapper.sh` to your `.bash_profile`
      or `.bashrc`. Alternatively, just run `source
      /usr/local/bin/virtualenvwrapper.sh` when you need it.
2.  Use VirtualWrapper to make a new virtual env:;
    * `mkvirtualenv --python=/usr/local/bin/python3 online-ratings-env`

## Getting set up with Docker

### Mac
You'll want to install `docker`, `docker-compose`, and `docker-machine`. Note:
If you're using Docker for Mac (v1.12), installing docker-machine is probably
unnecessary.

```shell
$ brew install docker docker-compose docker-machine
```

You'll also want to have a virtual machine installed, such as VirtualBox. 

```shell
$ brew cask install virtualbox
```

You can then set up a docker host on VirtualBox.

```shell
$ docker-machine create -d virtualbox dev
```

The output of the above command will tell you how to set the local environment
variables to connect to your shiny new docker host.  For Bash, it's `eval
$(docker-machine env dev)`. For fish shell it's `eval (docker-machine env dev)`.

### Linux
Install [docker](https://docs.docker.com/engine/installation/) and [docker-compose](https://docs.docker.com/compose/install/)

### [All]
Then the following commands should start the app running and start tailing the logs.

```shell
cp .env_example .env
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml logs
```

The `build` step will create docker containers for each part of the app (nginx,
flask, etc.). The `up -d` step will coordinate the running of all the containers
as specified in the docker-compose yaml file.

If this is the first time you've set up the database, you'll need to create the
initial tables with

```shell
docker-compose -f docker-compose.dev.yml run --rm web python /usr/src/app/create_db.py
```

The dockerfile configuration will then serve the app at [[virtual machine IP on
localhost]], port 80. For example, http://192.168.99.100:80 You can find your
Docker hosts by running

```shell
docker-machine ls
```

You can remap the ports that the app listens on by editing `docker-compose.base.yml` and changing the nginx ports mapping to something like `"8080:80"`

## Development
You might find it useful to have a python shell in Docker. This lets you interactively play with database queries and such.
```
docker-compose -f docker-compose.dev.yml run --rm web python -i /usr/src/app/shell.py
>>> from app.models import Player
>>> print(Player.query.filter(Player.id==1).first())
Player FooPlayerKGS, id 1
```

## Running Locally

Generally, we prefer running with Docker. However, if you wish to run the web
server locally (perhaps for a faster iteration cycle) you can do so with the
following:

```shell
cd online-ratings
sed 's/^\([^#]\)/export \1/g' .env_example > .env_local 
source .env_local
cd web
pip install -r requirements.txt
python3 run.py
```

You should see:

```shell
* Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

Note: At this point, you still need to run your local Online Ratings instance
against a database instance. You can either create a local postgres instance and
create some data. Or, you can point your local server at the running Docker
images. For that, all you need to do is run through the Docker startup
instructions above and then change `DB_SERVICE` in your `.env_local` to
`0.0.0.0`.


## Running the Tests
The standard `unittest` module has a discovery feature that will automatically
find and run tests.  The directions given below will search for tests in any
file named `test_*.py`.

```shell
source bin/activate
cd web
python -m unittest discover
```
To see other options for running tests, you may:

```shell
cd <repo root directory>
python -m unittest --help
```

## Deploying

Deploying should be the same as testing, except that the docker machine you use
is on AWS, etc. Additionally, you should run docker-compose with the prod
overrides:

```shell
vim .env (change passwords, secret_key to production values)
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

## Documentation

### Running locally

1. Ensure [`mkdocs`][0] is installed.
2. Run `mkdocs serve` from within the root of `online-ratings`.
3. Load it in a browser and profit!

### Making non-API Pages

Create or edit the `.md` files within `docs/`.

Refer to [mkdocs][0] for more details.

### Generating API Documentation

Source files to be edited can be found in `docs/schemata`.  The files are in [YAML][1] for improved
readability.

1. Install [prmd][2] per their instructions.
2. From root of `online-ratings`, run
   `prmd combine --meta docs/meta.yml --output docs/schema.json docs/schemata`
3. From root of `online-ratings`, run `prmd doc --output docs/api.md docs/schema.json`

[JSON Schema][3] is the general format used for types and [JSON Hyper-Schema][4] is used for
endpoint definitions.

### Deploying To gh-pages

1. Run `mkdocs gh-deploy --clean`.
2. That's it!

## Questions?
The developer mail list can be found here:
https://groups.google.com/forum/#!forum/usgo-online-ratings

[0]: http://www.mkdocs.org/
[1]: https://en.wikipedia.org/wiki/YAML
[2]: https://github.com/interagent/prmd
[3]: http://json-schema.org/documentation.html
[4]: http://json-schema.org/latest/json-schema-hypermedia.html
