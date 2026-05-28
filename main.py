import os
import json
import re
from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Load .env file configurations
load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

# Setup Bot Intents
# --- UPDATE INTENTS INITIALIZATION ---
intents = discord.Intents.default()
intents.message_content = True  # Allows reading message content/history for cleanup
intents.members = True          # Allows managing server roles seamlessly

bot = commands.Bot(command_prefix="!", intents=intents)

STAFFS_FILE = "staffs.json"

def load_staffs():
    """Loads the core staff configuration file as a unified dictionary object."""
    default_structure = {
        "resultsChannelId": None,
        "testerRoleId": None
    }
    
    if not os.path.exists(STAFFS_FILE):
        with open(STAFFS_FILE, "w") as f:
            json.dump(default_structure, f, indent=4)
        return default_structure
        
    with open(STAFFS_FILE, "r") as f:
        try:
            data = json.load(f)
            # Automatic database type repair if file was previously a list
            if isinstance(data, list):
                with open(STAFFS_FILE, "w") as wf:
                    json.dump(default_structure, wf, indent=4)
                return default_structure
            
            # Missing key migration pass
            if "testerRoleId" not in data:
                data["testerRoleId"] = None
                with open(STAFFS_FILE, "w") as wf:
                    json.dump(data, wf, indent=4)
                    
            return data
        except json.JSONDecodeError:
            with open(STAFFS_FILE, "w") as wf:
                json.dump(default_structure, wf, indent=4)
            return default_structure

def save_staffs(data):
    """Writes updated dictionary configurations back to disk."""
    with open(STAFFS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_testers():
    """
    TRICK SYSTEM: Reads from the new staffs.json structure but outputs a list.
    Keeps your unchanged 'if r in allowed_testers' command guards 100% functional.
    """
    staffs_data = load_staffs()
    role_id = staffs_data.get("testerRoleId")
    return [role_id] if role_id else []

TIERS_FILE = "tiers.json"

def load_tiers():
    if not os.path.exists(TIERS_FILE):
        # Default initialization map template
        default_structure = {
            "HT1": None, "LT1": None, "HT2": None, "LT2": None,
            "HT3": None, "LT3": None, "HT4": None, "LT4": None,
            "HT5": None, "LT5": None
        }
        with open(TIERS_FILE, "w") as f:
            json.dump(default_structure, f, indent=4)
        return default_structure
        
    with open(TIERS_FILE, "r") as f:
        return json.load(f)

def save_tiers(data):
    with open(TIERS_FILE, "w") as f:
        json.dump(data, f, indent=4)

PROFILE_FILE = "profiles.json"

def load_profiles():
    if not os.path.exists(PROFILE_FILE):
        return {}
    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_profile(user_id, data):
    profiles = load_profiles()
    profiles[str(user_id)] = data
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=4, ensure_ascii=False)

DATA_FILE = "gamemodes.json"

def load_gamemodes():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_gamemodes(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Failed to save gamemodes file: {e}")


# Regex patterns to validate custom Discord emojis <:name:id> or basic unicode emojis
CUSTOM_EMOJI_REGEX = re.compile(r"<a?:[a-zA-Z0-9_]+:[0-9]+>")

def is_valid_emoji(text: str) -> bool:
    # Quick structural check for custom server emojis or basic length validation
    if CUSTOM_EMOJI_REGEX.match(text):
        return True
    # Basic fall-back for standard Unicode emojis (usually small strings)
    if len(text) <= 4: 
        return True
    return False

@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user.name}")
    
    gamemodes_data = load_gamemodes()
    valid_modes = {k: v for k, v in gamemodes_data.items() if "roleId" in v and "channelId" in v}
    bot.add_view(PersistentQueueView(valid_modes))
    bot.add_view(LiveQueueButtons(""))
    print(f"💾 Restored active persistent view listeners with {len(valid_modes)} gamemodes.")
    bot.add_view(TicketControlView("")) 
    print("🔘 Registered persistent ticket control view buttons.")

    try:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        print(f"✅ Synced commands to Guild {GUILD_ID}")
    except Exception as e:
        print(f"❌ Sync failed: {e}")

# --- COMMAND 1: /tiertest ---
@bot.tree.command(name="tiertest", description="Check a player's Minecraft tier testing status")
@app_commands.describe(username="The Minecraft IGN to look up")
async def tiertest(interaction: discord.Interaction, username: str):
    await interaction.response.send_message(
        f"🔍 Looking up **{username}** in the tier database... (Logic comes later!)"
    )

