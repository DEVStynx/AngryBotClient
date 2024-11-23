import requests # dependency

url = "https://discord.com/api/webhooks/1307382500947005561/rumRiU4sS965gLveRdSXPabter_nyVTt-lMiZnK8KzC-DcT-WFV_NoUrx_4-yWoT4S4P" # webhook url, from here: https://i.imgur.com/f9XnAew.png

# for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
data = {
    "content" : "Your mama",
    "username" : "JoMamama"
}

# leave this out if you dont want an embed
# for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
data["embeds"] = [
    {
        "description" : "für Fortnite",
        "title" : "Fortnite"
    }
]

result = requests.post(url, json = data)

try:
    result.raise_for_status()
except requests.exceptions.HTTPError as err:
    print(err)
else:
    print(f"Payload delivered successfully, code {result.status_code}.")

# result: https://i.imgur.com/DRqXQzA.png