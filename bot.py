#!/usr/bin/env python3
"""
OnlyGhost Discord Bot - AI-Powered Studio Manager
Handles devlog generation, server management, and community updates
Uses Google Gemini API (Free)
"""
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Render'ın port hatası vermemesi için basit bir web sunucu fonksiyonu
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot aktif!")
        
    def do_HEAD(self):
        # Render'ın kontrol isteklerine (HEAD) 200 OK dönüyoruz
        self.send_response(200)
        self.end_headers()

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# Botunun ana başlama fonksiyonundan hemen ÖNCE bu thread'i başlat:
threading.Thread(target=run_health_check, daemon=True).start()

# ... bot.run(TOKEN) kodların buralarda bir yerde olmalı ...

import discord
from discord.ext import commands, tasks
import os
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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

bot = commands.Bot(command_prefix="!", intents=intents)

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
        print("❌ GEMINI_API_KEY not found in environment!")
        print("   Add it to .env file or set environment variable")
        return False
    
    genai.configure(api_key=GEMINI_API_KEY)
    return True

def generate_devlog(project_info: str) -> str:
    """Generate a devlog using Gemini AI"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        prompt = f"""Generate a professional devlog for this project update:

{project_info}

Format the devlog with:
1. Title (with version)
2. Summary (2-3 sentences)
3. What's New (bullet points)
4. Bug Fixes (if any)
5. Next Steps

