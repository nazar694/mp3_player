# Add Library
from tkinter import *
import pygame
import os
from tkinter import filedialog
import time
from mutagen.mp3 import MP3
import tkinter.ttk as ttk


class dirs:
    # Grab the Direction to main file
    direction = os.path.abspath(__file__)
    direction = os.path.dirname(direction)

    # Get Direction
    def getDir(self):
        return self.direction


class MP3Player:
    paused = False
    stopped = False
    song_len = 0

    # Direction to the audio folder
    dir = dirs().getDir()
    base_dir = os.path.join(dir, 'audio')

    # Initialize
    def __init__(self, win):
        # Create window
        win.title('MP3 Player')
        win.iconbitmap(os.path.join(self.dir, r'images\icon.ico'))
        win.geometry("470x370")
        win.resizable(width=False, height=False)

        # Initialize Pygame Mixer
        pygame.mixer.init()

        # Create Master Frame
        self.master_frame = Frame(root)
        self.master_frame.pack(pady=20)

        # Create Playlist Box
        self.song_box = Listbox(self.master_frame, width=60)
        self.song_box.grid(row=0, column=0)

        # Define Player Control Button Images
        self.back_btn_img = PhotoImage(file='images/back.png')
        self.forward_btn_img = PhotoImage(file='images/forward.png')
        self.play_btn_img = PhotoImage(file='images/play.png')
        self.pause_btn_img = PhotoImage(file='images/pause.png')
        self.stop_btn_img = PhotoImage(file='images/stop.png')

        # Create Player Control Frame
        self.controls_frame = Frame(self.master_frame)
        self.controls_frame.grid(row=1, column=0, pady=20)

        # Create Volume Label Frame
        self.volume_frame = LabelFrame(self.master_frame, text="Volume")
        self.volume_frame.grid(row=0, column=1, rowspan=2, padx=40)

        # Create Player Control Buttons
        self.back_button = Button(self.controls_frame, image=self.back_btn_img, borderwidth=0,
                                  command=self.previous_song)
        self.forward_button = Button(self.controls_frame, image=self.forward_btn_img, borderwidth=0,
                                     command=self.next_song)
        self.play_button = Button(self.controls_frame, image=self.play_btn_img, borderwidth=0, command=self.play)
        self.pause_button = Button(self.controls_frame, image=self.pause_btn_img, borderwidth=0, command=self.pause)
        self.stop_button = Button(self.controls_frame, image=self.stop_btn_img, borderwidth=0, command=self.stop)

        self.back_button.grid(row=0, column=0, padx=10)
        self.pause_button.grid(row=0, column=1, padx=10)
        self.play_button.grid(row=0, column=2, padx=10)
        self.stop_button.grid(row=0, column=3, padx=10)
        self.forward_button.grid(row=0, column=4, padx=10)

        # Create Status Bar
        self.status_bar = Label(win, text='00:00/00:00    ', bd=1, relief=GROOVE, anchor=E)
        self.status_bar.pack(fill=X, side=BOTTOM, ipady=2)

        # Create Music Position Slider
        self.song_slider = ttk.Scale(self.master_frame, from_=0, to=100, orient=HORIZONTAL, value=0, command=self.slide,
                                     length=360)
        self.song_slider.grid(row=2, column=0, pady=10)

        # Create Volume Slider
        self.volume_slider = ttk.Scale(self.volume_frame, from_=1, to=0, orient=VERTICAL, value=0.5,
                                       command=self.volume,
                                       length=200)
        self.volume_slider.pack(pady=10)

        # Create Menu
        self.my_menu = Menu(root)
        win.config(menu=self.my_menu)

        # Create Add Song Menu
        self.add_song_menu = Menu(self.my_menu)
        self.my_menu.add_cascade(label="Add Songs", menu=self.add_song_menu)
        self.add_song_menu.add_command(label="Add One Song To Playlist", command=self.add_song)
        self.add_song_menu.add_command(label="Add Many Songs To Playlist", command=self.add_many_songs)

        # Create Delete Song Menu
        self.remove_song_menu = Menu(self.my_menu)
        self.my_menu.add_cascade(label="Remove Songs", menu=self.remove_song_menu)
        self.remove_song_menu.add_command(label="Delete A Song From Playlist", command=self.delete_song)
        self.remove_song_menu.add_command(label="Delete All Songs From Playlist", command=self.delete_all_songs)

    # Grab Song Length Time Info
    def play_time(self):
        # Check for double timing
        if self.stopped:
            return
        # Grab Current Song Elapsed Time
        current_time = pygame.mixer.music.get_pos() / 1000

        # Grab song title from playlist
        song = self.song_box.get(ACTIVE)
        # Add directory structure and mp3 to song title
        song = self.replace(song)
        # Load Song with Mutagen
        song_mut = MP3(song)
        # Get song Length
        self.song_len = song_mut.info.length
        # Convert to Time Format
        converted_song_len = time.strftime('%M:%S', time.gmtime(self.song_len))
        # Increase current time by 1 second
        current_time += 1

        if int(self.song_slider.get()) == int(self.song_len):
            self.status_bar.config(text=f'{converted_song_len}/{converted_song_len}    ')
            self.next_song()

        elif self.paused:
            pass
        elif int(self.song_slider.get()) == int(current_time):
            # Update Slider To position
            slider_position = int(self.song_len)
            self.song_slider.config(to=slider_position, value=int(current_time))

        else:
            # Update Slider To position
            slider_position = int(self.song_len)
            self.song_slider.config(to=slider_position, value=int(self.song_slider.get()))

            # Convert to time format
            converted_current_time = time.strftime('%M:%S', time.gmtime(int(self.song_slider.get())))

            # Output time to status bar
            self.status_bar.config(text=f'{converted_current_time}/{converted_song_len}    ')

            # Move this thing along by one second
            next_time = int(self.song_slider.get()) + 1
            self.song_slider.config(value=next_time)

        # Update time
        self.status_bar.after(1000, self.play_time)

    # Play selected song
    def play(self):
        if self.paused:
            # Unpause
            pygame.mixer.music.unpause()
            self.paused = False
        else:
            # Set Stopped Variable To False So Song Can Play
            self.stopped = False
            song = self.song_box.get(ACTIVE)
            # Add directory structure and mp3 to song title
            song = self.replace(song)

            pygame.mixer.music.load(song)
            pygame.mixer.music.play(loops=0)

            # Call the play_time function to get song length
            self.play_time()

    # Stop Song
    def stop(self):
        # Reset Slider and Status Bar
        self.status_bar.config(text='00:00/00:00    ')
        self.song_slider.config(value=0)
        # Stop Song From Playing
        pygame.mixer.music.stop()
        self.song_box.selection_clear(ACTIVE)

        # Set Stop Variable To True
        self.stopped = True

    # Play The Next Song in the playlist
    def next_song(self):
        # Reset Slider and Status Bar
        self.status_bar.config(text='00:00/00:00    ')
        self.song_slider.config(value=0)

        # Get the current song tuple number
        next_one = self.song_box.curselection()
        # Add one to the current song number
        next_one = next_one[0] + 1
        # Grab song title from playlist
        song = self.song_box.get(next_one)
        # Add directory structure and mp3 to song title
        song = self.replace(song)
        # Load and play song
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(loops=0)

        # Clear active bar in playlist listbox
        self.song_box.selection_clear(0, END)

        # Activate new song bar
        self.song_box.activate(next_one)

        # Set Active Bar to Next Song
        self.song_box.selection_set(next_one, last=None)

    # Play Previous Song In Playlist
    def previous_song(self):
        # Reset Slider and Status Bar
        self.status_bar.config(text='00:00/00:00    ')
        self.song_slider.config(value=0)
        # Get the current song tuple number
        previous_one = self.song_box.curselection()
        # Subtract one from the current song number
        previous_one = previous_one[0] - 1
        # Grab song title from playlist
        song = self.song_box.get(previous_one)
        # Add directory structure and mp3 to song title
        song = self.replace(song)
        # Load and play song
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(loops=0)

        # Clear active bar in playlist listbox
        self.song_box.selection_clear(0, END)

        # Activate new song bar
        self.song_box.activate(previous_one)

        # Set Active Bar to Previous Song
        self.song_box.selection_set(previous_one, last=None)

    # Pause and Unpause The Current Song
    def pause(self):
        if self.paused:
            # Unpause
            pygame.mixer.music.unpause()
            self.paused = False
        else:
            # Pause
            pygame.mixer.music.pause()
            self.paused = True

    # Create slider function
    def slide(self, x):
        song = self.song_box.get(ACTIVE)
        # Add directory structure and mp3 to song title
        song = self.replace(song)

        pygame.mixer.music.load(song)
        pygame.mixer.music.play(loops=0, start=int(self.song_slider.get()))
        x += '0.000000000000000001'

    # Create Volume Function
    def volume(self, x):
        pygame.mixer.music.set_volume(self.volume_slider.get())
        x += '0.000000000000000001'

    # Add Song Function
    def add_song(self):
        song = filedialog.askopenfilename(initialdir='audio/', title="Choose A Song",
                                          filetypes=(("mp3 Files", "*.mp3"),))

        # Strip out the directory info and .mp3 extension from the song name
        song = os.path.basename(song)
        song = song.replace(".mp3", "")
        # Add song to listbox
        self.song_box.insert(END, song)

    # Add many songs to playlist
    def add_many_songs(self):
        songs = filedialog.askopenfilenames(initialdir='audio/', title="Choose A Songs",
                                            filetypes=(("mp3 Files", "*.mp3"),))

        # Loop through song list and replace directory info and mp3
        for song in songs:
            song = os.path.basename(song)
            song = song.replace(".mp3", "")
            # Insert into playlist
            self.song_box.insert(END, song)

    # Delete A Song
    def delete_song(self):
        self.stop()
        # Delete Currently Selected Song
        self.song_box.delete(ANCHOR)
        # Stop Music if it's playing
        pygame.mixer.music.stop()

    # Delete All Songs from Playlist
    def delete_all_songs(self):
        self.stop()
        # Delete All Songs
        self.song_box.delete(0, END)
        # Stop Music if it's playing
        pygame.mixer.music.stop()

    def replace(self, song):
        # Add directory structure and mp3 to song title
        return f'{self.base_dir}/{song}.mp3'


if __name__ == "__main__":
    # Start program
    root = Tk()
    MP3Player(root)
    root.mainloop()
