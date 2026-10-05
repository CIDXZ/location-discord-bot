# Location Discord bot

A small Discord bot that lets people in a server share where they are. Each person registers a place by name, the bot
turns it into coordinates, and anyone can pull up a member's location as a card with a Google Maps link.

## Commands

| Command | What it does |
|---|---|
| `!register <place>` | sign up with a city or place, e.g. `!register Visakhapatnam, India` |
| `!update_location <place>` | change your place |
| `!location [user id]` | show someone's location card, or your own if you leave the id out |

## How it works

- Place names go to the [OpenCage](https://opencagedata.com) geocoding API, which returns latitude and longitude.
- Each member is stored in a Firebase Realtime Database under their Discord id, with the place name, coordinates and
  when it was registered and last updated.
- `!location` reads that record back and posts it as an embed with a Maps link.

## Running it

```
pip install -r requirements.txt
```

You need a Discord bot, an OpenCage key (the free tier is plenty) and a Firebase project with Realtime Database turned
on. Then set:

| Variable | What it is |
|---|---|
| `DISCORD_BOT_TOKEN` | from the Discord Developer Portal |
| `OPENCAGE_API_KEY` | from your OpenCage dashboard |
| `FIREBASE_CREDENTIALS` | path to the service account JSON from Firebase, Project settings, Service accounts |
| `FIREBASE_DB_URL` | your Realtime Database URL |

Then `python location_bot.py`. The bot needs the Message Content intent turned on in the developer portal.

## On privacy

It's opt-in and only as precise as the place name someone types, so it's a city, not a GPS position. But anyone in the
server can look anyone up, which is fine among friends and not fine anywhere else. A real version would let people
choose who sees them and add a command to delete your own record.