Keep it concise and engaging."""
        
        response = model.generate_content(
            f"{SYSTEM_PROMPT}\n\n{prompt}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1024,
            )
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
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=512,
            )
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
    print(f"✅ Bot logged in as {bot.user}")
    print(f"📊 Watching {len(bot.guilds)} guild(s)")
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
                print(f"✅ Assigned Member role to {member.name}")
                
                # Send welcome DM
                try:
                    embed = discord.Embed(
                        title="🦖 Welcome to OnlyGhost's Game Studio!",
                        description="Thanks for joining our community!",
                        color=discord.Color.green()
                    )
                    embed.add_field(
                        name="📌 Getting Started",
                        value="Check out #ℹ️-about-me for server info and #📋-rules for guidelines.",
                        inline=False
                    )
                    embed.add_field(
                        name="🎮 Current Game",
                        value="**Life N Dinos** - A puzzle strategy game about saving dinosaurs!",
                        inline=False
                    )
                    await member.send(embed=embed)
                except:
                    pass
    except Exception as e:
        print(f"❌ Error in on_member_join: {e}")

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
    """Generate a devlog from project information
    
    Usage: !devlog Fixed 6 bugs, added color coding, improved UI
    """
    async with ctx.typing():
        devlog = generate_devlog(project_info)
        
        # Create embed
        embed = discord.Embed(
            title="📝 Generated Devlog",
            description=devlog,
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.set_footer(text="Generated by Gemini AI")
        
        await ctx.send(embed=embed)
        
        # Ask if they want to post it
        await ctx.send("✅ Devlog generated! React with 📤 to post to #📰-devlogs")

@bot.command(name="ask")
@is_owner()
async def ask_command(ctx, *, question):
    """Ask the AI assistant anything
    
    Usage: !ask What should I work on next?
    """
    async with ctx.typing():
        response = get_ai_response(question)
        
        embed = discord.Embed(
            title="🤖 AI Assistant Response",
            description=response,
            color=discord.Color.purple(),
            timestamp=datetime.now()
        )
        embed.set_footer(text="Powered by Gemini AI")
        
        await ctx.send(embed=embed)

@bot.command(name="announce")
@is_owner()
async def announce_command(ctx, *, message):
    """Send an announcement to #🎮-game-updates
    
    Usage: !announce New version released!
    """
    try:
        guild = bot.get_guild(GUILD_ID)
        if guild:
            channel = discord.utils.get(guild.text_channels, name="🎮-game-updates")
            if channel:
                embed = discord.Embed(
                    title="📢 Announcement",
                    description=message,
                    color=discord.Color.gold(),
                    timestamp=datetime.now()
                )
                embed.set_author(name="OnlyGhost", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
                
                await channel.send(embed=embed)
                await ctx.send("✅ Announcement posted!")
            else:
                await ctx.send("❌ Could not find #🎮-game-updates channel")
        else:
            await ctx.send("❌ Could not find guild")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name="update")
@is_owner()
async def update_command(ctx, *, update_info):
    """Post a studio update to #📰-devlogs
    
    Usage: !update Fixed critical bugs, improved performance
    """
    try:
        guild = bot.get_guild(GUILD_ID)
        if guild:
            channel = discord.utils.get(guild.text_channels, name="📰-devlogs")
            if channel:
                embed = discord.Embed(
                    title="🔄 Studio Update",
                    description=update_info,
                    color=discord.Color.blue(),
                    timestamp=datetime.now()
                )
                embed.set_author(name="OnlyGhost", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
                
                await channel.send(embed=embed)
                await ctx.send("✅ Update posted!")
            else:
                await ctx.send("❌ Could not find #📰-devlogs channel")
        else:
            await ctx.send("❌ Could not find guild")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name="notify")
@is_owner()
async def notify_command(ctx, role_name: str, *, message):
    """Notify a specific role
    
    Usage: !notify Developer New build available!
    """
    try:
        guild = bot.get_guild(GUILD_ID)
        if guild:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                embed = discord.Embed(
                    title="🔔 Notification",
                    description=message,
                    color=discord.Color.orange(),
                    timestamp=datetime.now()
                )
                
                # Find a channel to send to
                channel = discord.utils.get(guild.text_channels, name="🗣️-general")
                if channel:
                    await channel.send(f"{role.mention}", embed=embed)
                    await ctx.send(f"✅ Notified {role.name}!")
                else:
                    await ctx.send("❌ Could not find general channel")
            else:
                await ctx.send(f"❌ Role '{role_name}' not found")
        else:
            await ctx.send("❌ Could not find guild")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name="status")
@is_owner()
async def status_command(ctx):
    """Get bot and server status"""
    try:
        guild = bot.get_guild(GUILD_ID)
        if guild:
            embed = discord.Embed(
                title="📊 Server Status",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            
            embed.add_field(name="Guild", value=guild.name, inline=True)
            embed.add_field(name="Members", value=guild.member_count, inline=True)
            embed.add_field(name="Channels", value=len(guild.text_channels), inline=True)
            embed.add_field(name="Roles", value=len(guild.roles), inline=True)
            embed.add_field(name="Bot Status", value="🟢 Online", inline=True)
            embed.add_field(name="AI Model", value="Gemini Pro", inline=True)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Could not find guild")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name="commands")
@is_owner()
async def commands_command(ctx):
    """Show available commands"""
    embed = discord.Embed(
        title="🤖 Bot Commands",
        description="Available commands for OnlyGhost",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📝 !devlog <info>",
        value="Generate a devlog from project information",
        inline=False
    )
    
    embed.add_field(
        name="🤖 !ask <question>",
        value="Ask the AI assistant anything",
        inline=False
    )
    
    embed.add_field(
        name="📢 !announce <message>",
        value="Send announcement to #🎮-game-updates",
        inline=False
    )
    
    embed.add_field(
        name="🔄 !update <info>",
        value="Post studio update to #📰-devlogs",
        inline=False
    )
    
    embed.add_field(
        name="🔔 !notify <role> <message>",
        value="Notify a specific role",
        inline=False
    )
    
    embed.add_field(
        name="📊 !status",
        value="Get server and bot status",
        inline=False
    )
    
    embed.set_footer(text="Only available to OnlyGhost | Powered by Gemini AI")
    
    await ctx.send(embed=embed)

# ============================================================================
# ERROR HANDLING
# ============================================================================

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CheckFailure):
        await ctx.send("❌ You don't have permission to use this command!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument: {error.param.name}")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found! Use !help for available commands")
    else:
        await ctx.send(f"❌ Error: {str(error)}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Start the bot"""
    # Validate configuration
    if not DISCORD_BOT_TOKEN:
        print("❌ DISCORD_BOT_TOKEN not found!")
        print("   Add it to .env file or set environment variable")
        return
    
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not found!")
        print("   Add it to .env file or set environment variable")
        return
    
    # Setup Gemini
    if not setup_gemini():
        return
    
    print("="*60)
    print("🤖 OnlyGhost Discord Bot")
    print("="*60)
    print(f"Owner ID: {OWNER_ID}")
    print(f"Guild ID: {GUILD_ID}")
    print(f"AI Model: Gemini Pro (Free)")
    print("\n⏳ Starting bot...")
    
    try:
        bot.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        print(f"❌ Error starting bot: {e}")

