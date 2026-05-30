#!/usr/bin/env python3
"""
OnlyGhost Discord Bot - AI-Powered Studio Manager
Handles devlog generation, server management, and community updates
Uses Google Gemini API (Free)
"""
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import discord
from discord.ext import commands
import google.generativeai as genai
from dotenv import load_dotenv

# .env dosyasını yerelde çalışırken yükler (Render'da değişkenleri panelden okur)
load_dotenv()

# ============================================================================
# RENDER HEALTH CHECK SERVER
# ============================================================================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot aktif!")
        
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# Render port hatası vermesin diye web sunucusunu arka planda başlatıyoruz
threading.Thread(target=run_health_check, daemon=True).start()

# ============================================================================
# CONFIGURATION - FROM ENVIRONMENT VARIABLES
# ============================================================================
OWNER_ID = int(os.getenv("OWNER_ID", "581877396584529921"))
GUILD_ID = int(os.getenv("GUILD_ID", "1510030141005500626"))
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Varsayılan help komutunu kaldırıyoruz ki kendi yazdığımız çakışmasın
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ============================================================================
# SYSTEM PROMPT FOR AI
# ============================================================================
SYSTEM_PROMPT = """You are OnlyGhost's AI Assistant for the Life N Dinos game studio.

PERSONALITY & RULES:
- You are professional but friendly
- You speak in the same style as OnlyGhost (Turkish/English mix, casual but technical)
- You NEVER deviate from OnlyGhost's instructions
- You follow strict guidelines and never make up information
- You are knowledgeable about game development, pixel art, and indie games
- You provide accurate, helpful responses

ABOUT ONLYGHOST:
- Solo indie developer
- Creates pixel art puzzle games
- Current game: Life N Dinos (dinosaur puzzle strategy game)
- Passionate about creative gameplay and fun mechanics
- Active on itch.io

DEVLOG WRITING GUIDELINES:
- Write in English (professional tone)
- Include: What was done, bugs fixed, features added, next steps
- Use emojis for visual appeal
- Keep it concise but informative
- Format: Title, Summary, Changes, Next Steps
- Always mention version number

RESPONSE GUIDELINES:
- Be concise and direct
- Use markdown formatting
- Include relevant emojis
- Provide actionable information
- Ask clarifying questions if needed

RESTRICTIONS:
- Only respond to OnlyGhost's commands
- Don't make promises about features
- Don't share unreleased game details
- Don't modify server settings without explicit permission
- Always confirm important actions"""

# ============================================================================
# GEMINI AI SETUP
# ============================================================================
def setup_gemini():
    """Setup Gemini API"""
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not found in environment!", flush=True)
        return False
    
    genai.configure(api_key=GEMINI_API_KEY)
    return True

def generate_devlog(project_info: str) -> str:
    """Generate a devlog using Gemini AI"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        prompt = f"""Generate a professional devlog for this project update:\n\n{project_info}\n\nFormat the devlog with:\n1. Title (with version)\n2. Summary (2-3 sentences)\n3. What's New (bullet points)\n4. Bug Fixes (if any)\n5. Next Steps\n\nKeep it concise and engaging."""
        response = model.generate_content(
            f"{SYSTEM_PROMPT}\n\n{prompt}",
            generation_config=genai.types.GenerationConfig(temperature=0.7, max_output_tokens=1024)
        )
        return response.text
    except Exception as e:
        return f"❌ Error generating devlog: {str(e)}"

