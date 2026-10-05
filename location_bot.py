import os
import discord
from discord.ext import commands
import firebase_admin
from firebase_admin import credentials, db
import datetime
import requests

# All settings come from environment variables, see the README
cred = credentials.Certificate(os.environ["FIREBASE_CREDENTIALS"])  # path to your service account JSON
firebase_admin.initialize_app(cred, {"databaseURL": os.environ["FIREBASE_DB_URL"]})

discord_token = os.environ["DISCORD_BOT_TOKEN"]
opencage_api_key = os.environ["OPENCAGE_API_KEY"]

# Discord Bot Setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

def get_coordinates(location):
    """
    Get latitude and longitude using OpenCage Geocoder API.
    :param location: Location name (city, country, etc.)
    :return: (latitude, longitude) tuple or None if not found
    """
    try:
        url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={opencage_api_key}"
        response = requests.get(url)
        data = response.json()

        if data["results"]:
            lat = data["results"][0]["geometry"]["lat"]
            lon = data["results"][0]["geometry"]["lng"]
            return lat, lon
        else:
            return None
    except Exception as e:
        print(f"Error fetching coordinates: {e}")
        return None

@bot.command()
async def register(ctx, *, location: str):
    """
    Register a new user in Firebase using OpenCage API for coordinates.
    :param ctx: Discord context
    :param location: Location name (e.g., "Mumbai, India")
    """
    try:
        user_id = str(ctx.author.id)
        username = ctx.author.name
        ref = db.reference(f"users/{user_id}")

        if ref.get():
            await ctx.send(f"⚠️ {ctx.author.mention}, you are already registered!")
            return

        # Fetch coordinates
        coordinates = get_coordinates(location)
        if not coordinates:
            await ctx.send(f"❌ Unable to find coordinates for '{location}'. Try another city!")
            return

        latitude, longitude = coordinates

        # Store user details in Firebase
        ref.set({
            "username": username,
            "discord_id": user_id,
            "location": location,
            "latitude": latitude,
            "longitude": longitude,
            "registered_at": datetime.datetime.utcnow().isoformat(),
            "updated_at": datetime.datetime.utcnow().isoformat()
        })

        await ctx.send(f"✅ {ctx.author.mention}, you have been registered successfully in **{location}**!")
    except Exception as e:
        await ctx.send(f"⚠️ An error occurred: {e}")

@bot.command()
async def location(ctx, user_id: str = None):
    """
    Fetch a user's live location from Firebase.
    If no user_id is provided, fetch the caller's location.
    """
    try:
        if not user_id:
            user_id = str(ctx.author.id)  # Default to caller's ID
        
        ref = db.reference(f"users/{user_id}")
        data = ref.get()

        if data:
            location = data.get("location", "Unknown")
            latitude = data["latitude"]
            longitude = data["longitude"]
            updated_at = data["updated_at"]

            embed = discord.Embed(
                title=f"📍 Location of {data['username']}",
                description=f"**{location}**\nLatitude: {latitude}, Longitude: {longitude}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Last Updated", value=updated_at, inline=False)
            embed.add_field(name="Google Maps Link", 
                            value=f"[View on Google Maps](https://www.google.com/maps?q={latitude},{longitude})", 
                            inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"⚠️ No location data found for {user_id}.")
    except Exception as e:
        await ctx.send(f"⚠️ An error occurred: {e}")

@bot.command()
async def update_location(ctx, *, location: str):
    """
    Update the caller's location in Firebase using OpenCage API.
    """
    try:
        user_id = str(ctx.author.id)
        ref = db.reference(f"users/{user_id}")

        if not ref.get():
            await ctx.send(f"⚠️ {ctx.author.mention}, you are not registered! Use `!register <city>` first.")
            return

        # Fetch new coordinates
        coordinates = get_coordinates(location)
        if not coordinates:
            await ctx.send(f"❌ Unable to find coordinates for '{location}'. Try another city!")
            return

        latitude, longitude = coordinates

        # Update Firebase
        ref.update({
            "location": location,
            "latitude": latitude,
            "longitude": longitude,
            "updated_at": datetime.datetime.utcnow().isoformat()
        })

        await ctx.send(f"✅ {ctx.author.mention}, your location has been updated to **{location}**!")
    except Exception as e:
        await ctx.send(f"⚠️ An error occurred: {e}")

if __name__ == "__main__":
    bot.run(discord_token)