if __name__ == "__main__":
    main()


# ============================================================================
# BOT EVENTS
# ============================================================================

@bot.event
async def on_ready():
    """Bot is ready"""
    print(f"✅ Bot logged in as {bot.user}")
    print(f"📊 Watching {len(bot.guilds)} guild(s)")
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
                print(f"✅ Assigned Member role to {member.name}")
                
                # Send welcome DM
                try:
                    embed = discord.Embed(
                        title="🦖 Welcome to OnlyGhost's Game Studio!",
                        description="Thanks for joining our community!",
                        color=discord.Color.green()
                    )
                    embed.add_field(
                        name="📌 Getting Started",
                        value="Check out #ℹ️-about-me for server info and #📋-rules for guidelines.",
                        inline=False
                    )
                    embed.add_field(
                        name="🎮 Current Game",
                        value="**Life N Dinos** - A puzzle strategy game about saving dinosaurs!",
                        inline=False
                    )
                    await member.send(embed=embed)
                except:
                    pass
    except Exception as e:
        print(f"❌ Error in on_member_join: {e}")

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
    """Generate a devlog from project information
    
    Usage: !devlog Fixed 6 bugs, added color coding, improved UI
    """
    async with ctx.typing():
        devlog = generate_devlog(project_info)
        
        # Create embed
        embed = discord.Embed(
            title="📝 Generated Devlog",
            description=devlog,
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.set_footer(text="Generated by AI Assistant")
        
        await ctx.send(embed=embed)
        
        # Ask if they want to post it
        await ctx.send("✅ Devlog generated! React with 📤 to post to #📰-devlogs")

@bot.command(name="ask")
@is_owner()
async def ask_command(ctx, *, question):
    """Ask the AI assistant anything
    
    Usage: !ask What should I work on next?
    """
    async with ctx.typing():
        response = get_ai_response(question)
        
        embed = discord.Embed(
            title="🤖 AI Assistant Response",
            description=response,
            color=discord.Color.purple(),
            timestamp=datetime.now()
        )
        embed.set_footer(text="Powered by Claude AI")
        
        await ctx.send(embed=embed)

@bot.command(name="announce")
@is_owner()
async def announce_command(ctx, *, message):
    """Send an announcement to #🎮-game-updates
    
    Usage: !announce New version released!
    """
    try:
        guild = bot.get_guild(GUILD_ID)
        if guild:
            channel = discord.utils.get(guild.text_channels, name="🎮-game-updates")
            if channel:
                embed = discord.Embed(
                    title="📢 Announcement",
                    description=message,
                    color=discord.Color.gold(),
                    timestamp=datetime.now()
                )
                embed.set_author(name="OnlyGhost", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
                
                await channel.send(embed=embed)
                await ctx.send("✅ Announcement posted!")
            else:
                await ctx.send("❌ Could not find #🎮-game-updates channel")
        else:
            await ctx.send("❌ Could not find guild")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name="update")
@is_owner()
async def update_command(ctx, *, update_info):
    """Post a studio update to #📰-devlogs
    
    Usage: !update Fixed critical bugs, improved performance
    """
    try:
        guild = bot.get_guild(GUILD_ID)
        if guild:
            channel = discord.utils.get(guild.text_channels, name="📰-devlogs")
            if channel:
                embed = discord.Embed(
                    title="🔄 Studio Update",
                    description=update_info,
                    color=discord.Color.blue(),
                    timestamp=datetime.now()
                )
                embed.set_author(name="OnlyGhost", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
                
                await channel.send(embed=embed)
                await ctx.send("✅ Update posted!")
            else:
                await ctx.send("❌ Could not find #📰-devlogs channel")
        else:
            await ctx.send("❌ Could not find guild")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name="notify")
@is_owner()
async def notify_command(ctx, role_name: str, *, message):
    """Notify a specific role
    
    Usage: !notify Developer New build available!
    """
    try:
        guild = bot.get_guild(GUILD_ID)
        if guild:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                embed = discord.Embed(
                    title="🔔 Notification",
                    description=message,
                    color=discord.Color.orange(),
                    timestamp=datetime.now()
                )
                
                # Find a channel to send to
                channel = discord.utils.get(guild.text_channels, name="🗣️-general")
                if channel:
                    await channel.send(f"{role.mention}", embed=embed)
                    await ctx.send(f"✅ Notified {role.name}!")
                else:
                    await ctx.send("❌ Could not find general channel")
            else:
                await ctx.send(f"❌ Role '{role_name}' not found")
        else:
            await ctx.send("❌ Could not find guild")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name="status")