# --- COMMAND 2: /setupgamemodes ---
@bot.tree.command(name="setupgamemodes", description="Configure your tier testing gamemodes and their icons.")
@app_commands.describe(
    g1="Gamemode 1 name", icon1="Emoji/Icon for Gamemode 1",
    g2="Gamemode 2 name", icon2="Emoji/Icon for Gamemode 2",
    g3="Gamemode 3 name", icon3="Emoji/Icon for Gamemode 3",
    g4="Gamemode 4 name", icon4="Emoji/Icon for Gamemode 4",
    g5="Gamemode 5 name", icon5="Emoji/Icon for Gamemode 5",
    g6="Gamemode 6 name (Optional)", icon6="Emoji/Icon for Gamemode 6 (Optional)",
    g7="Gamemode 7 name (Optional)", icon7="Emoji/Icon for Gamemode 7 (Optional)",
    g8="Gamemode 8 name (Optional)", icon8="Emoji/Icon for Gamemode 8 (Optional)",
    g9="Gamemode 9 name (Optional)", icon9="Emoji/Icon for Gamemode 9 (Optional)",
    g10="Gamemode 10 name (Optional)", icon10="Emoji/Icon for Gamemode 10 (Optional)"
)
async def setupgamemodes(
    interaction: discord.Interaction,
    g1: str, icon1: str,
    g2: str, icon2: str,
    g3: str, icon3: str,
    g4: str, icon4: str,
    g5: str, icon5: str,
    g6: Optional[str] = None, icon6: Optional[str] = None,
    g7: Optional[str] = None, icon7: Optional[str] = None,
    g8: Optional[str] = None, icon8: Optional[str] = None,
    g9: Optional[str] = None, icon9: Optional[str] = None,
    g10: Optional[str] = None, icon10: Optional[str] = None
):
    # Collect arguments into structured tuples
    raw_slots = [
        (g1, icon1), (g2, icon2), (g3, icon3), (g4, icon4), (g5, icon5),
        (g6, icon6), (g7, icon7), (g8, icon8), (g9, icon9), (g10, icon10)
    ]
    
    gamemodes_config = {}

    for name, icon in raw_slots:
        # Skip if optional slots were left empty
        if not name or not icon:
            continue
        
        # Verify icon input safety
        if not is_valid_emoji(icon):
            await interaction.response.send_message(
                f"❌ **`{icon}`** does not look like a valid standard or custom server emoji. Action aborted.",
                ephemeral=True
            )
            return

        # Store using lowered key name for easy database access later
        gamemodes_config[name.lower()] = {
            "displayName": name,
            "icon": icon
        }

    # Save to JSON file
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(gamemodes_config, f, indent=4, ensure_ascii=False)
            
        # Create a clean string output for chat confirmation
        preview = "\n".join([f"{data['icon']} **{data['displayName']}**" for data in gamemodes_config.values()])
        await interaction.response.send_message(
            f"✅ **Gamemodes saved successfully!** Current configuration:\n\n{preview}"
        )
    except Exception as e:
        print(f"File Write Error: {e}")
        await interaction.response.send_message("❌ Failed to save configurations locally.", ephemeral=True)

# --- INTERACTIVE DROP-DOWN STEP FOR ROLES & CHANNELS ---
class RoleSetupView(discord.ui.View):
    def __init__(self, gamemodes_data):
        super().__init__(timeout=180)
        self.gamemodes_data = gamemodes_data
        self.selected_gamemode = None
        
        # Step 1 Dropdown: Gamemodes
        options = [
            discord.SelectOption(label=d["displayName"], value=k, emoji=d["icon"])
            for k, d in gamemodes_data.items()
        ]
        self.gamemode_select = discord.ui.Select(
            placeholder="Step 1: Choose a Minecraft gamemode...",
            options=options,
            custom_id="gm_select"
        )
        self.gamemode_select.callback = self.gamemode_callback
        self.add_item(self.gamemode_select)

        # Step 2 Dropdown: Roles (Initially hidden/disabled)
        self.role_select = discord.ui.RoleSelect(
            placeholder="Step 2: Select the testing/ping role...",
            custom_id="role_select",
            disabled=True
        )
        self.role_select.callback = self.role_callback
        self.add_item(self.role_select)

        # Step 3 Dropdown: Channels (Initially hidden/disabled)
        # Filters to only show standard text channels in the server
        self.channel_select = discord.ui.ChannelSelect(
            placeholder="Step 3: Select the queue text channel...",
            channel_types=[discord.ChannelType.text],
            custom_id="channel_select",
            disabled=True
        )
        self.channel_select.callback = self.channel_callback
        self.add_item(self.channel_select)

    async def gamemode_callback(self, interaction: discord.Interaction):
        self.selected_gamemode = self.gamemode_select.values[0]
        self.role_select.disabled = False  # Unlock roles
        
        name = self.gamemodes_data[self.selected_gamemode]['displayName']
        await interaction.response.edit_message(
            content=f"🎯 **Mode chosen: {name}**\nNext, pick the designated tier role below:",
            view=self
        )

    async def role_callback(self, interaction: discord.Interaction):
        chosen_role = self.role_select.values[0]
        self.gamemodes_data[self.selected_gamemode]["roleId"] = chosen_role.id
        
        self.channel_select.disabled = False  # Unlock channels
        
        await interaction.response.edit_message(
            content=f"🔒 **Role Saved:** {chosen_role.mention}\nFinal Step: Choose the dedicated channel for queue actions:",
            view=self
        )

    async def channel_callback(self, interaction: discord.Interaction):
        chosen_channel = self.channel_select.values[0]
        self.gamemodes_data[self.selected_gamemode]["channelId"] = chosen_channel.id
        
        # Commit full payload to file
        save_gamemodes(self.gamemodes_data)
        
        # Clean up view state
        for item in self.children:
            item.disabled = True

        gm = self.gamemodes_data[self.selected_gamemode]
        await interaction.response.edit_message(
            content=f"✅ **Configuration Complete!**\n{gm['icon']} **{gm['displayName']}** sessions are bound to {chosen_channel.mention} using notifications via <@&{gm['roleId']}>.",
            view=self
        )

