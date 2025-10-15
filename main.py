import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

intents = discord.Intents.default()
intents.members = True
intents.messages = True

CHANNEL_ID = 1427685251135569950  # Replace with your default channel ID
MESSAGE_ID_FILE = "message_id.txt"  # Persistent embed message ID
ALLY_LIST_FILE = "ally_list.txt"    # Persistent Ally stack
ENEMIES_LIST_FILE = "enemies_list.txt"  # Persistent Enemies stack

# Replace with Luna's Discord ID
ALLOWED_USER_ID = 1372549650225168436

class StatusBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="?", intents=intents)
        self.ally_list = []      # Ally stack in memory
        self.enemies_list = []   # Enemies stack in memory

    async def on_ready(self):
        print("Bot is ready!")

        # Load Ally list from file
        if os.path.exists(ALLY_LIST_FILE):
            with open(ALLY_LIST_FILE, "r") as f:
                self.ally_list = [line.strip() for line in f.readlines()]

        # Load Enemies list from file
        if os.path.exists(ENEMIES_LIST_FILE):
            with open(ENEMIES_LIST_FILE, "r") as f:
                self.enemies_list = [line.strip() for line in f.readlines()]

        # Load or create persistent embed message
        bot_message_id = None
        if os.path.exists(MESSAGE_ID_FILE):
            with open(MESSAGE_ID_FILE, "r") as f:
                bot_message_id = int(f.read().strip())

        channel = self.get_channel(CHANNEL_ID)
        if not channel:
            channel = await self.fetch_channel(CHANNEL_ID)

        if not bot_message_id:
            embed = discord.Embed(title="Status Board", color=discord.Color.blue())
            ally_content = "\n".join(f"- {entry}" for entry in self.ally_list) or "*(empty)*"
            enemies_content = "\n".join(f"- {entry}" for entry in self.enemies_list) or "*(empty)*"
            embed.add_field(name="Ally", value=ally_content, inline=False)
            embed.add_field(name="Enemies", value=enemies_content, inline=False)
            msg = await channel.send(embed=embed)
            bot_message_id = msg.id
            with open(MESSAGE_ID_FILE, "w") as f:
                f.write(str(bot_message_id))
            print(f"Persistent embed sent with ID: {bot_message_id}")
        else:
            print(f"Found existing persistent message ID: {bot_message_id}")

        self.bot_message_id = bot_message_id

        # Sync slash commands globally
        synced = await self.tree.sync()
        print(f"Synced {len(synced)} global command(s)")

        # Update embed to reflect current lists
        await self.update_embed()

    async def update_embed(self):
        """Update the persistent embed message with current Ally and Enemies stacks."""
        channel = self.get_channel(CHANNEL_ID)
        if not channel:
            channel = await self.fetch_channel(CHANNEL_ID)

        message = await channel.fetch_message(self.bot_message_id)

        embed = discord.Embed(title="Status Board", color=discord.Color.blue())
        ally_content = "\n".join(f"- {entry}" for entry in self.ally_list) or "*(empty)*"
        enemies_content = "\n".join(f"- {entry}" for entry in self.enemies_list) or "*(empty)*"
        embed.add_field(name="Ally", value=ally_content, inline=False)
        embed.add_field(name="Enemies", value=enemies_content, inline=False)

        await message.edit(embed=embed)

        # Save lists to files for persistence
        with open(ALLY_LIST_FILE, "w") as f:
            for entry in self.ally_list:
                f.write(f"{entry}\n")
        with open(ENEMIES_LIST_FILE, "w") as f:
            for entry in self.enemies_list:
                f.write(f"{entry}\n")


bot = StatusBot()


# -------- Ally commands --------
@bot.tree.command(name="add_ally", description="Exclusive for Luna")
async def add_ally(interaction: discord.Interaction, entry: str):
    if interaction.user.id != ALLOWED_USER_ID:
        await interaction.response.send_message("❌ You are not allowed to update Ally.", ephemeral=True)
        return

    bot.ally_list.append(entry)
    await bot.update_embed()
    await interaction.response.send_message(f"✅ Added to Ally: {entry}", ephemeral=True)


@bot.tree.command(name="remove_ally", description="Exclusive for Luna")
async def remove_ally(interaction: discord.Interaction, entry: str):
    if interaction.user.id != ALLOWED_USER_ID:
        await interaction.response.send_message("❌ You are not allowed to remove Ally entries.", ephemeral=True)
        return

    if entry in bot.ally_list:
        bot.ally_list.remove(entry)
        await bot.update_embed()
        await interaction.response.send_message(f"✅ Removed from Ally: {entry}", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Entry not found: {entry}", ephemeral=True)


@bot.tree.command(name="show_ally", description="Shows When Dawn Reaches Dusk Allies")
async def show_ally(interaction: discord.Interaction):
    content = "\n".join(f"- {entry}" for entry in bot.ally_list) or "*(empty)*"
    embed = discord.Embed(title="Ally", description=content, color=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)


# -------- Enemies commands --------
@bot.tree.command(name="add_enemies", description="Exclusive for Luna")
async def add_enemies(interaction: discord.Interaction, entry: str):
    if interaction.user.id != ALLOWED_USER_ID:
        await interaction.response.send_message("❌ You are not allowed to update Enemies.", ephemeral=True)
        return

    bot.enemies_list.append(entry)
    await bot.update_embed()
    await interaction.response.send_message(f"✅ Added to Enemies: {entry}", ephemeral=True)


@bot.tree.command(name="remove_enemies", description="Exclusive for Luna")
async def remove_enemies(interaction: discord.Interaction, entry: str):
    if interaction.user.id != ALLOWED_USER_ID:
        await interaction.response.send_message("❌ You are not allowed to remove Enemies entries.", ephemeral=True)
        return

    if entry in bot.enemies_list:
        bot.enemies_list.remove(entry)
        await bot.update_embed()
        await interaction.response.send_message(f"✅ Removed from Enemies: {entry}", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Entry not found: {entry}", ephemeral=True)


@bot.tree.command(name="show_enemies", description="Shows When Dawn Reaches Dusk Enemies")
async def show_enemies(interaction: discord.Interaction):
    content = "\n".join(f"- {entry}" for entry in bot.enemies_list) or "*(empty)*"
    embed = discord.Embed(title="Enemies", description=content, color=discord.Color.red())
    await interaction.response.send_message(embed=embed, ephemeral=True)


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
