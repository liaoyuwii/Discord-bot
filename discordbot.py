import discord
import os
from discord.utils import get
from PIL import Image
from io import BytesIO

# client是跟discord連接，intents是要求機器人的權限
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
client = discord.Client(intents=intents)

# 這是你設定的管理員角色名稱
ADMIN_ROLE_NAME = "Admin"  # 假設角色名稱為 "Admin"

# 調用event函式庫
@client.event
# 當機器人完成啟動
async def on_ready():
    print(f"目前登入身份 --> {client.user}")

@client.event
# 當頻道有新訊息
async def on_message(message):
    # 排除機器人本身的訊息，避免無限循環
    if message.author == client.user:
        return

    # 新訊息包含Hello，回覆Hello, world!
    if "WiiUpload" in message.content:
        if '檔案名稱' in message.content:
            # 取得檔案名稱
            file_name = message.content.split('檔案名稱:')[1].split('\n')[0].strip()
            os.mkdir("(檔案位置)" + file_name)
            script = message.content.split('描述:')[1].strip()
            # 檢查是否有附件
            c = 0
            if len(message.attachments) > 0:
                for attachment in message.attachments:
                    # 下載圖片到本地
                    print("檔名:", file_name, 'ENDF')
                    await attachment.save(
                        "(檔案位置)" + file_name + "\\" + str(c) + ".png")
                    print("TTTTTT", "(檔案位置)" + file_name + "\\" + str(c) + ".png")
                    c += 1
                    print(f"Saved image {file_name}")
            if len(script) > 0:
                with open(fr"(檔案位置)\{file_name}\{file_name}.txt", 'w') as f:
                    print("描述:", script, "ENDS")
                    f.write("描述:" + script)
            # 上傳成功訊息
            await message.channel.send("上傳成功!")
    if "!找:" in message.content:
        script = message.content.split('!找:')[1].strip()
        print("找檔案:", script)
        embed = discord.Embed(title="Files in directory")

        # 搜尋資料夾內的檔案
        if os.path.isdir(f'(檔案位置)\{script}'):
            files = os.listdir(f'(檔案位置)\{script}')
            for file_namess in files:
                file_path = os.path.join(f'(檔案位置)\{script}', file_namess)
                if ".txt" not in file_namess and os.path.isfile(file_path):
                    # 讀取圖片
                    image = Image.open(file_path)
                    # 生成縮圖
                    thumbnail = image.copy()
                    thumbnail.thumbnail((100, 100))  # 設定縮圖大小
                    # 將縮圖轉換為二進制數據
                    thumbnail_data = BytesIO()
                    thumbnail.save(thumbnail_data, format='PNG')  # 這裡使用 PNG 格式
                    thumbnail_data.seek(0)  # 將指針移回開始

                    # 上傳縮圖到 Discord 伺服器
                    thumbnail_file = discord.File(thumbnail_data, filename='thumbnail.png')

                    # 建立Embed
                    embed.add_field(name=file_namess, value="This is a file", inline=False)
                    embed.set_thumbnail(url=f"attachment://{thumbnail_file.filename}")

                    # 回傳嵌入訊息
                    print("Sending files", embed)
                    await message.channel.send(embed=embed, file=thumbnail_file)
                    embed.clear_fields()
                elif ".txt" in file_namess:
                    with open(file_path, 'r') as f:
                        script_content = f.read()
                    await message.channel.send(script_content)
        else:
            await message.channel.send("找不到指定的資料夾")

    if message.content == '!list_files':
        print("Listing files")
        # 取得伺服器上所有的資料夾
        dirs = [d for d in os.listdir('(檔案位置)') if
                os.path.isdir(os.path.join('(檔案位置)', d))]
        # 建立嵌入
        embed = discord.Embed(title="Directories in pic folder")
        # 加入資料夾列表
        for dir_name in dirs:
            dir_path = os.path.join('(檔案位置)', dir_name)
            embed.add_field(name=dir_name, value="This is a directory", inline=False)

            # 檢查資料夾內是否有圖片
            images = [f for f in os.listdir(dir_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if images:
                image_path = os.path.join(dir_path, images[0])
                image = Image.open(image_path)
                # 生成縮圖
                thumbnail = image.copy()
                thumbnail.thumbnail((100, 100))  # 設定縮圖大小
                # 將縮圖轉換為二進制數據
                thumbnail_data = BytesIO()
                thumbnail.save(thumbnail_data, format='PNG')  # 這裡使用 PNG 格式
                thumbnail_data.seek(0)  # 將指針移回開始

                # 上傳縮圖到 Discord 伺服器
                thumbnail_file = discord.File(thumbnail_data, filename='thumbnail.png')
                embed.set_thumbnail(url=f"attachment://{thumbnail_file.filename}")
                await message.channel.send(embed=embed, file=thumbnail_file)
                embed.clear_fields()
            else:
                await message.channel.send(embed=embed)

    if message.content == '!help':
        help_text = (
            "**!help** - 列出所有指令的使用方法\n"
            "**!list_files** - 列出所有資料夾名稱及其內的第一張圖片的縮圖\n"
            "**!找:<檔案名稱>** - 找出指定資料夾內的所有檔案並生成縮圖\n"
            "**WiiUpload 檔案名稱:<名稱> 描述:<描述>** - 上傳多張圖片並附帶描述"
        )
        await message.channel.send(help_text)

    if message.content.startswith("!admin"):
        if not any(role.permissions.administrator for role in message.author.roles):
            await message.channel.send("您沒有權限使用此指令")
            return

        try:
            member = message.mentions[0]
            role = get(message.guild.roles, name=ADMIN_ROLE_NAME)
            if role:
                await member.add_roles(role)
                await message.channel.send(f"已將 {member.mention} 添加到 {role.name} 角色")
            else:
                await message.channel.send(f"找不到名稱為 {ADMIN_ROLE_NAME} 的角色")
        except IndexError:
            await message.channel.send("請標記要授予管理員角色的用戶")

    if message.content == "!ticket":
        if any(role.permissions.administrator for role in message.author.roles):
            ticket_message = await message.channel.send("點我創建購買表單")
            await ticket_message.add_reaction("🎫")
        else:
            await message.channel.send("您沒有權限使用此指令")


@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    # 假設 "🎫" 是用來創建 ticket 的貼圖
    if str(reaction.emoji) == "🎫":
        guild = reaction.message.guild
        # 創建一個新的文字頻道，名稱格式為 "ticket-<用戶名稱>"
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        # 增加管理員的讀寫權限
        admin_role = get(guild.roles, name=ADMIN_ROLE_NAME)  # 假設管理員角色名稱為 "Admin"
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(f'ticket-{user.name}', overwrites=overwrites)
        ticket_message = await ticket_channel.send(f"Hello {user.mention}, 這裡是你的私人支援頻道。\n要關閉請點下面:x:")
        await ticket_message.add_reaction("❌")

    # 假設 "❌" 是用來刪除 ticket 的貼圖
    if str(reaction.emoji) == "❌":
        if reaction.message.channel.name.startswith("ticket-"):
            await reaction.message.channel.delete()


# Replace these values with your bot's token, channel ID, and the path to the image
token = "(discord bot Token)"
channel_id = "寶可夢Pokemon go 帳號交易平台"

client.run(token)