class TicketQueueDropdown(discord.ui.Select):
    def __init__(self):
        # Starts clean with no arguments, keeping it fully persistent compatible
        super().__init__(
            placeholder="🏆 Select a gamemode to start tier testing...",
            min_values=1,
            max_values=1,
            custom_id="persistent_queue_select_dropdown"
        )

    async def callback(self, interaction: discord.Interaction):
        profiles = load_profiles()
        user_id_str = str(interaction.user.id)
        
        if user_id_str not in profiles:
            await interaction.response.send_message(
                content="❌ **Profile Configuration Missing!**\nYou must setup your player identity details before joining a tier testing group.",
                view=CompleteRegistrationView(),
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)
        
        gamemodes_data = load_gamemodes()
        selected_key = self.values[0]
        
        if selected_key not in gamemodes_data:
            await interaction.followup.send("❌ This gamemode option is no longer active.", ephemeral=True)
            return
            
        config = gamemodes_data[selected_key]
        guild = interaction.guild
        member = interaction.user
        user_profile = profiles[user_id_str]
        
        role = guild.get_role(config.get("roleId"))
        target_channel = guild.get_channel(config.get("channelId"))
        
        if not role or not target_channel:
            await interaction.followup.send("❌ Error: Gamemode configuration broken (Missing role or channel).", ephemeral=True)
            return

        try:
            if role not in member.roles:
                await member.add_roles(role)
                
            await target_channel.set_permissions(member, read_messages=True, send_messages=True, view_channel=True)
            
            history = [msg async for msg in target_channel.history(limit=5)]
            has_embed = any(len(m.embeds) > 0 for m in history if m.author == interaction.client.user)
            
            if not has_embed:
                closed_embed = discord.Embed(
                    title=f"🛑 {config['displayName']} Queue is currently closed",
                    description="This testing session has ended. You will be notified here when a new queue opens.",
                    color=16711680
                )
                await target_channel.send(embed=closed_embed)
                
            await target_channel.send(
                content=f"🔔 **Player Entry:** {member.mention} joined the category! (`{user_profile['username']}` | `{user_profile['region']}` | `{user_profile['accountType']}`)"
            )
            await interaction.followup.send(f"✅ Access granted! Head over to {target_channel.mention}", ephemeral=True)
        except Exception as e:
            print(f"Callback error: {e}")
            await interaction.followup.send("❌ Something went wrong setting up permissions.", ephemeral=True)


class PersistentQueueView(discord.ui.View):
    def __init__(self, gamemodes_data=None):
        super().__init__(timeout=None)
        
        # FIXED: Call it empty, as it expects no arguments now
        dropdown = TicketQueueDropdown()
        
        # Populates the options dynamically if data was supplied by the command
        if gamemodes_data:
            options = [
                discord.SelectOption(label=data["displayName"], value=key, emoji=data["icon"])
                for key, data in gamemodes_data.items() if "roleId" in data and "channelId" in data
            ]
            dropdown.options = options
            
        self.add_item(dropdown)

# Temporary in-memory runtime dictionary tracking active arrays
# Format: { channel_id: [user_id_1, user_id_2] }
ACTIVE_QUEUES = {}
ACTIVE_TICKET_DATA = {}

class LiveQueueButtons(discord.ui.View):
    def __init__(self, gamemode_display_name=""):
        super().__init__(timeout=None)
        self.gamemode_name = gamemode_display_name

    def build_queue_string(self, channel_id):
        user_ids = ACTIVE_QUEUES.get(channel_id, [])
        if not user_ids:
            return "*The queue is currently empty. Be the first to join!*"
        
        return "\n".join([f"**#{index+1}** <@{uid}>" for index, uid in enumerate(user_ids)])

    # Added 'button: discord.ui.Button' parameter here
    @discord.ui.button(label="Join Queue", style=discord.ButtonStyle.success, custom_id="join_queue_btn")
    async def join_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        cid = interaction.channel_id
        uid = interaction.user.id
        
        if cid not in ACTIVE_QUEUES:
            ACTIVE_QUEUES[cid] = []
            
        if uid in ACTIVE_QUEUES[cid]:
            return # User already in line
            
        ACTIVE_QUEUES[cid].append(uid)
        
        embed = interaction.message.embeds[0]
        embed.description = f"Click below to claim your spot in line.\n\nQueue:\n{self.build_queue_string(cid)}"
        
        await interaction.message.edit(embed=embed)

    # Added 'button: discord.ui.Button' parameter here too
    @discord.ui.button(label="Leave Queue", style=discord.ButtonStyle.danger, custom_id="leave_queue_btn")
    async def leave_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        cid = interaction.channel_id
        uid = interaction.user.id
        
        if cid in ACTIVE_QUEUES and uid in ACTIVE_QUEUES[cid]:
            ACTIVE_QUEUES[cid].remove(uid)
            
            embed = interaction.message.embeds[0]
            embed.description = f"Click below to claim your spot in line.\n\nQueue:\n{self.build_queue_string(cid)}"
            await interaction.message.edit(embed=embed)