@is_owner()
async def status_command(ctx):
    """Get bot and server status"""
    try:
        guild = bot.get_guild(GUILD_ID)
        if guild:
            embed = discord.Embed(
                title="📊 Server Status",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            
            embed.add_field(name="Guild", value=guild.name, inline=True)
            embed.add_field(name="Members", value=guild.member_count, inline=True)
            embed.add_field(name="Channels", value=len(guild.text_channels), inline=True)
            embed.add_field(name="Roles", value=len(guild.roles), inline=True)
            embed.add_field(name="Bot Status", value="🟢 Online", inline=True)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Could not find guild")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name="help")
@is_owner()
async def help_command(ctx):
    """Show available commands"""
    embed = discord.Embed(
        title="🤖 Bot Commands",
        description="Available commands for OnlyGhost",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📝 !devlog <info>",
        value="Generate a devlog from project information",
        inline=False
    )
    
    embed.add_field(
        name="🤖 !ask <question>",
        value="Ask the AI assistant anything",
        inline=False
    )
    
    embed.add_field(
        name="📢 !announce <message>",
        value="Send announcement to #🎮-game-updates",
        inline=False
    )
    
    embed.add_field(
        name="🔄 !update <info>",
        value="Post studio update to #📰-devlogs",
        inline=False
    )
    
    embed.add_field(
        name="🔔 !notify <role> <message>",
        value="Notify a specific role",
        inline=False
    )
    
    embed.add_field(
        name="📊 !status",
        value="Get server and bot status",
        inline=False
    )
    
    embed.set_footer(text="Only available to OnlyGhost")
    
    await ctx.send(embed=embed)

# ============================================================================
# ERROR HANDLING
# ============================================================================

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CheckFailure):
        await ctx.send("❌ You don't have permission to use this command!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument: {error.param.name}")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found! Use !help for available commands")
    else:
        await ctx.send(f"❌ Error: {str(error)}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Start the bot"""
    # Get token from environment or ask user
    token = os.getenv("DISCORD_BOT_TOKEN")
    
    if not token:
        print("❌ DISCORD_BOT_TOKEN environment variable not set!")
        print("\nTo set it:")
        print("Windows: set DISCORD_BOT_TOKEN=your_token_here")
        print("Linux/Mac: export DISCORD_BOT_TOKEN=your_token_here")
        return
    
    print("="*60)
    print("🤖 OnlyGhost Discord Bot")
    print("="*60)
    print(f"Owner ID: {OWNER_ID}")
    print(f"Guild ID: {GUILD_ID}")
    print("\n⏳ Starting bot...")
    
    try:
        bot.run(token)
    except Exception as e:
        print(f"❌ Error starting bot: {e}")

if __name__ == "__main__":
    main()
