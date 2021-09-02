import gi
import time
import os
import urllib
import requests
import mimetypes
import base64
import re

gi.require_version('Notify', '0.7')
gi.require_version('Gtk', '3.0')
from gi.repository import Notify, Gtk
from gi.repository import Gio, GLib, GObject, Peas
from gi.repository import RB
from pypresence import Presence
from status_prefs import discord_status_prefs 

#use your own!
RPI_APP_ID = "882453993622740994"


class discord_status_dev(GObject.Object, Peas.Activatable):
  GObject.type_register(discord_status_prefs)
  prefs = discord_status_prefs()
  settings = prefs.load_settings()
  show_notifs = settings["show_notifs"]

  try:
    Notify.init("Rhythmbox")
  except:
    print("Failed to init Notify. Is the notificaion service running?")

  is_streaming = False
  RPC = Presence(RPI_APP_ID)
  connected = False
  gave_up = False
  
  try:
    RPC.connect()
    try:
      if show_notifs:
        Notify.Notification.new("Rhythmbox Discord Status Plugin", "Connected to Discord").show()
        Notify.uninit()
    except:
      print("Failed to init Notify. Is the notificaion service running?")
    connected = True
  except ConnectionRefusedError:
    try:
      if show_notifs:
        Notify.Notification.new("Rhythmbox Discord Status Plugin", "Failed to connect to discord: ConnectionRefused. Is discord open?").show()
        Notify.uninit()
    except:
      print("Failed to init Notify. Is the notificaion service running?")

    if show_notifs:
      while not connected and not gave_up:
        dialog = Gtk.Dialog(title = "Discord Rhythmbox Status Plugin",
                            parent = None,
                            buttons = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                       Gtk.STOCK_OK, Gtk.ResponseType.OK)
                           )

        hbox = Gtk.HBox()

        label = Gtk.Label("\nFailed to connect to the discord client. Make sure that discord is open. Retry?\n")
        hbox.pack_start(label, True, True, 0)

        dialog.vbox.pack_start(hbox, True, True, 0)
        dialog.vbox.show_all()

        response = dialog.run()

        if (response == Gtk.ResponseType.OK):
          try:
            RPC.connect()
            connected = True
          except ConnectionRefusedError:
            print('Failed to retry connection to discord')

        elif (response == Gtk.ResponseType.CANCEL):
          gave_up = True
          dialog.destroy()

        else:
          pass

          dialog.destroy()
  __gtype_name__ = 'DiscordStatusPlugin'
  object = GObject.property(type=GObject.Object)
  start_date = None
  playing_date = None
  is_playing = False
  availableCovers = []

  def __init__ (self):
    GObject.Object.__init__ (self)

  def do_activate(self):
    shell = self.object
    sp = shell.props.shell_player
    self.psc_id  = sp.connect ('playing-song-changed',
                               self.playing_entry_changed)
    self.pc_id   = sp.connect ('playing-changed',
                               self.playing_changed)
    self.ec_id   = sp.connect ('elapsed-changed',
                               self.elapsed_changed)
    self.pspc_id = sp.connect ('playing-song-property-changed',
                               self.playing_song_property_changed)

    self.RPC.update(state="Playback Stopped", details="Rhythmbox Status Plugin", large_image="rhythmbox", small_image="stop", small_text="Stopped")

  def do_deactivate(self):
    shell = self.object
    sp = shell.props.shell_player
    sp.disconnect (self.psc_id)
    sp.disconnect (self.pc_id)
    sp.disconnect (self.ec_id)
    sp.disconnect (self.pspc_id)
    self.RPC.clear(pid=os.getpid())
    self.RPC.close()

  def get_info(self, sp):
      album = None
      title = None
      artist = None
      duration = None

      if not sp.get_playing_entry().get_string(RB.RhythmDBPropType.ALBUM):
        album = 'Unknown'
      else:
        album = sp.get_playing_entry().get_string(RB.RhythmDBPropType.ALBUM)

      if not sp.get_playing_entry().get_string(RB.RhythmDBPropType.TITLE):
        title = 'Unknown'
      else:
        title = sp.get_playing_entry().get_string(RB.RhythmDBPropType.TITLE)

      if not sp.get_playing_entry().get_string(RB.RhythmDBPropType.ARTIST):
        artist = 'Unknown'
      else:
        artist = sp.get_playing_entry().get_string(RB.RhythmDBPropType.ARTIST)

      if not sp.get_playing_entry().get_ulong(RB.RhythmDBPropType.DURATION):
        duration = 0
      else:
        duration = sp.get_playing_entry().get_ulong(RB.RhythmDBPropType.DURATION)
	
      if len(album) < 2:
        album = "%s​" %(album)
        
      return [album, title, artist, duration]
  
  def upload_cover(self, coverName, coverPath, coverListFile, sp):

    #Converts the file:// url of the current song to a readable directory
    coverPath=os.path.dirname(urllib.request.url2pathname(sp.get_playing_entry().get_playback_uri()).replace('file://', ''))
    coverImage = None

    #I yoinked part of this code from https://github.com/fossfreedom/desktop-art/ 
    #It searches the given directory for something with the type of image
    #Then writes it to a file that it's been found
    #Encrypts it with base64 and uploads it to discord

    if os.path.isdir(coverPath):
      print(coverPath)
      for f in os.listdir(coverPath):
          coverImage = os.path.join(coverPath, f)
          mt = mimetypes.guess_type(coverImage)[0]
          if mt and mt.startswith('image/'):
              print("\n \n \n FOUND IMAGE \n \n \n")
              coverListFile.close()
              coverListFile = open(".local/share/rhythmbox/plugins/discord-rhythmbox-plugin/coverLists.txt", "at")

              print(coverImage)
              coverListFile.write(coverName + "\n")
              
              with open(coverImage, "rb") as image:
                print("\n \n \n BASE64 STUFF \n \n \n")
                coverBase64 = base64.b64encode(image.read())
                coverBase64_2 = coverBase64.decode()

                payload = { "name": coverName, "image": "data:image/;base64,"+coverBase64_2}
                print(payload)
                requests.post("https://discordapp.com/api/oauth2/applications/"+RPI_APP_ID+"/assets",data = payload )

                return True
    return False
  
  def get_cover(self, sp):
    
    info = self.get_info(sp)

    coverName = ("%s - %s" %(info[2], info[0])).lower().replace(" ","_")
    coverName = re.sub(r'[^\w]', '_', coverName)
    #This removes all spaces, makes it lowercase and removes symbols to make it fit with discords character limits
    #Some symbols do work but I have no way to differentiate soooo
    print(coverName)
    coverListFile = open(".local/share/rhythmbox/plugins/discord-rhythmbox-plugin/coverLists.txt", "rt")
    coverList = coverListFile.readlines()

    coverPath=os.path.dirname(urllib.request.url2pathname(sp.get_playing_entry().get_playback_uri()).replace('file://', ''))
    

    if coverList != []:
      for i in coverList:
        if i == (coverName+"\n"):
          return coverName
      if self.upload_cover(coverName,coverPath,coverListFile,sp):
        return coverName
      else: 
        return "rhythmbox"
    else:
      if self.upload_cover(coverName,coverPath,coverListFile,sp):
        return coverName
      else: 
        return "rhythmbox"

  def playing_song_property_changed(self, sp, uri, property, old, newvalue):
      print("playing_song_property_changed: %s %s %s %s" %(uri, property, old, newvalue))
      
      info = self.get_info(sp)
      if property == "rb:stream-song-title":
        self.is_streaming = True
        self.update_streaming_rpc(info, newvalue, self.get_cover(sp))

  def update_streaming_rpc(self, info, d, cover):
    self.RPC.update(state=info[1][0:127], details=d[0:127], large_image=cover, small_image="play", small_text="Streaming", start=int(time.time()))

  def playing_entry_changed(self, sp, entry):
    if sp.get_playing_entry():
      self.start_date = int(time.time())
      self.playing_date = self.start_date
      info = self.get_info(sp)
      album = info[0]
      title = info[1]
      artist = info[2]
      duration = info[3]

      cover = self.get_cover(sp)

      if duration == 0 and not self.is_streaming:
        self.update_streaming_rpc(info, "Unknown - Unknown", cover)
      elif duration == 0 and self.is_streaming:
        self.update_streaming_rpc(info, "Unknown - Unknown", cover)
        return
      else:
        self.is_streaming = False

      details="%s - %s" %(title, artist)
      self.is_playing = True

      start_time = int(time.time())
      pos = sp.get_playing_time().time
      end_time = start_time + duration - pos

      self.RPC.update(state=album[0:127], details=details[0:127], large_image=cover, small_image="play", small_text="Playing", start=start_time, end=end_time)

  def playing_changed(self, sp, playing):
    album = None
    title = None
    artist = None
    cover = None
    if sp.get_playing_entry():
      info = self.get_info(sp)
      album = info[0]
      title = info[1]
      artist = info[2]
      duration = info[3]

      cover = self.get_cover(sp)

      if duration == 0 and not self.is_streaming:
        self.update_streaming_rpc(info, "Unknown - Unknown", cover)
      elif duration == 0:
        return
      else:
        self.is_streaming = False

      details="%s - %s" %(title, artist)

      start_time = int(time.time())
      pos = sp.get_playing_time().time
      end_time = start_time + duration - pos

    if playing:
      self.is_playing = True
      self.RPC.update(state=album[0:127], details=details[0:127], large_image=cover, small_image="play", small_text="Playing", start=start_time, end=end_time)
    elif not playing and not sp.get_playing_entry():
      self.is_playing = False
      self.RPC.update(state="Playback Stopped", details="Rhythmbox Status Plugin", large_image="rhythmbox", small_image="stop", small_text="Stopped")
    else:
      self.is_playing = False
      self.RPC.update(state=album[0:127], details=details[0:127], large_image=cover, small_image="pause", small_text="Paused")

  def elapsed_changed(self, sp, elapsed):
    if not self.playing_date or not self.is_playing:
      return
    else:
      self.playing_date += 1
    if self.playing_date - elapsed == self.start_date:
      return
    else:
      if sp.get_playing_entry() and self.is_playing and not elapsed == 0:
        self.playing_date = self.start_date + elapsed
        info = self.get_info(sp)
        album = info[0]
        title = info[1]
        artist = info[2]
        duration = info[3]

        cover = self.get_cover(sp)

        if duration == 0 and not self.is_streaming:
          self.update_streaming_rpc(info, "Unknown - Unknown", cover)
        elif duration == 0:
          return
        else:
          self.is_streaming = False

        details="%s - %s" %(title, artist)

        start_time = int(time.time())
        pos = sp.get_playing_time().time
        end_time = start_time + duration - pos

        self.RPC.update(state=album[0:127], details=details[0:127], large_image=cover, small_image="play", small_text="Playing", start=start_time, end=end_time)
