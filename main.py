import os
import requests
from urllib.parse import quote_plus
from PIL import Image, ImageFont, ImageDraw
import math
import shutil
import json
import discord
import os


def draw_outline_shadow(draw, xy, udlr, text, font, text_colour=(255, 255, 255), shadow_colour=(0, 0, 0)):
    # xy is 2 element tuple == (x,y)
    # udlr is a 4 element tuple == (up, down, left, right)
    udlr = (udlr[0], udlr[1]+.5, udlr[2], udlr[3])
    x, y = xy
    up, down, left, right = udlr
    # sides
    draw.text((x-left, y), text, shadow_colour, font=font)
    draw.text((x+right, y), text, shadow_colour, font=font)
    draw.text((x, y-up), text, shadow_colour, font=font)
    draw.text((x, y+down), text, shadow_colour, font=font)
    # corners
    draw.text((x-left, y-up), text, shadow_colour, font=font)
    draw.text((x-left, y+down), text, shadow_colour, font=font)
    draw.text((x+right, y-up), text, shadow_colour, font=font)
    draw.text((x+right, y+down), text, shadow_colour, font=font)
    # main text
    draw.text((x, y), text, text_colour, font=font)
    return draw


def create_profile_img(api_key, tag):
    league_cups = [399, 499, 599, 799, 999, 1199, 1399, 1599, 1799, 1999, 2199,
                   2399, 2599, 2799, 2999, 3199, 3499, 3799, 4099, 4399, 4699, 4999, 10000000]
    role_dict = {"admin": "Elder", "member": "Member",
                 "coLeader": "Co-leader", "leader": "Leader"}

    api_dom = 'https://api.clashofclans.com/v1/players/'
    headers = {
        'Accept': 'application/json',
        'authorization': 'Bearer ' + api_key
    }

    with open("leagues.json", "w") as fi:
        fi.write(json.dumps(requests.get(
            "https://api.clashofclans.com/v1/leagues", headers=headers).json()))

    player_tag = tag

    encoded_tag = quote_plus(player_tag)
    url = api_dom + encoded_tag
    r = requests.get(url, headers=headers)
    with open("data.json", "w") as fi:
        fi.write(json.dumps(r.json()))
    player_dict = r.json()
    status_code = r.status_code

    # Always included
    account_name = player_dict["name"]
    xp = player_dict["expLevel"]
    tag = player_dict["tag"]
    badges = player_dict["labels"]
    current_trophies = player_dict["trophies"]
    best_trophies = player_dict["bestTrophies"]
    for i, amount in enumerate(league_cups):
        try:
            if amount < best_trophies and best_trophies < league_cups[i+1]:
                index = i+1
        except IndexError:
            index = len(league_cups) - 1
    best_league_badge_url = requests.get("https://api.clashofclans.com/v1/leagues/290000"+(
        str(index) if index > 9 else "0"+str(index)), headers=headers).json()["iconUrls"]["small"]
    with open("best_league_badge.png", "wb") as fi:
        shutil.copyfileobj(requests.get(
            best_league_badge_url, stream=True).raw, fi)
    best_league_badge = Image.open("best_league_badge.png")
    best_league_badge = best_league_badge.resize((125, 125))
    war_stars = player_dict["warStars"]
    troops_donated = player_dict["donations"]
    troops_received = player_dict["donationsReceived"]
    attacks_won = player_dict["attackWins"]
    defenses_won = player_dict["defenseWins"]

    if "clan" in player_dict:
        clan_name = player_dict["clan"]["name"]
        clan_badge_url = player_dict["clan"]["badgeUrls"]["medium"]
        with open("clan_badge.png", "wb") as fi:
            shutil.copyfileobj(requests.get(
                clan_badge_url, stream=True).raw, fi)
        clan_badge = Image.open("clan_badge.png")
        clan_badge = clan_badge.resize((350, 350))
        clan_role = player_dict["role"]

    if "league" in player_dict:
        current_league_badge = Image.open(
            "files/leagues/" + str(player_dict["league"]["id"]) + ".png")
        current_league_badge = current_league_badge.resize((275, 275))
        current_league_name = player_dict["league"]["name"]

    main_blank = Image.open("files/template.jpg")
    main_blank = main_blank.resize((2050, 738))
    draw = ImageDraw.Draw(main_blank)

    white = 255, 255, 255
    black = 0, 0, 0

    # Bottom numbers
    bottom_number_font = ImageFont.truetype(
        "files\\fonts\\CCBackBeat-Light_5.ttf", 30)
    bottom_x = [430, 930, 1410, 1975]
    bottom_y = 685

    numbers = [troops_donated, troops_received, attacks_won, defenses_won]
    for i in range(4):
        width, height = bottom_number_font.getsize(str(numbers[i]))
        x = bottom_x[i] - width + (len(str(numbers[i]))/2)*10
        draw.text((x, bottom_y), str(
            numbers[i]), white, font=bottom_number_font)

    # XP Level
    xp_font = ImageFont.truetype("files\\fonts\\Supercell-Magic_5.ttf", 42)
    width, height = xp_font.getsize(str(xp))
    xp_x = 80 - math.floor(width/2)
    draw = draw_outline_shadow(
        draw, (xp_x, 75), (1.5, 5*1.15, 1.5, 2), str(xp), xp_font)

    # Player tag, name
    name_font = ImageFont.truetype("files\\fonts\\Supercell-Magic_5.ttf", 42)
    draw = draw_outline_shadow(
        draw, (155, 30), (1.75, 6.5, 1.75, 2.25), account_name, name_font)
    grey = 200, 200, 200
    tag_font = ImageFont.truetype("files\\fonts\\CCBackBeat-Light_5.ttf", 40)
    draw = draw_outline_shadow(
        draw, (155, 90), (1.7, 5.5, 1.7, 1.7), tag, tag_font, grey)

    # War stars
    war_stars_font = ImageFont.truetype(
        "files\\fonts\\Supercell-Magic_5.ttf", 36)
    draw = draw_outline_shadow(
        draw, (1670, 530), (2.5, 7, 2.5, 2.5), str(war_stars), war_stars_font)

    # Trophies
    # Current
    current_trophies_font = ImageFont.truetype(
        "files\\fonts\\Supercell-Magic_5.ttf", 50)
    draw = draw_outline_shadow(draw, (1720, 175), (3, 9, 3, 3), str(
        current_trophies), current_trophies_font)
    # Best
    best_trophies_font = ImageFont.truetype(
        "files\\fonts\\Supercell-Magic_5.ttf", 36)
    draw = draw_outline_shadow(draw, (1680, 365), (2, 6, 2, 2), str(
        best_trophies), best_trophies_font)

    # Labels
    for i, badge in enumerate(badges):
        with open("badge.png", "wb") as fi:
            shutil.copyfileobj(requests.get(
                badge["iconUrls"]["medium"], stream=True).raw, fi)
        badge_img = Image.open("badge.png")
        main_blank.paste(badge_img, (29+(157*i), 216), badge_img)

    # Best league badge
    best_league_y = 335
    if index == 22:
        best_league_y -= 15
    main_blank.paste(best_league_badge,
                     (1500, best_league_y), best_league_badge)

    # League name
    if not "league" in player_dict:
        current_league_name = "Unranked"
    lt_font = ImageFont.truetype("files\\fonts\\Supercell-Magic_5.ttf", 29)
    draw = draw_outline_shadow(
        draw, (1600, 100), (1, 5, 1, 1), current_league_name, lt_font)

    # Clan name
    if not "clan" in player_dict:
        clan_name = "No clan"
    clanname_font = ImageFont.truetype(
        "files\\fonts\\Supercell-Magic_5.ttf", 30)
    clanname_x = 1065 - (len(clan_name)/2)*21
    draw = draw_outline_shadow(
        draw, (clanname_x, 30), (1.2, 5, 1.2, 1.2), clan_name, clanname_font)

    if "clan" in player_dict:
        # Clan badge
        main_blank.paste(clan_badge, (905, 115), clan_badge)

        # Clan role
        role_img = Image.open("files\\role\\"+role_dict[clan_role]+".png")
        role_img = role_img.resize(
            (int(role_img.size[0]*1.2), int(role_img.size[1]*1.2)))
        main_blank.paste(role_img, box=(150, 145))

    if "league" in player_dict:
        # Current badge
        main_blank.paste(current_league_badge,
                         (1330, 20), current_league_badge)

    main_blank.save("out.jpg", "JPEG")


# Permissions int = 44032
API_KEY = "" # https://developer.clashofclans.com/#/
TOKEN = "" # bot token from the dev portal
PREFIX = ">"

client = discord.Client()


@client.event
async def on_ready():
    print('Ready')


@client.event
async def on_message(message: discord.Message):
    await client.wait_until_ready()
    if message.content.startswith(PREFIX + "nimage"):
        args = message.content.split(" ")
        if len(args) < 2:
            await message.channel.send("Please provide a player tag!")
            return
        if len(args) > 2:
            await message.channel.send("Too many arguments!")
            return
        create_profile_img(API_KEY, args[1])
        await message.channel.send(file=discord.File("out.jpg"))

client.run(TOKEN)