class TicketControlView(discord.ui.View):
    def __init__(self, gamemode_key):
        super().__init__(timeout=None)
        self.gamemode_key = gamemode_key

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        user_roles = [r.id for r in interaction.user.roles]
        allowed_testers = load_testers()
        is_tester = any(r in allowed_testers for r in user_roles)
        
        if not is_tester and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only authorized testers can manage this test session.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Next Player", style=discord.ButtonStyle.primary, custom_id="ticket_next_player_btn")
    async def next_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        current_channel = interaction.channel
        
        gamemodes_data = load_gamemodes()
        gm = gamemodes_data.get(self.gamemode_key)
        
        if not gm:
            await interaction.followup.send("❌ Error: Gamemode config not found.", ephemeral=True)
            return

        success = await process_next_candidate(interaction, self.gamemode_key, gm)
        
        if success:
            # Clean up our global tracking dictionary safely if it exists
            if current_channel.id in ACTIVE_TICKET_DATA:
                del ACTIVE_TICKET_DATA[current_channel.id]
            await current_channel.delete()

    @discord.ui.button(label="Close Test and Queue", style=discord.ButtonStyle.danger, custom_id="ticket_close_all_btn")
    async def close_all_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        gamemodes_data = load_gamemodes()
        gm = gamemodes_data.get(self.gamemode_key)
        current_channel = interaction.channel
        
        if gm:
            public_channel = interaction.guild.get_channel(gm["channelId"])
            if public_channel:
                async for msg in public_channel.history(limit=15):
                    if msg.author == interaction.client.user:
                        try: await msg.delete()
                        except Exception: pass

                if gm["channelId"] in ACTIVE_QUEUES:
                    del ACTIVE_QUEUES[gm["channelId"]]

                closed_embed = discord.Embed(
                    title=f"🛑 {gm['displayName']} Queue is currently closed",
                    description="This testing session has ended. You will be notified here when a new queue opens.",
                    color=16711680
                )
                await public_channel.send(embed=closed_embed)

        # Clean up our global tracking dictionary safely if it exists
        if current_channel.id in ACTIVE_TICKET_DATA:
            del ACTIVE_TICKET_DATA[current_channel.id]
        await current_channel.delete()

async def process_next_candidate(interaction: discord.Interaction, gm_key, gm):
    guild = interaction.guild
    public_channel_id = gm["channelId"]
    queue_list = ACTIVE_QUEUES.get(public_channel_id, [])

    if not queue_list:
        await interaction.followup.send("ℹ️ The queue is currently empty! No waiting players to pull.", ephemeral=True)
        return False

    target_player_id = queue_list.pop(0)
    ACTIVE_QUEUES[public_channel_id] = queue_list
    
    public_channel = guild.get_channel(public_channel_id)
    if public_channel:
        async for msg in public_channel.history(limit=5):
            if msg.author == interaction.client.user and msg.embeds:
                embed = msg.embeds[0]
                if not queue_list:
                    embed.description = "Click below to claim your spot in line.\n\nQueue:\n*The queue is currently empty. Be the first to join!*"
                else:
                    queue_str = "\n".join([f"**#{idx+1}** <@{uid}>" for idx, uid in enumerate(queue_list)])
                    embed.description = f"Click below to claim your spot in line.\n\nQueue:\n{queue_str}"
                await msg.edit(embed=embed)
                break

    category = discord.utils.get(guild.categories, name="Going Tests")
    if not category:
        await interaction.followup.send("❌ Error: 'Going Tests' category folder not found in server setup.", ephemeral=True)
        return False

    target_member = guild.get_member(target_player_id)
    if not target_member:
        await interaction.followup.send("❌ Candidate player is no longer present in the server.", ephemeral=True)
        return False

    # Permission dictionary setup
    overrides = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        target_member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
    }

    ticket_channel = await guild.create_text_channel(
        name=f"test-{target_member.display_name}",
        category=category,
        overwrites=overrides
    )

    # REGISTER TICKET METADATA INTO MEMORY SLOT
    ACTIVE_TICKET_DATA[ticket_channel.id] = {
        "player_id": target_player_id,
        "gamemode_key": gm_key
    }
    

    profiles = load_profiles()
    prof = profiles.get(str(target_player_id), {"username": "Not Found", "region": "Unknown", "accountType": "Unknown"})

    ticket_embed = discord.Embed(
        title=f"⚔️ Active Testing Session: {gm['displayName']}",
        description=(
            f"**Candidate:** {target_member.mention}\n"
            f"• Minecraft IGN: `{prof['username']}`\n"
            f"• Region: `{prof['region']}`\n"
            f"• Client Account: `{prof['accountType']}`\n\n"
            "Staff can evaluate skills here. Use the utility controls below to cycle positions."
        ),
        color=3447003
    )
    
    await ticket_channel.send(content=f"{interaction.user.mention} 🤝 {target_member.mention}", embed=ticket_embed, view=TicketControlView(gm_key))
    return True