def get_ai_response(user_message: str) -> str:
    """Get AI response for user queries"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        response = model.generate_content(
            f"{SYSTEM_PROMPT}\n\nUser: {user_message}",
            generation_config=genai.types.GenerationConfig(temperature=0.7, max_output_tokens=512)
        )
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ============================================================================
# BOT EVENTS
# ============================================================================
@bot.event
async def on_ready():
    """Bot is ready"""
    print(f"✅ Bot logged in as {bot.user}", flush=True)
    print(f"📊 Watching {len(bot.guilds)} guild(s)", flush=True)
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="Life N Dinos development"
    ))

@bot.event
async def on_member_join(member):
    """Auto-assign Member role to new users"""
    try:
        guild = bot.get_guild(GUILD_ID)
        if guild:
            member_role = discord.utils.get(guild.roles, name="👤 Member")
            if member_role:
                await member.add_roles(member_role)
                print(f"✅ Assigned Member role to {member.name}", flush=True)
                
                try:
                    embed = discord.Embed(
                        title="🦖 Welcome to OnlyGhost's Game Studio!",
                        description="Thanks for joining our community!",
                        color=discord.Color.green()
                    )
                    embed.add_field(name="📌 Getting Started", value="Check out #ℹ️-about-me for server info and #📋-rules for guidelines.", inline=False)
                    embed.add_field(name="🎮 Current Game", value="**Life N Dinos** - A puzzle strategy game about saving dinosaurs!", inline=False)
                    await member.send(embed=embed)
                except:
                    pass
    except Exception as e:
        print(f"❌ Error in on_member_join: {e}", flush=True)

# ============================================================================
# OWNER ONLY COMMANDS
# ============================================================================
def is_owner():
    """Check if user is owner"""
    async def predicate(ctx):
        return ctx.author.id == OWNER_ID
    return commands.check(predicate)

@bot.command(name="devlog")
@is_owner()
async def devlog_command(ctx, *, project_info):
    async with ctx.typing():
        devlog = generate_devlog(project_info)
        embed = discord.Embed(title="📝 Generated Devlog", description=devlog, color=discord.Color.blue(), timestamp=datetime.now())
        embed.set_footer(text="Generated by Gemini AI")
        await ctx.send(embed=embed)
        await ctx.send("✅ Devlog generated! React with 📤 to post to #📰-devlogs")

@bot.command(name="ask")
@is_owner()
async def ask_command(ctx, *, question):
    async with ctx.typing():
        response = get_ai_response(question)
        embed = discord.Embed(title="🤖 AI Assistant Response", description=response, color=discord.Color.purple(), timestamp=datetime.now())
        embed.set_footer(text="Powered by Gemini AI")
        await ctx.send(embed=embed)

@bot.command(name="announce")
@is_owner()
async def announce_command(ctx, *, message):
    try:
        guild = bot.get_guild(GUILD_ID)
        if guild:
            channel = discord.utils.get(guild.text_channels, name="🎮-game-updates")
            if channel:
                embed = discord.Embed(title="📢 Announcement", description=message, color=discord.Color.gold(), timestamp=datetime.now())
                embed.set_author(name="OnlyGhost", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
                await channel.send(embed=embed)
                await ctx.send("✅ Announcement posted!")
            else:
                await ctx.send("❌ Could not find #🎮-game-updates channel")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name="update")
@is_owner()
async def update_command(ctx, *, update_info):
    try:
        guild = bot.get_guild(GUILD_ID)
        if guild:
            channel = discord.utils.get(guild.text_channels, name="📰-devlogs")
            if channel:
                embed = discord.Embed(title="🔄 Studio Update", description=update_info, color=discord.Color.blue(), timestamp=datetime.now())
                embed.set_author(name="OnlyGhost", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
                await channel.send(embed=embed)
                await ctx.send("✅ Update posted!")
            else:
                await ctx.send("❌ Could not find #📰-devlogs channel")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name="status")
@is_owner()
async def status_command(ctx):
    try:
        guild = bot.get_guild(GUILD_ID)
        if guild:
            embed = discord.Embed(title="📊 Server Status", color=discord.Color.green(), timestamp=datetime.now())
            embed.add_field(name="Guild", value=guild.name, inline=True)
            embed.add_field(name="Members", value=guild.member_count, inline=True)
            embed.add_field(name="Bot Status", value="🟢 Online", inline=True)
            embed.add_field(name="AI Model", value="Gemini 2.5 Flash Lite", inline=True)
            await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name="help")
@is_owner()
async def help_command(ctx):
    embed = discord.Embed(title="🤖 Bot Commands", description="Available commands for OnlyGhost", color=discord.Color.blue())
    embed.add_field(name="📝 !devlog <info>", value="Generate a devlog from project information", inline=False)
    embed.add_field(name="🤖 !ask <question>", value="Ask the AI assistant anything", inline=False)
    embed.add_field(name="📢 !announce <message>", value="Send announcement to #🎮-game-updates", inline=False)
    embed.add_field(name="🔄 !update <info>", value="Post studio update to #📰-devlogs", inline=False)
    embed.add_field(name="📊 !status", value="Get server and bot status", inline=False)
    embed.set_footer(text="Only available to OnlyGhost | Powered by Gemini AI")
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("❌ You don't have permission to use this command!")
    else:
        await ctx.send(f"❌ Error: {str(error)}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    """Start the bot"""
    if not DISCORD_BOT_TOKEN:
        print("❌ DISCORD_BOT_TOKEN not found in environment!", flush=True)
        return
    
    if not setup_gemini():
        return
    
    print("="*60, flush=True)
    print("🤖 OnlyGhost Discord Bot Initializing...", flush=True)
    print("="*60, flush=True)
    
    try:
        bot.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        print(f"❌ Error starting bot: {e}", flush=True)

if __name__ == "__main__":
    main()