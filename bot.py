import discord
from discord.ext import commands
from discord import app_commands
import random
import re
import math
from PIL import Image, ImageDraw, ImageFont
import io
import aiohttp
import asyncio
from datetime import datetime, timezone
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Bot setup dengan intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    # Add CryptoCommand cog
    await bot.add_cog(CryptoCommand(bot))

    # Sync commands
    synced = await bot.tree.sync()
    print(f"🤖 Bot {bot.user.display_name} telah aktif!")
    print(f"📊 Connected to {len(bot.guilds)} servers")
    print(f"✅ Synced {len(synced)} slash commands.")


# Function to create welcome banner
async def create_welcome_banner(member):
    try:
        # Create a simple banner using PIL
        width, height = 800, 200
        img = Image.new(
            "RGB", (width, height), color=(114, 137, 218)
        )  # Discord blurple
        draw = ImageDraw.Draw(img)

        # Try to use default font, fallback if not available
        try:
            font_large = ImageFont.truetype("arial.ttf", 36)
            font_small = ImageFont.truetype("arial.ttf", 20)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Draw text
        welcome_text = f"Welcome {member.display_name}!"
        guild_text = f"to {member.guild.name}"

        # Center the text
        bbox = draw.textbbox((0, 0), welcome_text, font=font_large)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = height // 2 - 30

        draw.text((x, y), welcome_text, fill=(255, 255, 255), font=font_large)

        bbox2 = draw.textbbox((0, 0), guild_text, font=font_small)
        text_width2 = bbox2[2] - bbox2[0]
        x2 = (width - text_width2) // 2
        y2 = y + 50

        draw.text((x2, y2), guild_text, fill=(255, 255, 255), font=font_small)

        # Save to BytesIO
        banner_bytes = io.BytesIO()
        img.save(banner_bytes, format="PNG")
        banner_bytes.seek(0)

        return banner_bytes
    except Exception as e:
        print(f"Error creating welcome banner: {e}")
        return None


