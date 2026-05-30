const { Client, GatewayIntentBits, EmbedBuilder, PermissionFlagsBits, ChannelType } = require('discord.js');
const { GoogleGenerativeAI } = require('@google/generative-ai');
require('dotenv').config();
const http = require('http');

// ============================================================================
// CONFIGURATION
// ============================================================================

const OWNER_ID = process.env.OWNER_ID || '581877396584529921';
const GUILD_ID = process.env.GUILD_ID || '1510030141005500626';
const DISCORD_BOT_TOKEN = process.env.DISCORD_BOT_TOKEN;
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

// Studio Rules - Kurallar
const STUDIO_RULES = `
🎮 **STUDIO KURALLAR VE REHBER**

📋 **GENEL KURALLAR:**
1. Saygılı ve profesyonel davran
2. Spam ve flood yapmayın
3. NSFW içerik yasak
4. Reklam ve self-promotion yasak
5. Başkalarını taciz etmeyin

🎨 **STUDIO HAKKINDA:**
- Biz indie game studio'suyuz
- Pixel art ve puzzle oyunları yapıyoruz
- Şu an "Life N Dinos" üzerinde çalışıyoruz
- Topluluk geri bildirimi çok önemli

💬 **CHAT KURALLARI:**
1. Konuya uygun kanallarda yazın
2. Uzun yazılar için thread açın
3. Spoiler içeriği gizleyin
4. Linkler paylaşmadan önce sorun

🤖 **BOT KOMUTLARI:**
- \`/help\` - Tüm komutları göster
- \`/help-ai\` - AI asistantan yardım al
- \`/rules\` - Kuralları göster
- \`/info\` - Studio hakkında bilgi

👥 **ROL SİSTEMİ:**
- 👤 Member - Yeni üyeler
- 🎨 Artist - Sanat ekibi
- 💻 Developer - Geliştirici ekibi
- 🎮 Tester - Test ekibi
- 📢 Moderator - Sunucu yöneticileri

⚠️ **KURALLARI İHLAL ETMEK:**
- 1. İhlal: Uyarı
- 2. İhlal: Mute (1 saat)
- 3. İhlal: Kick
- 4. İhlal: Ban

Sorularınız için \`/help-ai\` kullanın!
`;

const SYSTEM_PROMPT = `You are a helpful Discord bot for a game development studio.

PERSONALITY:
- Professional but friendly
- Helpful and supportive
- Knowledgeable about game development
- Respectful of studio rules

STUDIO INFO:
- Indie game development studio
- Creates pixel art puzzle games
- Current project: Life N Dinos
- Community-focused

RULES TO FOLLOW:
- Be respectful and professional
- No spam or flooding
- No NSFW content
- No advertising
- No harassment
- Follow channel topics
- Use threads for long discussions
- Hide spoilers
- Ask before sharing links

RESPONSE GUIDELINES:
- Be concise and helpful
- Use markdown formatting
- Include relevant emojis
- Provide actionable information
- Ask clarifying questions if needed
- Always be respectful of studio rules`;

// ============================================================================
// DISCORD CLIENT SETUP
// ============================================================================

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.DirectMessages,
  ],
});

// ============================================================================
// GEMINI AI SETUP
// ============================================================================

let genai;

function setupGemini() {
  if (!GEMINI_API_KEY) {
    console.log('❌ GEMINI_API_KEY not found in environment!');
    return false;
  }
  genai = new GoogleGenerativeAI(GEMINI_API_KEY);
  return true;
}

async function getAIResponse(userMessage) {
  try {
    const model = genai.getGenerativeModel({ model: 'gemini-2.5-flash-lite' });
    const result = await model.generateContent(
      `${SYSTEM_PROMPT}\n\nUser: ${userMessage}`
    );
    return result.response.text();
  } catch (error) {
    return `❌ Error: ${error.message}`;
  }
}

// ============================================================================
// WEB SERVER (Keep bot alive on Render)
// ============================================================================

