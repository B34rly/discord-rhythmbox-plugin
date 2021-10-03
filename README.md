# discord-rhythmbox-plugin
A simple plugin for rhythmbox to update your rich presence in discord.
This is based off of the built-in im-status and webremote plugins and has some borrowed code; credit where credit is due!

Note: This plugin does not work with Discord installed via Flatpak.

## Installation

- Install `pypresence`

On systems that use python2 and 3:

`pip3 install pypresence`

Or if not:
 
`pip install pypresence`

(You can try it with sudo if it does not work)

- Clone the repo:

`git clone https://github.com/B34rly/discord-rhythmbox-plugin.git`

- Put the `discord-rhythmbox-plugin` folder in `~/.local/share/rhythmbox/plugins`

- Enable the plugin

Note: Make sure that discord is open when you enable the plugin.

## First Time Setup

Make a discord app at discord.com/developers

Upload all the images in /icons to the rich presence assets tab

Fill in RPI_APP_ID in discord-status.py with your own application id from 

Fill in RPI_TOKEN with your discord token (google to get an up to date guide)

## Album art not showing/wrong picture?
The album arts are retrieved directly from the rhythmbox database. If there isn't an album art in rhythmbox, a placeholder will be used as the status image (/icons/unknown)