# Helper function untuk HTTP requests
async def fetch_api(url, headers=None):
    """Generic function untuk fetch API dengan error handling"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"API Error: Status {response.status} for {url}")
                    return None
    except aiohttp.ClientError as e:
        print(f"Network Error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return None


# MEME API Command
@bot.tree.command(name="meme", description="Dapatkan meme random dari internet!")
async def random_meme(interaction: discord.Interaction):
    await interaction.response.defer()  # Bot akan "typing..."

    try:
        # Coba beberapa API meme
        meme_apis = [
            "https://meme-api.com/gimme",
            "https://api.imgflip.com/get_memes",
            "https://some-random-api.ml/meme",
        ]

        meme_data = None

        # Coba API pertama (meme-api.com)
        meme_data = await fetch_api(meme_apis[0])

        if meme_data and "url" in meme_data:
            embed = discord.Embed(title="😂 Random Meme", color=0xFF6B35)

            # Set title jika ada
            if "title" in meme_data:
                embed.add_field(name="📝 Title", value=meme_data["title"], inline=False)

            # Set subreddit info jika ada
            if "subreddit" in meme_data:
                embed.add_field(
                    name="📍 From", value=f"r/{meme_data['subreddit']}", inline=True
                )

            if "author" in meme_data:
                embed.add_field(
                    name="👤 By", value=f"u/{meme_data['author']}", inline=True
                )

            if "ups" in meme_data:
                embed.add_field(
                    name="⬆️ Upvotes", value=f"{meme_data['ups']:,}", inline=True
                )

            # Set image
            embed.set_image(url=meme_data["url"])

            # Set footer
            embed.set_footer(
                text=f"Requested by {interaction.user.display_name} • Via meme-api.com",
                icon_url=interaction.user.display_avatar.url,
            )

            await interaction.followup.send(embed=embed)

        else:
            # Fallback jika API gagal
            embed = discord.Embed(
                title="❌ Meme Tidak Tersedia",
                description="Maaf, tidak bisa mengambil meme saat ini. Coba lagi nanti!",
                color=0xFF0000,
            )
            embed.add_field(
                name="💡 Tips",
                value="• Pastikan koneksi internet stabil\n• API mungkin sedang down\n• Coba beberapa saat lagi",
                inline=False,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as e:
        print(f"Error in meme command: {e}")
        embed = discord.Embed(
            title="❌ Error!",
            description="Terjadi kesalahan saat mengambil meme.",
            color=0xFF0000,
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


# ANIME INFO Command menggunakan Jikan API
@bot.tree.command(name="animeinfo", description="Cari informasi anime dari MyAnimeList")
async def anime_info(interaction: discord.Interaction, judul: str):
    await interaction.response.defer()

    try:
        # Search anime menggunakan Jikan API v4
        search_url = f"https://api.jikan.moe/v4/anime?q={judul}&limit=1"
        search_data = await fetch_api(search_url)

        if not search_data or not search_data.get("data"):
            embed = discord.Embed(
                title="❌ Anime Tidak Ditemukan",
                description=f"Tidak dapat menemukan anime dengan judul: **{judul}**",
                color=0xFF0000,
            )
            embed.add_field(
                name="💡 Tips",
                value="• Coba gunakan judul bahasa Inggris\n• Periksa ejaan judul\n• Gunakan judul yang lebih spesifik",
                inline=False,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        anime = search_data["data"][0]

        # Buat embed info anime
        embed = discord.Embed(
            title=anime.get("title", "Unknown Title"),
            description=(
                anime.get("synopsis", "Tidak ada sinopsis tersedia.")[:500] + "..."
                if anime.get("synopsis") and len(anime.get("synopsis", "")) > 500
                else anime.get("synopsis", "Tidak ada sinopsis tersedia.")
            ),
            color=0x2E86AB,
            url=anime.get("url"),
        )

        # Set thumbnail/poster
        if anime.get("images", {}).get("jpg", {}).get("large_image_url"):
            embed.set_thumbnail(url=anime["images"]["jpg"]["large_image_url"])

        # Info dasar
        embed.add_field(name="📺 Tipe", value=anime.get("type", "Unknown"), inline=True)

        embed.add_field(
            name="📅 Tahun",
            value=anime.get("year", "Unknown") or "Unknown",
            inline=True,
        )

        embed.add_field(
            name="📊 Episode",
            value=anime.get("episodes", "Unknown") or "Unknown",
            inline=True,
        )

        embed.add_field(
            name="⭐ Score",
            value=f"{anime.get('score', 'N/A')}/10" if anime.get("score") else "N/A",
            inline=True,
        )

        embed.add_field(
            name="👥 Popularity",
            value=(
                f"#{anime.get('popularity', 'N/A'):,}"
                if anime.get("popularity")
                else "N/A"
            ),
            inline=True,
        )

        embed.add_field(
            name="📈 Rank",
            value=f"#{anime.get('rank', 'N/A'):,}" if anime.get("rank") else "N/A",
            inline=True,
        )

        # Status
        embed.add_field(
            name="📺 Status", value=anime.get("status", "Unknown"), inline=True
        )

        # Duration
        embed.add_field(
            name="⏱️ Durasi", value=anime.get("duration", "Unknown"), inline=True
        )

        # Rating
        embed.add_field(
            name="🔞 Rating", value=anime.get("rating", "Unknown"), inline=True
        )

        # Genres
        if anime.get("genres"):
            genres = [genre["name"] for genre in anime["genres"][:5]]  # Limit 5 genres
            embed.add_field(name="🏷️ Genre", value=", ".join(genres), inline=False)

        # Studios
        if anime.get("studios"):
            studios = [studio["name"] for studio in anime["studios"][:3]]
            embed.add_field(name="🏢 Studio", value=", ".join(studios), inline=False)

        # Aired info
        if anime.get("aired", {}).get("string"):
            embed.add_field(
                name="📅 Tayang", value=anime["aired"]["string"], inline=False
            )

        # Set footer
        embed.set_footer(
            text=f"Requested by {interaction.user.display_name} • Data dari MyAnimeList",
            icon_url=interaction.user.display_avatar.url,
        )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        print(f"Error in animeinfo command: {e}")
        embed = discord.Embed(
            title="❌ Error!",
            description="Terjadi kesalahan saat mengambil info anime.",
            color=0xFF0000,
        )
        embed.add_field(
            name="🔍 Kemungkinan Masalah",
            value="• API MyAnimeList sedang down\n• Koneksi internet bermasalah\n• Rate limit tercapai",
            inline=False,
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


# QUOTE API Command
@bot.tree.command(name="quote", description="Dapatkan quote inspiratif random!")
async def random_quote(interaction: discord.Interaction):
    await interaction.response.defer()

    try:
        # API untuk quotes
        quote_apis = [
            "https://api.quotable.io/random",
            "https://zenquotes.io/api/random",
        ]

        # Coba API pertama
        quote_data = await fetch_api(quote_apis[0])

        if quote_data and "content" in quote_data:
            embed = discord.Embed(
                title="💭 Inspirational Quote",
                description=f"*\"{quote_data['content']}\"*",
                color=0x9B59B6,
            )

            embed.add_field(
                name="👤 Author", value=quote_data.get("author", "Unknown"), inline=True
            )

            if "tags" in quote_data:
                embed.add_field(
                    name="🏷️ Tags", value=", ".join(quote_data["tags"][:3]), inline=True
                )

            embed.set_footer(
                text=f"Requested by {interaction.user.display_name} • Via Quotable API",
                icon_url=interaction.user.display_avatar.url,
            )

            await interaction.followup.send(embed=embed)

        else:
            # Fallback quotes jika API gagal
            fallback_quotes = [
                {
                    "content": "The only way to do great work is to love what you do.",
                    "author": "Steve Jobs",
                },
                {
                    "content": "Innovation distinguishes between a leader and a follower.",
                    "author": "Steve Jobs",
                },
                {
                    "content": "Life is what happens to you while you're busy making other plans.",
                    "author": "John Lennon",
                },
                {
                    "content": "The future belongs to those who believe in the beauty of their dreams.",
                    "author": "Eleanor Roosevelt",
                },
                {
                    "content": "It is during our darkest moments that we must focus to see the light.",
                    "author": "Aristotle",
                },
            ]

            quote = random.choice(fallback_quotes)
            embed = discord.Embed(
                title="💭 Inspirational Quote",
                description=f"*\"{quote['content']}\"*",
                color=0x9B59B6,
            )
            embed.add_field(name="👤 Author", value=quote["author"], inline=True)
            embed.set_footer(
                text=f"Requested by {interaction.user.display_name} • Fallback Quote"
            )

            await interaction.followup.send(embed=embed)

    except Exception as e:
        print(f"Error in quote command: {e}")
        embed = discord.Embed(
            title="❌ Error!",
            description="Tidak bisa mengambil quote saat ini.",
            color=0xFF0000,
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


# CAT FACT API Command
@bot.tree.command(name="catfact", description="Fakta random tentang kucing!")
async def cat_fact(interaction: discord.Interaction):
    await interaction.response.defer()

    try:
        fact_data = await fetch_api("https://catfact.ninja/fact")

        if fact_data and "fact" in fact_data:
            embed = discord.Embed(
                title="🐱 Cat Fact", description=fact_data["fact"], color=0xFFA500
            )

            embed.set_thumbnail(url="https://cataas.com/cat?width=200&height=200")
            embed.set_footer(
                text=f"Requested by {interaction.user.display_name} • Via CatFact API",
                icon_url=interaction.user.display_avatar.url,
            )

            await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Cat Fact Tidak Tersedia",
                description="Tidak bisa mengambil fakta kucing saat ini.",
                color=0xFF0000,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as e:
        print(f"Error in catfact command: {e}")
        embed = discord.Embed(
            title="❌ Error!",
            description="Terjadi kesalahan saat mengambil cat fact.",
            color=0xFF0000,
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


# WEATHER API Command (OpenWeatherMap - dengan API key aktif)
@bot.tree.command(name="weather", description="Cek cuaca di kota tertentu")
async def weather_info(interaction: discord.Interaction, kota: str):
    await interaction.response.defer()

    try:
        # API OpenWeatherMap dengan API key yang sudah ada
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={kota}&appid=20948314ac3dee57aa88e101d2507a89&units=metric&lang=id"

        # Fetch data cuaca
        weather_data = await fetch_api(weather_url)

        if weather_data and weather_data.get("cod") == 200:
            # Data cuaca berhasil didapat
            main = weather_data["main"]
            weather = weather_data["weather"][0]
            wind = weather_data.get("wind", {})
            clouds = weather_data.get("clouds", {})
            sys = weather_data.get("sys", {})

            # Tentukan emoji berdasarkan kondisi cuaca
            weather_icons = {
                "clear sky": "☀️",
                "few clouds": "🌤️",
                "scattered clouds": "⛅",
                "broken clouds": "☁️",
                "shower rain": "🌦️",
                "rain": "🌧️",
                "thunderstorm": "⛈️",
                "snow": "🌨️",
                "mist": "🌫️",
                "fog": "🌫️",
                "haze": "🌫️",
            }

            weather_icon = weather_icons.get(weather["description"], "🌤️")

            # Buat embed cuaca
            embed = discord.Embed(
                title=f"{weather_icon} Cuaca {weather_data['name']}, {sys.get('country', '')}",
                description=f"**{weather['description'].title()}**",
                color=0x87CEEB,
                timestamp=datetime.now(timezone.utc),
            )

            # Suhu
            embed.add_field(
                name="🌡️ Suhu",
                value=(
                    f"**{main['temp']:.1f}°C**\n"
                    f"Terasa: {main.get('feels_like', 'N/A'):.1f}°C\n"
                    f"Min: {main.get('temp_min', 'N/A'):.1f}°C\n"
                    f"Max: {main.get('temp_max', 'N/A'):.1f}°C"
                ),
                inline=True,
            )

            # Kondisi Atmosfer
            embed.add_field(
                name="💨 Atmosfer",
                value=(
                    f"**Kelembaban:** {main.get('humidity', 'N/A')}%\n"
                    f"**Tekanan:** {main.get('pressure', 'N/A')} hPa\n"
                    f"**Visibilitas:** {weather_data.get('visibility', 'N/A')/1000:.1f} km"
                    if weather_data.get("visibility")
                    else "**Visibilitas:** N/A"
                ),
                inline=True,
            )

            # Angin & Awan
            embed.add_field(
                name="🌬️ Angin & Awan",
                value=(
                    f"**Kecepatan Angin:** {wind.get('speed', 'N/A')} m/s\n"
                    f"**Arah Angin:** {wind.get('deg', 'N/A')}°\n"
                    f"**Tutupan Awan:** {clouds.get('all', 'N/A')}%"
                ),
                inline=True,
            )

            # Waktu Matahari
            if sys.get("sunrise") and sys.get("sunset"):
                sunrise = datetime.fromtimestamp(sys["sunrise"], tz=timezone.utc)
                sunset = datetime.fromtimestamp(sys["sunset"], tz=timezone.utc)

                embed.add_field(
                    name="🌅 Matahari",
                    value=(
                        f"**Terbit:** <t:{sys['sunrise']}:t>\n"
                        f"**Terbenam:** <t:{sys['sunset']}:t>"
                    ),
                    inline=True,
                )

            # Koordinat
            if weather_data.get("coord"):
                coord = weather_data["coord"]
                embed.add_field(
                    name="📍 Koordinat",
                    value=f"**Lat:** {coord.get('lat', 'N/A')}\n**Lon:** {coord.get('lon', 'N/A')}",
                    inline=True,
                )

            # Timestamp data
            if weather_data.get("dt"):
                embed.add_field(
                    name="🕐 Update Terakhir",
                    value=f"<t:{weather_data['dt']}:R>",
                    inline=True,
                )

            embed.set_footer(
                text=f"Requested by {interaction.user.display_name} • Data dari OpenWeatherMap",
                icon_url=interaction.user.display_avatar.url,
            )

            await interaction.followup.send(embed=embed)

        elif weather_data and weather_data.get("cod") == "404":
            # Kota tidak ditemukan
            embed = discord.Embed(
                title="❌ Kota Tidak Ditemukan",
                description=f"Tidak dapat menemukan data cuaca untuk: **{kota.title()}**",
                color=0xFF0000,
            )

            embed.add_field(
                name="💡 Tips Pencarian",
                value=(
                    "• Gunakan nama kota dalam bahasa Inggris\n"
                    "• Coba tambahkan nama negara: `Jakarta, ID`\n"
                    "• Periksa ejaan nama kota\n"
                    "• Gunakan nama kota yang lebih spesifik"
                ),
                inline=False,
            )

            embed.add_field(
                name="📝 Contoh Format",
                value=(
                    "`/weather Jakarta`\n"
                    "`/weather London`\n"
                    "`/weather New York, US`\n"
                    "`/weather Tokyo, JP`"
                ),
                inline=False,
            )

            await interaction.followup.send(embed=embed, ephemeral=True)

        else:
            # Error dari API
            embed = discord.Embed(
                title="❌ Error API",
                description="Terjadi kesalahan saat mengambil data cuaca dari OpenWeatherMap.",
                color=0xFF0000,
            )

            if weather_data and weather_data.get("message"):
                embed.add_field(
                    name="📋 Detail Error",
                    value=f"```{weather_data['message']}```",
                    inline=False,
                )

            embed.add_field(
                name="🔄 Solusi",
                value=(
                    "• Coba lagi dalam beberapa saat\n"
                    "• Periksa ejaan nama kota\n"
                    "• API mungkin sedang maintenance"
                ),
                inline=False,
            )

            await interaction.followup.send(embed=embed, ephemeral=True)

    except aiohttp.ClientError as e:
        # Network error
        embed = discord.Embed(
            title="🌐 Network Error",
            description="Tidak dapat terhubung ke layanan cuaca.",
            color=0xFF0000,
        )
        embed.add_field(
            name="🔧 Kemungkinan Masalah",
            value="• Koneksi internet bermasalah\n• Server OpenWeatherMap down\n• Timeout request",
            inline=False,
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as e:
        print(f"Error in weather command: {e}")
        embed = discord.Embed(
            title="❌ Error!",
            description="Terjadi kesalahan tak terduga saat mengambil info cuaca.",
            color=0xFF0000,
        )
        embed.add_field(
            name="🐛 Debug Info", value=f"```{str(e)[:200]}```", inline=False
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


# DOG API Command
@bot.tree.command(name="dog", description="Dapatkan foto anjing random yang lucu!")
async def random_dog(interaction: discord.Interaction):
    await interaction.response.defer()

    try:
        dog_data = await fetch_api("https://dog.ceo/api/breeds/image/random")

        if dog_data and "message" in dog_data and dog_data["status"] == "success":
            embed = discord.Embed(title="🐕 Random Dog", color=0x8B4513)

            embed.set_image(url=dog_data["message"])
            embed.set_footer(
                text=f"Requested by {interaction.user.display_name} • Via Dog CEO API",
                icon_url=interaction.user.display_avatar.url,
            )

            await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Dog Image Tidak Tersedia",
                description="Tidak bisa mengambil foto anjing saat ini.",
                color=0xFF0000,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as e:
        print(f"Error in dog command: {e}")
        embed = discord.Embed(
            title="❌ Error!",
            description="Terjadi kesalahan saat mengambil foto anjing.",
            color=0xFF0000,
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


# Help command (Updated dengan API commands)
@bot.tree.command(name="help", description="Tampilkan semua commands yang tersedia")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📋 Daftar Commands",
        description="Berikut adalah semua commands yang tersedia:",
        color=0x7289DA,
    )

    # Utility Commands
    embed.add_field(
        name="🔧 Utility Commands",
        value=(
            "`/hello` - Bot menyapa kamu\n"
            "`/ping` - Cek latency bot\n"
            "`/serverinfo` - Info server\n"
            "`/userinfo` - Info user\n"
            "`/help` - Tampilkan commands ini\n"
            "`/botinfo` - Informasi lengkap tentang bot"
        ),
        inline=False,
    )

    # Calculator & Tools
    embed.add_field(
        name="🧮 Calculator & Tools",
        value=(
            "`/kalkulator [operasi]` - Kalkulator matematika\n"
            "`/acakangka [min] [max]` - Generate angka random"
        ),
        inline=False,
    )

    # API Commands
    embed.add_field(
        name="🌐 API Commands",
        value=(
            "`/meme` - Random meme dari internet\n"
            "`/animeinfo [judul]` - Info anime dari MAL\n"
            "`/quote` - Quote inspiratif random\n"
            "`/catfact` - Fakta random tentang kucing\n"
            "`/dog` - Foto anjing random\n"
            "`/weather [kota]` - Info cuaca (perlu setup)\n"
            "`/crypto [coin]` - Harga cryptocurrency (USD & IDR, perubahan 24h, market cap, volume)"
        ),
        inline=False,
    )

    embed.set_footer(text="Gunakan slash commands (/) untuk menjalankan perintah!")
    embed.set_thumbnail(url=bot.user.display_avatar.url)

    await interaction.response.send_message(embed=embed)


# Calculator command
@bot.tree.command(name="kalkulator", description="Kalkulator matematika sederhana")
async def kalkulator(interaction: discord.Interaction, operasi: str):
    try:
        # Validasi karakter yang diperbolehkan
        allowed_chars = re.compile(r"^[0-9+\-*/.()√π^% ]+$")
        expression = operasi.replace(" ", "")

        if not allowed_chars.match(expression):
            embed = discord.Embed(
                title="❌ Karakter Tidak Valid!",
                description="Operasi hanya boleh menggunakan angka dan operator matematika.",
                color=0xFF0000,
            )
            embed.add_field(
                name="✅ Operator Valid:",
                value="• `+` (tambah), `-` (kurang)\n• `*` (kali), `/` (bagi)\n• `()` (kurung)\n• `^` (pangkat), `√` (akar)\n• `%` (modulo), `π` (pi)",
                inline=False,
            )
            embed.add_field(
                name="📝 Contoh:",
                value="`/kalkulator 2 + 3 * 4`\n`/kalkulator √16 + 5^2`\n`/kalkulator π * 2`",
                inline=False,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Replace custom operators
        expression = expression.replace("√", "sqrt")
        expression = expression.replace("π", str(3.14159265359))
        expression = expression.replace("^", "**")

        # Fungsi helper untuk sqrt
        def sqrt(x):
            return math.sqrt(x)

        # Evaluasi dengan namespace terbatas untuk keamanan
        allowed_names = {
            "__builtins__": {},
            "sqrt": sqrt,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "pow": pow,
        }

        # Hitung hasil
        result = eval(expression, allowed_names)

        # Format hasil
        if isinstance(result, float):
            if result.is_integer():
                result = int(result)
            else:
                result = round(result, 8)  # Batasi decimal places

        # Buat embed hasil
        embed = discord.Embed(title="🧮 Hasil Kalkulasi", color=0x00BFFF)

        # Tampilkan operasi asli (dengan symbol yang bagus)
        display_expression = (
            operasi.replace("*", "×")
            .replace("/", "÷")
            .replace("sqrt", "√")
            .replace(str(3.14159265359), "π")
        )

        embed.add_field(
            name="📝 Operasi:", value=f"`{display_expression}`", inline=False
        )
        embed.add_field(name="✅ Hasil:", value=f"**{result}**", inline=False)

        # Tambahkan info tambahan untuk hasil tertentu
        if abs(result) > 1000000:
            embed.add_field(
                name="📊 Notasi Ilmiah:", value=f"{result:.2e}", inline=True
            )

        embed.set_footer(text=f"Dihitung oleh {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    except ZeroDivisionError:
        embed = discord.Embed(
            title="❌ Error: Pembagian dengan Nol!",
            description="Tidak bisa membagi dengan angka nol.",
            color=0xFF0000,
        )
        embed.add_field(
            name="💡 Tips:", value="Pastikan penyebut tidak bernilai 0", inline=False
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    except ValueError as e:
        embed = discord.Embed(
            title="❌ Error: Nilai Tidak Valid!",
            description="Periksa kembali operasi matematika Anda.",
            color=0xFF0000,
        )
        embed.add_field(
            name="🔍 Kemungkinan Masalah:",
            value="• Akar dari bilangan negatif\n• Operasi tidak valid\n• Syntax error",
            inline=False,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    except Exception as e:
        embed = discord.Embed(
            title="❌ Error dalam Kalkulasi!",
            description="Terjadi kesalahan saat menghitung operasi.",
            color=0xFF0000,
        )
        embed.add_field(
            name="💡 Saran:",
            value="• Periksa syntax operasi\n• Gunakan tanda kurung jika perlu\n• Coba operasi yang lebih sederhana",
            inline=False,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


# Tool: Random Number Generator
@bot.tree.command(
    name="acakangka", description="Generate angka random dalam range tertentu"
)
async def acak_angka(interaction: discord.Interaction, min_val: int, max_val: int):
    try:
        # Validasi input
        if min_val > max_val:
            min_val, max_val = max_val, min_val  # Swap jika terbalik

        # Batasi range untuk mencegah spam
        if abs(max_val - min_val) > 1000000:
            embed = discord.Embed(
                title="❌ Range Terlalu Besar!",
                description="Range maksimal adalah 1,000,000 angka.",
                color=0xFF0000,
            )
            embed.add_field(
                name="📝 Contoh Valid:",
                value="`/acakangka 1 100`\n`/acakangka -50 50`",
                inline=False,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Generate random number
        result = random.randint(min_val, max_val)

        # Buat embed hasil
        embed = discord.Embed(title="🌀 Angka Random", color=0x9B59B6)

        embed.add_field(
            name="📊 Range:",
            value=f"**{min_val:,}** hingga **{max_val:,}**",
            inline=False,
        )
        embed.add_field(name="🎲 Hasil:", value=f"**{result:,}**", inline=False)

        # Info tambahan
        total_possibilities = max_val - min_val + 1
        embed.add_field(
            name="📈 Info:",
            value=f"1 dari {total_possibilities:,} kemungkinan",
            inline=True,
        )

        embed.set_footer(text=f"Generated untuk {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="❌ Error!",
            description="Terjadi kesalahan saat generate angka random.",
            color=0xFF0000,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="hello", description="Bot akan menyapa kamu dengan ramah")
async def hello_command(interaction: discord.Interaction):
    # Daftar sapaan random
    greetings = [
        f"Halo {interaction.user.mention}! 👋 Semoga harimu menyenangkan!",
        f"Hai {interaction.user.mention}! 😊 Apa kabar hari ini?",
        f"Hello {interaction.user.mention}! 🌟 Senang bertemu denganmu!",
        f"Heyy {interaction.user.mention}! 🎉 Semoga hari ini penuh berkah!",
        f"Selamat datang {interaction.user.mention}! ✨ Ada yang bisa saya bantu?",
    ]

    greeting = random.choice(greetings)

    embed = discord.Embed(title="👋 Hello There!", description=greeting, color=0x00FF7F)

    # Tambahkan info tambahan
    embed.add_field(
        name="ℹ️ Info Bot",
        value=f"Prefix: `/`\nBot Online: ✅\nLatency: {round(bot.latency * 1000)}ms",
        inline=False,
    )

    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_footer(text=f"Requested by {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="ping", description="Cek latency/ping bot ke Discord")
async def ping_command(interaction: discord.Interaction):
    # Hitung latency
    latency = round(bot.latency * 1000)

    # Tentukan status berdasarkan latency
    if latency < 100:
        status = "🟢 Excellent"
        color = 0x00FF00
    elif latency < 200:
        status = "🟡 Good"
        color = 0xFFFF00
    elif latency < 300:
        status = "🟠 Fair"
        color = 0xFFA500
    else:
        status = "🔴 Poor"
        color = 0xFF0000

    embed = discord.Embed(
        title="🏓 Pong!", description=f"Bot latency: **{latency}ms**", color=color
    )

    embed.add_field(name="📊 Status Koneksi", value=status, inline=True)

    embed.add_field(name="📈 WebSocket Latency", value=f"{latency}ms", inline=True)

    embed.set_footer(text=f"Requested by {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="serverinfo", description="Informasi lengkap tentang server ini")
async def server_info(interaction: discord.Interaction):
    guild = interaction.guild

    # Hitung berbagai statistik
    text_channels = len(
        [ch for ch in guild.channels if isinstance(ch, discord.TextChannel)]
    )
    voice_channels = len(
        [ch for ch in guild.channels if isinstance(ch, discord.VoiceChannel)]
    )
    categories = len(guild.categories)

    # Status member
    online_members = len(
        [m for m in guild.members if m.status != discord.Status.offline]
    )
    bot_count = len([m for m in guild.members if m.bot])
    human_count = guild.member_count - bot_count

    embed = discord.Embed(
        title=f"📊 Server Info: {guild.name}",
        color=0x7289DA,
        timestamp=datetime.now(timezone.utc),
    )

    # Set server icon sebagai thumbnail
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    # Basic Info
    embed.add_field(
        name="🏷️ Basic Info",
        value=(
            f"**Server ID:** {guild.id}\n"
            f"**Owner:** {guild.owner.mention if guild.owner else 'Unknown'}\n"
            f"**Created:** <t:{int(guild.created_at.timestamp())}:R>\n"
            f"**Verification:** {guild.verification_level.name.title()}"
        ),
        inline=False,
    )

    # Member Stats
    embed.add_field(
        name="👥 Members",
        value=(
            f"**Total:** {guild.member_count:,}\n"
            f"**Humans:** {human_count:,}\n"
            f"**Bots:** {bot_count:,}\n"
            f"**Online:** {online_members:,}"
        ),
        inline=True,
    )

    # Channel Stats
    embed.add_field(
        name="📺 Channels",
        value=(
            f"**Text:** {text_channels}\n"
            f"**Voice:** {voice_channels}\n"
            f"**Categories:** {categories}\n"
            f"**Total:** {len(guild.channels)}"
        ),
        inline=True,
    )

    # Server Features
    embed.add_field(
        name="✨ Features",
        value=(
            f"**Roles:** {len(guild.roles)}\n"
            f"**Emojis:** {len(guild.emojis)}\n"
            f"**Boosts:** {guild.premium_subscription_count}\n"
            f"**Boost Level:** {guild.premium_tier}"
        ),
        inline=True,
    )

    # Server banner jika ada
    if guild.banner:
        embed.set_image(url=guild.banner.url)

    embed.set_footer(
        text=f"Requested by {interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url,
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="userinfo", description="Informasi tentang user tertentu")
async def user_info(interaction: discord.Interaction, user: discord.Member = None):
    # Default ke user yang menjalankan command
    if user is None:
        user = interaction.user

    embed = discord.Embed(
        title=f"👤 User Info: {user.display_name}",
        color=user.color if user.color.value != 0 else 0x7289DA,
        timestamp=datetime.now(timezone.utc),
    )

    # Set avatar sebagai thumbnail
    embed.set_thumbnail(url=user.display_avatar.url)

    # Basic User Info
    embed.add_field(
        name="🏷️ Basic Info",
        value=(
            f"**Username:** {user.name}\n"
            f"**Display Name:** {user.display_name}\n"
            f"**ID:** {user.id}\n"
            f"**Bot:** {'Yes' if user.bot else 'No'}"
        ),
        inline=False,
    )

    # Account Info
    embed.add_field(
        name="📅 Account",
        value=(
            f"**Created:** <t:{int(user.created_at.timestamp())}:R>\n"
            f"**Joined Server:** <t:{int(user.joined_at.timestamp())}:R>\n"
        ),
        inline=True,
    )

    # Status & Activity
    status_emoji = {
        discord.Status.online: "🟢",
        discord.Status.idle: "🟡",
        discord.Status.dnd: "🔴",
        discord.Status.offline: "⚫",
    }

    embed.add_field(
        name="📱 Status",
        value=(
            f"**Status:** {status_emoji.get(user.status, '❓')} {user.status.name.title()}\n"
            f"**Activity:** {user.activity.name if user.activity else 'None'}"
        ),
        inline=True,
    )

    # Roles (limit to top 10)
    if hasattr(user, "roles") and len(user.roles) > 1:
        roles = [role.mention for role in user.roles[1:]]  # Skip @everyone
        if len(roles) > 10:
            roles = roles[:10] + [f"... and {len(user.roles) - 11} more"]

        embed.add_field(
            name=f"🎭 Roles ({len(user.roles) - 1})",
            value=" ".join(roles) if roles else "No roles",
            inline=False,
        )

    # Permissions (hanya untuk member, bukan user biasa)
    if hasattr(user, "guild_permissions"):
        perms = user.guild_permissions
        key_perms = []

        if perms.administrator:
            key_perms.append("Administrator")
        if perms.manage_guild:
            key_perms.append("Manage Server")
        if perms.manage_channels:
            key_perms.append("Manage Channels")
        if perms.manage_messages:
            key_perms.append("Manage Messages")
        if perms.kick_members:
            key_perms.append("Kick Members")
        if perms.ban_members:
            key_perms.append("Ban Members")

        if key_perms:
            embed.add_field(
                name="🔑 Key Permissions", value=", ".join(key_perms[:5]), inline=False
            )

    # User banner jika ada
    if user.banner:
        embed.set_image(url=user.banner.url)

    embed.set_footer(
        text=f"Requested by {interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url,
    )

    await interaction.response.send_message(embed=embed)


# Welcome/Leave Events
@bot.event
async def on_member_join(member):
    """Event ketika member baru join server"""
    try:
        # Cari channel welcome (bisa disesuaikan)
        welcome_channel = None

        # Cari channel dengan nama yang mengandung 'welcome', 'general', atau 'lobby'
        for channel in member.guild.text_channels:
            if any(
                name in channel.name.lower()
                for name in ["welcome", "general", "lobby", "main"]
            ):
                welcome_channel = channel
                break

        # Jika tidak ada, gunakan system channel atau channel pertama
        if not welcome_channel:
            welcome_channel = (
                member.guild.system_channel or member.guild.text_channels[0]
            )

        if welcome_channel:
            # Buat welcome banner
            banner = await create_welcome_banner(member)

            # Buat embed welcome
            embed = discord.Embed(
                title="🎉 Welcome to the Server!",
                description=f"Hey {member.mention}, welcome to **{member.guild.name}**!",
                color=0x00FF7F,
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="👤 Member Info",
                value=(
                    f"**Account Created:** <t:{int(member.created_at.timestamp())}:R>\n"
                    f"**Member #{member.guild.member_count}**"
                ),
                inline=True,
            )

            embed.add_field(
                name="📋 Getting Started",
                value=(
                    "• Read the server rules\n"
                    "• Introduce yourself\n"
                    "• Have fun chatting!"
                ),
                inline=True,
            )

            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"Welcome to {member.guild.name}!")

            # Send welcome message
            if banner:
                file = discord.File(banner, filename="welcome_banner.png")
                embed.set_image(url="attachment://welcome_banner.png")
                await welcome_channel.send(file=file, embed=embed)
            else:
                await welcome_channel.send(embed=embed)

    except Exception as e:
        print(f"Error in welcome event: {e}")


@bot.event
async def on_member_remove(member):
    """Event ketika member leave server"""
    try:
        # Cari channel untuk goodbye message
        goodbye_channel = None

        for channel in member.guild.text_channels:
            if any(
                name in channel.name.lower()
                for name in ["goodbye", "leave", "general", "lobby"]
            ):
                goodbye_channel = channel
                break

        if not goodbye_channel:
            goodbye_channel = (
                member.guild.system_channel or member.guild.text_channels[0]
            )

        if goodbye_channel:
            embed = discord.Embed(
                title="👋 Goodbye!",
                description=f"**{member.display_name}** has left the server.",
                color=0xFF6B6B,
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="📊 Member Stats",
                value=f"We now have **{member.guild.member_count}** members.",
                inline=False,
            )

            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text="Thanks for being part of our community!")

            await goodbye_channel.send(embed=embed)

    except Exception as e:
        print(f"Error in goodbye event: {e}")


# Error handling
@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore command not found errors

    embed = discord.Embed(
        title="❌ Command Error",
        description="Terjadi kesalahan saat menjalankan command.",
        color=0xFF0000,
    )

    embed.add_field(
        name="🔍 Error Details", value=f"```{str(error)[:500]}```", inline=False
    )

    embed.add_field(
        name="💡 Tips",
        value="• Periksa syntax command\n• Gunakan `/help` untuk melihat commands\n• Coba lagi setelah beberapa saat",
        inline=False,
    )

    try:
        await ctx.send(embed=embed, ephemeral=True)
    except:
        pass


@bot.event
async def on_app_command_error(interaction: discord.Interaction, error):
    """Handle slash command errors"""
    if interaction.response.is_done():
        return

    embed = discord.Embed(
        title="❌ Command Error",
        description="Terjadi kesalahan saat menjalankan slash command.",
        color=0xFF0000,
    )

    embed.add_field(
        name="🔍 Error Type", value=f"```{type(error).__name__}```", inline=False
    )

    embed.add_field(
        name="💡 Saran",
        value="• Coba jalankan command lagi\n• Periksa parameter yang dimasukkan\n• Gunakan `/help` untuk bantuan",
        inline=False,
    )

    try:
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except:
        try:
            await interaction.followup.send(embed=embed, ephemeral=True)
        except:
            pass


class CryptoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = None

    async def setup_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        if self.session:
            await self.session.close()

    @app_commands.command(
        name="crypto", description="Menampilkan informasi harga cryptocurrency"
    )
    @app_commands.describe(
        coin="Simbol atau nama cryptocurrency (contoh: BTC, ETH, bitcoin)"
    )
    async def crypto(self, interaction: discord.Interaction, coin: str):
        await self.setup_session()

        try:
            # CoinGecko API endpoint
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": coin.lower(),
                "vs_currencies": "usd,idr",
                "include_24hr_change": "true",
                "include_market_cap": "true",
                "include_24hr_vol": "true",
            }

            # Try with coin as ID first
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data:
                        # If no data with ID, try searching by symbol
                        search_url = "https://api.coingecko.com/api/v3/search"
                        search_params = {"query": coin}

                        async with self.session.get(
                            search_url, params=search_params
                        ) as search_response:
                            if search_response.status == 200:
                                search_data = await search_response.json()
                                coins = search_data.get("coins", [])

                                if coins:
                                    # Use the first match
                                    coin_id = coins[0]["id"]
                                    params["ids"] = coin_id

                                    async with self.session.get(
                                        url, params=params
                                    ) as retry_response:
                                        if retry_response.status == 200:
                                            data = await retry_response.json()
                                        else:
                                            raise Exception(
                                                "Failed to fetch crypto data"
                                            )
                                else:
                                    embed = discord.Embed(
                                        title="❌ Error",
                                        description=f"Cryptocurrency '{coin}' tidak ditemukan!",
                                        color=0xFF0000,
                                        timestamp=datetime.now(timezone.utc),
                                    )
                                    await interaction.response.send_message(embed=embed)
                                    return
                            else:
                                raise Exception("Failed to search cryptocurrency")

                    if data:
                        # Get the first (and should be only) result
                        coin_data = list(data.values())[0]
                        coin_name = list(data.keys())[0].title()
                        coin_id = list(data.keys())[0]  # Store coin ID for chart

                        # Create embed
                        embed = discord.Embed(
                            title=f"💰 {coin_name.upper()} Price Information",
                            color=(
                                0x00FF00
                                if coin_data.get("usd_24h_change", 0) >= 0
                                else 0xFF0000
                            ),
                            timestamp=datetime.now(timezone.utc),
                        )

                        # Price information
                        usd_price = coin_data.get("usd", "N/A")
                        idr_price = coin_data.get("idr", "N/A")
                        change_24h = coin_data.get("usd_24h_change", 0)
                        market_cap = coin_data.get("usd_market_cap", "N/A")
                        volume_24h = coin_data.get("usd_24h_vol", "N/A")

                        # Price Info
                        embed.add_field(
                            name="💵 Price Information",
                            value=(
                                f"**USD:** ${usd_price:,.8f}\n"
                                if isinstance(usd_price, (int, float))
                                else f"**USD:** {usd_price}\n"
                            )
                            + (
                                f"**IDR:** Rp {idr_price:,.2f}"
                                if isinstance(idr_price, (int, float))
                                else f"**IDR:** {idr_price}"
                            ),
                            inline=False,
                        )

                        # 24h Change
                        change_emoji = "📈" if change_24h >= 0 else "📉"
                        change_color = "+" if change_24h >= 0 else ""
                        embed.add_field(
                            name=f"{change_emoji} 24h Performance",
                            value=f"**Change:** {change_color}{change_24h:.2f}%",
                            inline=True,
                        )

                        # Market Data
                        market_info = ""
                        if isinstance(market_cap, (int, float)):
                            market_info += f"**Market Cap:** ${market_cap:,.0f}\n"
                        if isinstance(volume_24h, (int, float)):
                            market_info += f"**24h Volume:** ${volume_24h:,.0f}"

                        if market_info:
                            embed.add_field(
                                name="📊 Market Data",
                                value=market_info,
                                inline=True,
                            )

                        embed.set_footer(
                            text=f"Requested by {interaction.user.display_name} • Data from CoinGecko API",
                            icon_url=interaction.user.display_avatar.url,
                        )

                        # Create chart embed
                        chart_embed = discord.Embed(
                            title=f"📈 {coin_name.upper()} Price Chart",
                            description=f"7-day price chart for {coin_name}",
                            color=0x00D4AA,
                            timestamp=datetime.now(timezone.utc),
                        )

                        # Add chart image from CoinGecko
                        chart_url = (
                            f"https://www.coingecko.com/coins/{coin_id}/sparkline.svg"
                        )
                        chart_embed.set_image(url=chart_url)

                        chart_embed.set_footer(
                            text="Chart provided by CoinGecko",
                            icon_url="https://static.coingecko.com/s/thumbnail-007177f3eca19695592f0b8b0eabbdae282b54154e1be912285c9034ea6cbaf2.png",
                        )

                        # Send both embeds
                        await interaction.response.send_message(
                            embeds=[embed, chart_embed]
                        )
                    else:
                        embed = discord.Embed(
                            title="❌ Error",
                            description=f"Data untuk '{coin}' tidak ditemukan!",
                            color=0xFF0000,
                            timestamp=datetime.now(timezone.utc),
                        )
                        await interaction.response.send_message(embed=embed)

                else:
                    embed = discord.Embed(
                        title="❌ Error",
                        description="Gagal mengambil data cryptocurrency. Silakan coba lagi.",
                        color=0xFF0000,
                        timestamp=datetime.now(timezone.utc),
                    )
                    await interaction.response.send_message(embed=embed)

        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="❌ Error",
                description="Request timeout. Silakan coba lagi.",
                color=0xFF0000,
                timestamp=datetime.now(timezone.utc),
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(f"Error in crypto command: {e}")
            embed = (
                discord.Embed(
                    title="❌ Error",
                    description="Terjadi kesalahan saat mengambil data cryptocurrency.",
                    color=0xFF0000,
                    timestamp=datetime.utc,
                ),
            )

            await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="botinfo", description="Informasi lengkap tentang bot ini"
    )
    async def info_command(self, interaction: discord.Interaction):
        bot_user = self.bot.user

        # Hitung statistik bot
        total_guilds = len(self.bot.guilds)
        total_users = len(set(self.bot.get_all_members()))
        total_channels = len(set(self.bot.get_all_channels()))

        embed = discord.Embed(
            title=f"🤖 Bot Info: {bot_user.display_name}",
            color=0x7289DA,
            timestamp=datetime.now(timezone.utc),
        )

        # Set bot avatar sebagai thumbnail
        if bot_user.avatar:
            embed.set_thumbnail(url=bot_user.avatar.url)

        # Basic Info
        embed.add_field(
            name="🏷️ Basic Info",
            value=(
                f"**Bot Name:** {bot_user.display_name}\n"
                f"**Bot ID:** {bot_user.id}\n"
                f"**Developer:** Rasena\n"
                f"**Created:** <t:{int(bot_user.created_at.timestamp())}:R>"
            ),
            inline=False,
        )

        # Statistics
        embed.add_field(
            name="📊 Statistics",
            value=(
                f"**Servers:** {total_guilds:,}\n"
                f"**Users:** {total_users:,}\n"
                f"**Channels:** {total_channels:,}\n"
                f"**Ping:** {round(self.bot.latency * 1000)}ms"
            ),
            inline=True,
        )

        # Technical Info
        embed.add_field(
            name="⚙️ Technical",
            value=(
                f"**Library:** discord.py\n"
                f"**Python:** 3.8+\n"
                f"**Version:** 1.0.0\n"
                f"**Status:** Online"
            ),
            inline=True,
        )

        # Developer Social Media
        embed.add_field(
            name="👨‍💻 Developer Contact",
            value=(
                f"**Name:** Rasena\n"
                f"**Instagram:** [rrssnaaa](https://www.instagram.com/rrssnaaa)\n"
                f"**TikTok:** [hyrasena](https://www.tiktok.com/@hyrasena)"
            ),
            inline=False,
        )

        embed.set_footer(
            text=f"Requested by {interaction.user.display_name} • Made with ❤️ by Rasena",
            icon_url=interaction.user.display_avatar.url,
        )

        await interaction.response.send_message(embed=embed)


# Tambahkan ini di bagian startup bot Anda
async def setup_crypto_commands(bot):
    await bot.add_cog(CryptoCommand(bot))


# Run the bot
if __name__ == "__main__":
    token = os.getenv("TOKEN")

    if token is None:
        print("❌ TOKEN tidak ditemukan. Pastikan sudah diset di environment variable.")
    else:
        bot.run(token)