function startWebServer() {
  const server = http.createServer((req, res) => {
    if (req.url === '/') {
      const uptime = Math.floor(process.uptime());
      const hours = Math.floor(uptime / 3600);
      const minutes = Math.floor((uptime % 3600) / 60);
      const seconds = uptime % 60;

      const html = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🤖 Studio Bot Status</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 20px;
    }
    .container {
      background: white;
      border-radius: 15px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
      padding: 40px;
      max-width: 500px;
      width: 100%;
    }
    .header {
      text-align: center;
      margin-bottom: 30px;
    }
    .header h1 {
      font-size: 2.5em;
      color: #667eea;
      margin-bottom: 10px;
    }
    .status-badge {
      display: inline-block;
      background: #10b981;
      color: white;
      padding: 8px 16px;
      border-radius: 20px;
      font-weight: bold;
      font-size: 0.9em;
    }
    .status-badge.offline {
      background: #ef4444;
    }
    .info-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-top: 30px;
    }
    .info-card {
      background: #f3f4f6;
      padding: 20px;
      border-radius: 10px;
      border-left: 4px solid #667eea;
    }
    .info-card h3 {
      color: #667eea;
      font-size: 0.9em;
      text-transform: uppercase;
      margin-bottom: 8px;
      font-weight: 600;
    }
    .info-card p {
      color: #1f2937;
      font-size: 1.3em;
      font-weight: bold;
    }
    .full-width {
      grid-column: 1 / -1;
    }
    .commands {
      margin-top: 30px;
      padding-top: 30px;
      border-top: 2px solid #e5e7eb;
    }
    .commands h3 {
      color: #667eea;
      margin-bottom: 15px;
      font-size: 1.1em;
    }
    .command-list {
      list-style: none;
    }
    .command-list li {
      padding: 8px 0;
      color: #4b5563;
      font-size: 0.95em;
    }
    .command-list li:before {
      content: "⚡ ";
      color: #667eea;
      font-weight: bold;
    }
    .footer {
      text-align: center;
      margin-top: 30px;
      color: #9ca3af;
      font-size: 0.9em;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🤖 Studio Bot</h1>
      <span class="status-badge">🟢 ONLINE</span>
    </div>

    <div class="info-grid">
      <div class="info-card">
        <h3>Guilds</h3>
        <p>${client.guilds.cache.size}</p>
      </div>
      <div class="info-card">
        <h3>Users</h3>
        <p>${client.users.cache.size}</p>
      </div>
      <div class="info-card">
        <h3>Uptime</h3>
        <p>${hours}h ${minutes}m ${seconds}s</p>
      </div>
      <div class="info-card">
        <h3>Ping</h3>
        <p>${client.ws.ping}ms</p>
      </div>
      <div class="info-card full-width">
        <h3>Bot Status</h3>
        <p>✅ All Systems Operational</p>
      </div>
    </div>

    <div class="commands">
      <h3>Available Commands</h3>
      <ul class="command-list">
        <li>/help - Show all commands</li>
        <li>/help-ai - Ask AI about rules</li>
        <li>/rules - Show studio rules</li>
        <li>/info - Studio information</li>
        <li>/assign-role - Assign roles</li>
        <li>/mute - Mute members</li>
        <li>/kick - Kick members</li>
        <li>/ban - Ban members</li>
      </ul>
    </div>

    <div class="footer">
      <p>🎮 Game Development Studio Bot</p>
      <p>Powered by Discord.js & Gemini AI</p>
    </div>
  </div>
</body>
</html>
      `;
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end(html);
    } else if (req.url === '/api/status') {
      const status = {
        status: 'online',
        bot: client.user.tag,
        guilds: client.guilds.cache.size,
        users: client.users.cache.size,
        uptime: process.uptime(),
        ping: client.ws.ping,
        timestamp: new Date().toISOString(),
      };
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(status, null, 2));
    } else {
      res.writeHead(404, { 'Content-Type': 'text/html' });
      res.end('<h1>404 - Not Found</h1>');
    }
  });

  const PORT = process.env.PORT || 8000;
  server.listen(PORT, () => {
    console.log(`🌐 Web server running on port ${PORT}`);
  });
}

// ============================================================================
// BOT EVENTS
// ============================================================================

client.on('ready', () => {
  console.log(`✅ Bot logged in as ${client.user.tag}`);
  console.log(`📊 Watching ${client.guilds.cache.size} guild(s)`);
  client.user.setActivity('🎮 Game Development', { type: 'WATCHING' });
});

client.on('guildMemberAdd', async (member) => {
  try {
    const guild = client.guilds.cache.get(GUILD_ID);
    if (guild) {
      const memberRole = guild.roles.cache.find(r => r.name === '👤 Member');
      if (memberRole) {
        await member.roles.add(memberRole);
        console.log(`✅ Assigned Member role to ${member.user.username}`);

        // Send welcome DM
        try {
          const embed = new EmbedBuilder()
            .setTitle('🦖 Welcome to Our Game Studio!')
            .setDescription('Thanks for joining our community!')
            .setColor('#00ff00')
            .addFields(
              {
                name: '📌 Getting Started',
                value: 'Check out #ℹ️-about-us for server info and #📋-rules for guidelines.',
              },
              {
                name: '🎮 Current Project',
                value: '**Life N Dinos** - A puzzle strategy game about saving dinosaurs!',
              },
              {
                name: '💬 Need Help?',
                value: 'Use `/help-ai` to ask questions about our studio and rules!',
              }
            );
          await member.send({ embeds: [embed] });
        } catch (e) {
          // DM failed, ignore
        }
      }
    }
  } catch (error) {
    console.error('Error in guildMemberAdd:', error);
  }
});

// ============================================================================
// SLASH COMMANDS
// ============================================================================

client.on('interactionCreate', async (interaction) => {
  if (!interaction.isChatInputCommand()) return;

  const { commandName } = interaction;

  try {
    // Help Command
    if (commandName === 'help') {
      const embed = new EmbedBuilder()
        .setTitle('🤖 Bot Commands')
        .setDescription('Available commands for everyone')
        .setColor('#0099ff')
        .addFields(
          {
            name: '📚 `/help`',
            value: 'Show all available commands',
            inline: false,
          },
          {
            name: '🤖 `/help-ai <question>`',
            value: 'Ask AI assistant about studio rules and guidelines',
            inline: false,
          },
          {
            name: '📋 `/rules`',
            value: 'Show studio rules and guidelines',
            inline: false,
          },
          {
            name: '📖 `/info`',
            value: 'Show studio information',
            inline: false,
          },
          {
            name: '👥 `/assign-role <member> <role>`',
            value: 'Assign a role to a member (Moderator only)',
            inline: false,
          },
          {
            name: '🔇 `/mute <member> <duration>`',
            value: 'Mute a member (Moderator only)',
            inline: false,
          },
          {
            name: '🚫 `/kick <member> <reason>`',
            value: 'Kick a member (Moderator only)',
            inline: false,
          },
          {
            name: '⛔ `/ban <member> <reason>`',
            value: 'Ban a member (Moderator only)',
            inline: false,
          },
          {
            name: '📢 `/announce <message>`',
            value: 'Send announcement (Owner only)',
            inline: false,
          },
          {
            name: '🔄 `/update <info>`',
            value: 'Post studio update (Owner only)',
            inline: false,
          }
        )
        .setFooter({ text: 'Use /help-ai for questions about rules' });

      await interaction.reply({ embeds: [embed], ephemeral: true });
    }

    // Help AI Command
    else if (commandName === 'help-ai') {
      const question = interaction.options.getString('question');
      await interaction.deferReply();

      const response = await getAIResponse(question);

      const embed = new EmbedBuilder()
        .setTitle('🤖 AI Assistant Response')
        .setDescription(response)
        .setColor('#9900ff')
        .setFooter({ text: 'Powered by Gemini AI' });

      await interaction.editReply({ embeds: [embed] });
    }

    // Rules Command
    else if (commandName === 'rules') {
      const embed = new EmbedBuilder()
        .setTitle('📋 Studio Rules & Guidelines')
        .setDescription(STUDIO_RULES)
        .setColor('#ff9900')
        .setFooter({ text: 'Follow these rules to keep our community safe and fun!' });

      await interaction.reply({ embeds: [embed], ephemeral: true });
    }

    // Info Command
    else if (commandName === 'info') {
      const embed = new EmbedBuilder()
        .setTitle('🎮 Studio Information')
        .setDescription('Welcome to our game development studio!')
        .setColor('#00ff99')
        .addFields(
          {
            name: '🎨 What We Do',
            value: 'We create indie pixel art puzzle games with creative gameplay.',
          },
          {
            name: '🎮 Current Project',
            value: '**Life N Dinos** - A puzzle strategy game about saving dinosaurs!',
          },
          {
            name: '👥 Team',
            value: 'Artists, Developers, Testers, and Community Members',
          },
          {
            name: '💬 Community',
            value: 'We value feedback and community involvement in our development process.',
          },
          {
            name: '🔗 Links',
            value: 'Check pinned messages for links to our itch.io and other platforms.',
          }
        );

      await interaction.reply({ embeds: [embed], ephemeral: true });
    }

    // Assign Role Command (Moderator only)
    else if (commandName === 'assign-role') {
      if (!interaction.member.permissions.has(PermissionFlagsBits.ManageRoles)) {
        return await interaction.reply({
          content: '❌ You need Manage Roles permission!',
          ephemeral: true,
        });
      }

      const member = interaction.options.getMember('member');
      const roleName = interaction.options.getString('role');
      const guild = interaction.guild;

      const role = guild.roles.cache.find(r => r.name === roleName);

      if (!role) {
        return await interaction.reply({
          content: `❌ Role "${roleName}" not found!`,
          ephemeral: true,
        });
      }

      await member.roles.add(role);

      const embed = new EmbedBuilder()
        .setTitle('✅ Role Assigned')
        .setDescription(`${member.user.username} has been assigned the ${role.name} role`)
        .setColor('#00ff00');

      await interaction.reply({ embeds: [embed] });
    }

    // Mute Command (Moderator only)
    else if (commandName === 'mute') {
      if (!interaction.member.permissions.has(PermissionFlagsBits.ModerateMembers)) {
        return await interaction.reply({
          content: '❌ You need Moderate Members permission!',
          ephemeral: true,
        });
      }

      const member = interaction.options.getMember('member');
      const duration = interaction.options.getInteger('duration');

      await member.timeout(duration * 60 * 1000);

      const embed = new EmbedBuilder()
        .setTitle('🔇 Member Muted')
        .setDescription(`${member.user.username} has been muted for ${duration} minutes`)
        .setColor('#ff9900');

      await interaction.reply({ embeds: [embed] });
    }

    // Kick Command (Moderator only)
    else if (commandName === 'kick') {
      if (!interaction.member.permissions.has(PermissionFlagsBits.KickMembers)) {
        return await interaction.reply({
          content: '❌ You need Kick Members permission!',
          ephemeral: true,
        });
      }

      const member = interaction.options.getMember('member');
      const reason = interaction.options.getString('reason') || 'No reason provided';

      await member.kick(reason);

      const embed = new EmbedBuilder()
        .setTitle('🚫 Member Kicked')
        .setDescription(`${member.user.username} has been kicked\n**Reason:** ${reason}`)
        .setColor('#ff6600');

      await interaction.reply({ embeds: [embed] });
    }

    // Ban Command (Moderator only)
    else if (commandName === 'ban') {
      if (!interaction.member.permissions.has(PermissionFlagsBits.BanMembers)) {
        return await interaction.reply({
          content: '❌ You need Ban Members permission!',
          ephemeral: true,
        });
      }

      const member = interaction.options.getMember('member');
      const reason = interaction.options.getString('reason') || 'No reason provided';

      await member.ban({ reason });

      const embed = new EmbedBuilder()
        .setTitle('⛔ Member Banned')
        .setDescription(`${member.user.username} has been banned\n**Reason:** ${reason}`)
        .setColor('#ff0000');

      await interaction.reply({ embeds: [embed] });
    }

    // Announce Command (Owner only)
    else if (commandName === 'announce') {
      if (interaction.user.id !== OWNER_ID) {
        return await interaction.reply({
          content: '❌ Only the studio owner can use this command!',
          ephemeral: true,
        });
      }

      const message = interaction.options.getString('message');
      const guild = interaction.guild;
      const channel = guild.channels.cache.find(
        c => c.name === '📢-announcements' && c.type === ChannelType.GuildText
      );

      if (!channel) {
        return await interaction.reply({
          content: '❌ Could not find #📢-announcements channel',
          ephemeral: true,
        });
      }

      const embed = new EmbedBuilder()
        .setTitle('📢 Announcement')
        .setDescription(message)
        .setColor('#ffff00')
        .setAuthor({
          name: 'Studio Owner',
          iconURL: interaction.user.avatarURL(),
        })
        .setTimestamp();

      await channel.send({ embeds: [embed] });
      await interaction.reply({
        content: '✅ Announcement posted!',
        ephemeral: true,
      });
    }

    // Update Command (Owner only)
    else if (commandName === 'update') {
      if (interaction.user.id !== OWNER_ID) {
        return await interaction.reply({
          content: '❌ Only the studio owner can use this command!',
          ephemeral: true,
        });
      }

      const info = interaction.options.getString('info');
      const guild = interaction.guild;
      const channel = guild.channels.cache.find(
        c => c.name === '📰-devlogs' && c.type === ChannelType.GuildText
      );

      if (!channel) {
        return await interaction.reply({
          content: '❌ Could not find #📰-devlogs channel',
          ephemeral: true,
        });
      }

      const embed = new EmbedBuilder()
        .setTitle('🔄 Studio Update')
        .setDescription(info)
        .setColor('#0099ff')
        .setAuthor({
          name: 'Studio Owner',
          iconURL: interaction.user.avatarURL(),
        })
        .setTimestamp();

      await channel.send({ embeds: [embed] });
      await interaction.reply({
        content: '✅ Update posted!',
        ephemeral: true,
      });
    }
  } catch (error) {
    console.error('Error handling command:', error);
    await interaction.reply({
      content: `❌ Error: ${error.message}`,
      ephemeral: true,
    });
  }
});

// ============================================================================
// REGISTER SLASH COMMANDS
// ============================================================================

async function registerCommands() {
  try {
    const commands = [
      {
        name: 'help',
        description: 'Show all available commands',
      },
      {
        name: 'help-ai',
        description: 'Ask AI assistant about studio rules and guidelines',
        options: [
          {
            name: 'question',
            description: 'Your question about studio rules or guidelines',
            type: 3,
            required: true,
          },
        ],
      },
      {
        name: 'rules',
        description: 'Show studio rules and guidelines',
      },
      {
        name: 'info',
        description: 'Show studio information',
      },
      {
        name: 'assign-role',
        description: 'Assign a role to a member (Moderator only)',
        options: [
          {
            name: 'member',
            description: 'The member to assign role to',
            type: 9,
            required: true,
          },
          {
            name: 'role',
            description: 'The role name to assign',
            type: 3,
            required: true,
          },
        ],
      },
      {
        name: 'mute',
        description: 'Mute a member (Moderator only)',
        options: [
          {
            name: 'member',
            description: 'The member to mute',
            type: 9,
            required: true,
          },
          {
            name: 'duration',
            description: 'Duration in minutes',
            type: 4,
            required: true,
          },
        ],
      },
      {
        name: 'kick',
        description: 'Kick a member (Moderator only)',
        options: [
          {
            name: 'member',
            description: 'The member to kick',
            type: 9,
            required: true,
          },
          {
            name: 'reason',
            description: 'Reason for kicking',
            type: 3,
            required: false,
          },
        ],
      },
      {
        name: 'ban',
        description: 'Ban a member (Moderator only)',
        options: [
          {
            name: 'member',
            description: 'The member to ban',
            type: 9,
            required: true,
          },
          {
            name: 'reason',
            description: 'Reason for banning',
            type: 3,
            required: false,
          },
        ],
      },
      {
        name: 'announce',
        description: 'Send announcement (Owner only)',
        options: [
          {
            name: 'message',
            description: 'Announcement message',
            type: 3,
            required: true,
          },
        ],
      },
      {
        name: 'update',
        description: 'Post studio update (Owner only)',
        options: [
          {
            name: 'info',
            description: 'Update information',
            type: 3,
            required: true,
          },
        ],
      },
    ];

    await client.application.commands.set(commands);
    console.log('✅ Slash commands registered');
  } catch (error) {
    console.error('Error registering commands:', error);
  }
}

// ============================================================================
// MAIN
// ============================================================================

async function main() {
  if (!DISCORD_BOT_TOKEN) {
    console.log('❌ DISCORD_BOT_TOKEN not found in environment!');
    process.exit(1);
  }

  if (!setupGemini()) {
    process.exit(1);
  }

  console.log('='.repeat(60));
  console.log('🤖 Studio Discord Bot');
  console.log('='.repeat(60));
  console.log(`Owner ID: ${OWNER_ID}`);
  console.log(`Guild ID: ${GUILD_ID}`);
  console.log(`AI Model: Gemini 2.5 Flash Lite`);
  console.log('\n⏳ Starting bot...\n');

  startWebServer();

  client.once('ready', registerCommands);

  await client.login(DISCORD_BOT_TOKEN);
}

main().catch(console.error);
