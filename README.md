# discord-rhythmbox-plugin
A simple plugin for rhythmbox to update your rich presence in discord.
This is based off of the built-in im-status and webremote plugins and has some borrowed code; credit where credit is due!

Note: This plugin does not work with Discord installed via Flatpak.

## Usage

Make a discord app at discord.com/developers

Upload all the images in /icons to the rich presence assets tab

Fill in RPI_APP_ID in discord-status.py with your own application id from 

Fill in RPI_TOKEN with your discord token (google to get an up to date guide)

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

## Album art not showing/wrong picture?

The album art is found by going to the directory of the song playing and getting the first image. 

If there isn't a picture:

Go in to the directory and if there isn't an image, copy the right one from `.cache/rhythmbox/album-art` into your song's directory
(Can't use the art directry from `.cache/rhythmbox/album-art` as there is no documentation on the naming scheme)

If it's the wrong picture:

Make sure that the song is in it's own directory (not `Downloads` or anything) and the only picture in that directory is the album art
