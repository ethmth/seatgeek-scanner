# Seatgeek Scanner (WORK-IN-PROGRESS)

A tool to continuously search for tickets that fall below a target price within a date range for any given show on Seatgeek. Integrates with IFTTT webhooks. Uses Python, Selenium, and Docker.

## Disclaimer

The author of this program holds no responsibility for what a user may choose to do with the script. I created this as a programming exercise to learn Selenium.

Proceed with caution, keeping Seatgeek's Terms of Service in mind and be aware of potential deterrents on your IP/account that Seatgeek may incur if you so choose to use this program irresponsibly.

## Requirements

Requires `docker` and `docker-compose`.

## Setup

### Getting the Files

Ensure `git` is installed, then clone the git repo.

```sh
git clone https://github.com/ethmth/seatgeek-scanner.git
cd seatgeek-scanner/
```

### Configuration

In the `src` directory, copy the `.env-sample` file and call the copy `.env`.

```sh
cp src/.env-sample src/.env
```

Edit the `.env` file, providing the show you want to track, an optional IP address for a ThingM Blink1 API ([github.com/ethmth/thingm-blink-api](https://github.com/ethmth/thingm-blink-api)), an IFTTT event you want to trigger, a date range you want to search through, and a target price.

```sh
nano src/.env
```

```
SHOW_PREFIX=https://seatgeek.com/funny-girl-tickets
BLINK_IP=127.0.0.1:5000
IFTTT_KEY=<YOUR_IFTTT_KEY_HERE>
IFTTT_EVENT=fg_tickets_avail
IFTTT_MESSAGE="Tickets fell below target price"
DATE_RANGE=20230223-20230401
TARGET_PRICE=79
```

## Running the Container

While in the repo directory, run the scanner using docker compose.

```sh
docker-compose up
```

Alternatively, you can set the API to run in the background.

```sh
docker-compose up -d
```

(Stop the background container by entering the repo directory and running `docker-compose stop`)

The docker container will run, continuously scanning Seatgeek to check whether tickets for the show you specified, within the date range specified, fall below the target price. If so, the IFTTT event specified in the `.env` file is triggered, and if you provided a Blink IP, a request will be sent to that as well.