# --- STEP B: The Pop-up Text Modal for Username ---
# --- TRACKING ENGINE FOR IN-PROGRESS CONFIGURATIONS ---
# Structure: { user_id: {"region": "Asia", "accountType": "Premium"} }
class RegistrationModal(discord.ui.Modal, title="Account Registration"):
    # Input 1: Minecraft IGN
    ign_input = discord.ui.TextInput(
        label="Minecraft IGN (Username)",
        placeholder="e.g., PotionOfWater",
        required=True,
        min_length=3,
        max_length=16
    )
    
    # Input 2: Region
    region_input = discord.ui.TextInput(
        label="Region (Type: Asia or Europe)",
        placeholder="Asia / Europe",
        required=True,
        min_length=4,
        max_length=6
    )
    
    # Input 3: Account Type
    type_input = discord.ui.TextInput(
        label="Account Type (Type: Premium or Cracked)",
        placeholder="Premium / Cracked",
        required=True,
        min_length=7,
        max_length=7
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        ign = self.ign_input.value.strip()
        region = self.region_input.value.strip().capitalize()
        acc_type = self.type_input.value.strip().capitalize()

        # Validate inputs cleanly
        if region not in ["Asia", "Europe"]:
            await interaction.followup.send("❌ Invalid Region! Please type exactly `Asia` or `Europe`.", ephemeral=True)
            return
            
        if acc_type not in ["Premium", "Cracked"]:
            await interaction.followup.send("❌ Invalid Account Type! Please type exactly `Premium` or `Cracked`.", ephemeral=True)
            return

        # Save to profiles.json database
        profile_payload = {
            "username": ign,
            "region": region,
            "accountType": acc_type
        }
        save_profile(interaction.user.id, profile_payload)

        await interaction.followup.send(
            content=f"✅ **Profile Registered!**\n• IGN: `{ign}`\n• Region: `{region}`\n• Account: `{acc_type}`\n\nYou can now use the main gamemode dropdown selection again!",
            ephemeral=True
        )

# Simple fallback view containing a single prompt button
class CompleteRegistrationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="📝 Complete Profile Setup", style=discord.ButtonStyle.primary, custom_id="trigger_reg_modal_btn")
    async def open_modal_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Instantly opens the pop-up modal form safely
        await interaction.response.send_modal(RegistrationModal())

class StaffControlView(discord.ui.View):
    def __init__(self, gamemodes_data):
        super().__init__(timeout=300)
        self.gamemodes_data = gamemodes_data
        self.selected_key = None

        options = [
            discord.SelectOption(label=d["displayName"], value=k, emoji=d["icon"])
            for k, d in gamemodes_data.items() if "channelId" in d
        ]
        self.gm_select = discord.ui.Select(
            placeholder="Select a gamemode to manage...",
            options=options,
            custom_id="staff_gm_select"
        )
        self.gm_select.callback = self.dropdown_callback
        self.add_item(self.gm_select)

    async def dropdown_callback(self, interaction: discord.Interaction):
        self.selected_key = self.gm_select.values[0]
        gm = self.gamemodes_data[self.selected_key]
        
        await interaction.response.edit_message(
            content=f"⚙️ Managing: {gm['icon']} **{gm['displayName']}**\nChoose an action below to update its public channel:",
            view=self
        )

    @discord.ui.button(label="Open Queue", style=discord.ButtonStyle.success, row=1)
    async def open_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.selected_key:
            await interaction.response.send_message("❌ Please select a gamemode first!", ephemeral=True)
            return

        await interaction.response.defer()
        gm = self.gamemodes_data[self.selected_key]
        target_channel = interaction.guild.get_channel(gm["channelId"])

        if not target_channel:
            await interaction.followup.send("❌ Target channel not found.", ephemeral=True)
            return

        # Clear old embeds
        async for msg in target_channel.history(limit=15):
            if msg.author == interaction.client.user:
                try: await msg.delete()
                except Exception: pass

        ACTIVE_QUEUES[gm["channelId"]] = []

        # Displays the user display name cleanly inside the open layout
        open_embed = discord.Embed(
            title=f"✅ {gm['displayName']} Tester Available! (Tester: {interaction.user.display_name})",
            description="Click below to claim your spot in line.\n\nQueue:\n*The queue is currently empty. Be the first to join!*",
            color=65386
        )

        await target_channel.send(content="@here ⚡ **The testing queue is now OPEN!**")
        await target_channel.send(embed=open_embed, view=LiveQueueButtons(gm["displayName"]))
        
        await interaction.edit_original_response(content=f"✅ Opened the queue inside {target_channel.mention}!", view=self)

    @discord.ui.button(label="Close Queue", style=discord.ButtonStyle.danger, row=1)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.selected_key:
            await interaction.response.send_message("❌ Please select a gamemode first!", ephemeral=True)
            return

        await interaction.response.defer()
        gm = self.gamemodes_data[self.selected_key]
        target_channel = interaction.guild.get_channel(gm["channelId"])

        if not target_channel:
            await interaction.followup.send("❌ Target channel not found.", ephemeral=True)
            return

        async for msg in target_channel.history(limit=15):
            if msg.author == interaction.client.user:
                try: await msg.delete()
                except Exception: pass

        if gm["channelId"] in ACTIVE_QUEUES:
            del ACTIVE_QUEUES[gm["channelId"]]

        closed_embed = discord.Embed(
            title=f"{gm['displayName']} Queue is currently closed",
            description="This testing session has ended. You will be notified here when a new queue opens.",
            color=16711680
        )
        await target_channel.send(embed=closed_embed)
        
        await interaction.edit_original_response(content=f"🛑 Closed the queue inside {target_channel.mention}!", view=self)

