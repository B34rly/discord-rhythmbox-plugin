# discord-rhythmbox-plugin
A simple plugin for rhythmbox to update your rich presence in discord.
This is based off of the built-in im-status plugin and has some borrowed code; credit where credit is due!
Also some code borrowed from https://github.com/fossfreedom/desktop-art/ 

Note: This plugin does not work with Discord installed via Flatpak.

## Usage

Replace the ID in discord-status.py with your own application in discord.com/developers

- Install `pypresence`:
- Install mimetypes
On systems that use python2 and 3:

`pip3 install pypresence
pip3 install mimetypes`

Or if not:
 
`pip install pypresence`
(You can try it with sudo if it does not work)

- Clone the repo:

`git clone https://github.com/ToppleKek/discord-rhythmbox-plugin.git`

- Put the `discord-rhythmbox-plugin` folder in `~/.local/share/rhythmbox/plugins`

- Enable the plugin

Note: Make sure that discord is open when you enable the plugin.
