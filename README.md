# DS3 Death Counter

## Demo

[Watch the demo video](https://github.com/user-attachments/assets/49bd52cb-4f27-447c-aeeb-aaa57d882f22)

## About

DS3 Death Counter tracks deaths during a Twitch stream when the channel is playing **Dark Souls III**. It watches the stream, detects deaths from the video, saves screenshots and timestamps, and displays the results in a Streamlit dashboard.

The dashboard includes death totals, timing and daily trends, stream information, and a screenshot gallery.

## Requirements

- Docker and Docker Compose
- A Twitch application with a client ID and client secret
- The Twitch broadcaster's ID
- A Firefox profile for the stream player

## Setup

### 1. Configure Twitch credentials

Create an application in the [Twitch Developer Console](https://dev.twitch.tv/console/apps). Select **Register Your Application**, complete the form, and copy its client ID and client secret from the application settings.

Create a `.env` file in the project root:

```dotenv
APP_ID=your_twitch_client_id
APP_SECRET=your_twitch_client_secret
BROADCASTER_ID=your_twitch_broadcaster_id
```

Keep this file private and do not commit it.

### 2. Create Twitch authentication tokens

Install the project dependencies, then run the login script from the `twitch` directory:

```bash
pip install -r requirements.txt
cd twitch
python first_login.py
cd ..
```

Complete the Twitch authorization flow. The script saves the generated tokens to `twitch/tokens.json`, which Docker Compose mounts into the reader container.

### 3. Add a Firefox profile

Export the Firefox profile you want the stream player to use and place it in the project root as `ie0j48b9.default-release`. Docker Compose mounts this directory into the reader container.

### 4. Start the application

From the project root, build and start both services:

```bash
docker compose up --build -d
```

Open the dashboard at [http://localhost:8501](http://localhost:8501). To follow the service logs:

```bash
docker compose logs -f
```

To stop the services:

```bash
docker compose down
```

## Data and configuration

Docker Compose stores the database, screenshots, and logs in named volumes. The reader refreshes Twitch tokens in `twitch/tokens.json`; keep the token file and Firefox profile private.

The main settings are read from `.env`:

| Variable | Description |
| --- | --- |
| `APP_ID` | Twitch application client ID |
| `APP_SECRET` | Twitch application client secret |
| `BROADCASTER_ID` | Twitch ID of the channel to monitor |