# --- FIX FOR LINE 589 INSIDE YOUR COMMAND ---
@bot.tree.command(name="setup-test-message", description="Deploy the permanent tier testing registration embed.")
async def setup_test_message(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin access denied.", ephemeral=True)
        return
        
    gamemodes_data = load_gamemodes()
    valid_modes = {k: v for k, v in gamemodes_data.items() if "roleId" in v and "channelId" in v}
    
    if not valid_modes:
        await interaction.response.send_message("❌ You haven't fully linked roles or channels via `/setupgameroles` yet!", ephemeral=True)
        return

    embed = discord.Embed(
        title="✨ Minecraft Tier Testing Hub",
        description=(
            "Ready to prove your skills? Select the gamemode you want to be tested in from the dropdown menu below.\n\n"
            "**What happens next?**\n"
            "• You will instantly receive the corresponding ping role.\n"
            "• You will be granted private access to the specific queue channel.\n"
            "• Staff will be pinged automatically to match up against you."
        ),
        color=discord.Color.gold()
    )
    embed.set_footer(text="Make sure your inventory is sorted and you are ready before applying!")

    await interaction.response.send_message("⚙️ Deploying dashboard...", ephemeral=True)
    
    # CHANGE THIS LINE TO USE valid_modes:
    await interaction.channel.send(embed=embed, view=PersistentQueueView(valid_modes))

# --- UPDATE JUST THE COMMAND DEFINITION ---
@bot.tree.command(name="setupgameroles", description="Link testing roles and text channels to gamemodes.")
async def setupgameroles(interaction: discord.Interaction):
    # 1. Immediately defer to stop the 3-second timeout clock (ephemeral keeps it private)
    await interaction.response.defer(ephemeral=True)

    if not interaction.user.guild_permissions.manage_roles:
        await interaction.followup.send("❌ Staff access denied.", ephemeral=True)
        return

    gamemodes_data = load_gamemodes()
    if not gamemodes_data:
        await interaction.followup.send("❌ Initialize your gamemodes using `/setupgamemodes` first.", ephemeral=True)
        return

    # 2. Use followup.send instead of response.send_message
    await interaction.followup.send(
        content="⚙️ **Minecraft Tier Bot — Access Configurator**", 
        view=RoleSetupView(gamemodes_data), 
        ephemeral=True
    )

@bot.tree.command(name="setuptesterrole", description="Configure the official role allowed to manage queues and run test evaluations.")
@discord.app_commands.describe(role="The target role for authorized testers")
async def setuptesterrole_command(interaction: discord.Interaction, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin privileges required.", ephemeral=True)
        return

    staffs_data = load_staffs()
    staffs_data["testerRoleId"] = role.id
    save_staffs(staffs_data)

    await interaction.response.send_message(f"✅ **Tester authority access has been successfully linked to** {role.mention}!", ephemeral=True)

@bot.tree.command(name="openqueue", description="Open or close a specific gamemode testing queue via the staff command hub.")
async def openqueue(interaction: discord.Interaction):
    # Authority Validation Pass
    user_roles = [r.id for r in interaction.user.roles]
    allowed_testers = load_testers()
    
    is_tester = any(r in allowed_testers for r in user_roles)
    if not is_tester and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You are not authorized to manage testing lines.", ephemeral=True)
        return

    gamemodes_data = load_gamemodes()
    valid_modes = {k: v for k, v in gamemodes_data.items() if "channelId" in v}

    if not valid_modes:
        await interaction.response.send_message("❌ No configured gamemodes with text channels found.", ephemeral=True)
        return

    # DO NOT put embeds here! The StaffControlView buttons handle that when clicked.
    await interaction.response.send_message(
        content="🕹️ **Minecraft Testing Command Hub**\nSelect the gamemode you want to toggle:",
        view=StaffControlView(valid_modes),
        ephemeral=True
    )

    # Initialize empty track list
    ACTIVE_QUEUES[interaction.channel_id] = []

    open_embed = discord.Embed(
        title=f"✅ {gm['displayName']} Tester Available! (Tester: {interaction.user.display_name})",
        description="Click below to claim your spot in line.\n\nQueue:\n*The queue is currently empty. Be the first to join!*",
        color=65386 # Lime Green
    )
    
    # Broadcast notice and send live control elements
    await interaction.channel.send(content="@here ⚡ **The testing queue is now OPEN!**")
    await interaction.channel.send(
        embed=open_embed, 
        view=LiveQueueButtons(current_mode["displayName"])
    )

@bot.tree.command(name="closequeue", description="Close the live queue for this specific testing category.")
async def closequeue(interaction: discord.Interaction):
    # 1. Authority Verification Check
    user_roles = [r.id for r in interaction.user.roles]
    allowed_testers = load_testers()
    
    is_tester = any(r in allowed_testers for r in user_roles)
    if not is_tester and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You are not authorized to close queues.", ephemeral=True)
        return

    # 2. Match the current channel to a configured gamemode
    gamemodes_data = load_gamemodes()
    current_mode = None
    for key, data in gamemodes_data.items():
        if data.get("channelId") == interaction.channel_id:
            current_mode = data
            break
            
    if not current_mode:
        await interaction.response.send_message("❌ This text channel is not mapped to an active gamemode framework.", ephemeral=True)
        return

    await interaction.response.defer()

    # 3. Clean up the channel history (Deletes the active queue layout and @here tags)
    async for msg in interaction.channel.history(limit=15):
        if msg.author == interaction.client.user:
            try:
                await msg.delete()
            except Exception:
                pass

    # 4. Wipe the list of active players in memory for this channel
    if interaction.channel_id in ACTIVE_QUEUES:
        del ACTIVE_QUEUES[interaction.channel_id]

    # 5. Send your exact requested Closed Queue Embed layout
    closed_embed = discord.Embed(
        title=f"{current_mode['displayName']} Queue is currently closed",
        description="This testing session has ended. You will be notified here when a new queue opens.",
        color=16711680 # Red
    )
    
    await interaction.channel.send(embed=closed_embed)

@bot.tree.command(name="setuptiersroles", description="Link tier slots directly to their corresponding server roles.")
async def setuptiersroles(
    interaction: discord.Interaction,
    ht1: discord.Role, lt1: discord.Role,
    ht2: discord.Role, lt2: discord.Role,
    ht3: discord.Role, lt3: discord.Role,
    ht4: discord.Role, lt4: discord.Role,
    ht5: discord.Role, lt5: discord.Role
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin privileges required.", ephemeral=True)
        return

    tier_payload = {
        "HT1": ht1.id, "LT1": lt1.id,
        "HT2": ht2.id, "LT2": lt2.id,
        "HT3": ht3.id, "LT3": lt3.id,
        "HT4": ht4.id, "LT4": lt4.id,
        "HT5": ht5.id, "LT5": lt5.id
    }
    
    save_tiers(tier_payload)
    await interaction.response.send_message("✅ **Tier matrix references saved successfully to database configuration!**", ephemeral=True)

@bot.tree.command(name="result", description="Log evaluation scorecard data and update candidate rank status roles.")
@discord.app_commands.describe(
    earned="The rank tier performance achieved (e.g., HT4, LT2)",
    additionalrole="An optional secondary role to grant the candidate"
)
async def result_command(
    interaction: discord.Interaction,
    earned: str,
    additionalrole: discord.Role = None
):
    # 1. Scope Restriction Validation
    if not interaction.channel.category or interaction.channel.category.name != "Going Tests":
        await interaction.response.send_message("❌ This command can only be executed within an active ticket under 'Going Tests'!", ephemeral=True)
        return

    # 2. Verify results channel is configured in staffs.json
    staffs_data = load_staffs()
    results_channel_id = staffs_data.get("resultsChannelId")
    if not results_channel_id:
        await interaction.response.send_message("❌ Configuration missing: Ask an admin to set up the results channel using `/setupresults` first.", ephemeral=True)
        return

    guild = interaction.guild
    results_channel = guild.get_channel(results_channel_id)
    if not results_channel:
        await interaction.response.send_message("❌ Error: The configured results channel could not be found in this server.", ephemeral=True)
        return

    # 3. Extract context metadata mapping from runtime state cache
    ticket_context = ACTIVE_TICKET_DATA.get(interaction.channel.id)
    if not ticket_context:
        await interaction.response.send_message("❌ Could not identify candidate contextual data for this channel room.", ephemeral=True)
        return

    await interaction.response.defer() # Extend interaction timeout threshold

    player_id = ticket_context["player_id"]
    gm_key = ticket_context["gamemode_key"]

    member = guild.get_member(player_id)
    if not member:
        await interaction.followup.send("❌ Candidate member is no longer in this Discord server.", ephemeral=True)
        return

    # Normalize tier selection input format string
    earned_clean = earned.strip().upper()
    tier_config = load_tiers()

    if earned_clean not in tier_config:
        await interaction.followup.send(f"❌ Invalid rank identifier! Use one of the following: `{', '.join(tier_config.keys())}`", ephemeral=True)
        return

    # 4. Retrieve user profiling variables
    profiles = load_profiles()
    gamemodes_data = load_gamemodes()
    
    prof_payload = profiles.get(str(player_id), {"username": "Unknown", "region": "Unknown", "accountType": "Unknown"})
    gm_payload = gamemodes_data.get(gm_key, {"displayName": "Unknown"})

    # Determine Previous Rank state mapping via current roles
    previous_rank = "None"
    for rank_key, role_id in tier_config.items():
        if role_id and member.get_role(role_id):
            previous_rank = rank_key
            break

    # 5. Handle Rank Role Upgrades/Demotions
    # Strip any old tier roles first to prevent overlapping ranks
    for old_role_id in tier_config.values():
        if old_role_id:
            old_role_obj = guild.get_role(old_role_id)
            if old_role_obj and old_role_obj in member.roles:
                try: await member.remove_roles(old_role_obj)
                except Exception: pass

    # Apply the newly earned tier role
    target_role_id = tier_config[earned_clean]
    if target_role_id:
        new_role_obj = guild.get_role(target_role_id)
        if new_role_obj:
            await member.add_roles(new_role_obj)

    # Process any optional secondary role passed into parameter fields
    if additionalrole:
        await member.add_roles(additionalrole)

    # 6. Build and Send the Embed Card
    avatar_url = f"https://mc-heads.net/avatar/{prof_payload['username']}/180.png"

    embed = discord.Embed(
        title=f"{member.name}'s test update 🏆",
        description=(
            f"Tester\n{interaction.user.mention}\n\n"
            f"Minecraft Username\n`{prof_payload['username']}`\n\n"
            f"Gamemode\n`{gm_payload['displayName']}`\n\n"
            f"Type\n`{prof_payload['accountType']}`\n\n"
            f"Previous Rank\n`{previous_rank}`\n\n"
            f"Tier Earned\n`{earned_clean}`\n\n"
            f"Region\n`{prof_payload['region']}`"
        ),
        color=16711680 # Pure Red
    )
    embed.set_thumbnail(url=avatar_url)

    # UPDATED: Broadcast public scorecard log directly to the designated #results channel, pinging the candidate explicitly
    await results_channel.send(content=member.mention, embed=embed)
    
    # Send a receipt confirmation log back to the tester inside the private ticket room
    await interaction.followup.send(f"✅ Test evaluation posted publicly inside {results_channel.mention} and roles successfully adjusted!", ephemeral=True)    

@bot.tree.command(name="setupresults", description="Set the channel where final test results and scorecards will be announced.")
@discord.app_commands.describe(channel="The target text channel for public test updates")
async def setupresults_command(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin privileges required.", ephemeral=True)
        return

    staffs_data = load_staffs()
    staffs_data["resultsChannelId"] = channel.id
    save_staffs(staffs_data)

    await interaction.response.send_message(f"✅ **Public results logging channel has been successfully set to** {channel.mention}!", ephemeral=True)

@bot.tree.command(name="test", description="Pull player #1 out of the current channel queue into an active testing ticket room.")
async def test_command(interaction: discord.Interaction):
    # Authority Validation
    user_roles = [r.id for r in interaction.user.roles]
    allowed_testers = load_testers()
    is_tester = any(r in allowed_testers for r in user_roles)
    
    if not is_tester and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You are not authorized to conduct testing evaluations.", ephemeral=True)
        return

    # Auto detect gamemode mapping based on current channel ID
    gamemodes_data = load_gamemodes()
    current_key = None
    current_mode = None
    
    for key, data in gamemodes_data.items():
        if data.get("channelId") == interaction.channel_id:
            current_key = key
            current_mode = data
            break
            
    if not current_mode:
        await interaction.response.send_message("❌ This command must be executed within an active gamemode queue channel.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    
    # Process the ticket lifecycle
    success = await process_next_candidate(interaction, current_key, current_mode)
    if success:
        await interaction.followup.send("✅ Matchmaker tracking processed. Ticket room created successfully!", ephemeral=True)

# Run the Bot
bot.run(TOKEN)