

# Do imports
import os
import sys
import tkinter as tk
from cefpython3 import cefpython as cef


# Do local imports
from misc import *


def create_window(lo_players, s_data_type, i_total_iters=None):

    # Define key variables
    if i_total_iters is None:
        i_total_iters = len(lo_players) * 2

    # Get initial players
    o_player_1, o_player_2 = get_players(lo_players)

    # Define what to do when a swipe is made
    def button_callback(o_winner, o_loser):

        # Update elos
        update_elos(o_winner, o_loser)

        # Get two players to compare
        nonlocal o_player_1, o_player_2
        o_player_1, o_player_2 = get_players(lo_players)

        # Update images
        content_frame1.load(o_player_1.s_name)
        content_frame2.load(o_player_2.s_name)

        # Update counter label
        current_index = int(counter_label.cget("text").split("/")[0].strip()) + 1
        counter_label.config(text=f"{current_index} / {i_total_iters}")

        # Check if current_index exceeds total_players
        if current_index > i_total_iters:
            root.destroy()
            return

    # Set up window
    sys.excepthook = cef.ExceptHook
    cef.Initialize()
    root = tk.Tk()
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.title("Compare Options!")

    # Create a frame to hold the content frames and the button frames
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    # Create a counter label
    counter_label = tk.Label(main_frame, text="1 / " + str(i_total_iters), font=("Arial", 12))
    counter_label.pack(side="top", pady=5, fill="x")

    # Create a frame to hold the url/image
    full_content_frame = tk.Frame(main_frame)
    full_content_frame.pack(side="top", fill="both", expand=True)

    # Create a subframe for the left url/image
    left_content_frame = tk.Frame(full_content_frame)
    left_content_frame.pack(side="left", fill="both", expand=True)

    # Populate url/image on the left
    if s_data_type == "urls":
        content_frame1 = BrowserFrame(left_content_frame, o_player_1.s_name)
    elif s_data_type == "images":
        content_frame1 = ImageFrame(left_content_frame, o_player_1.s_name, f_width_coef=0.5)
    content_frame1.pack(side="top", fill="both", expand=True)

    # Create a subframe for the right url/image
    right_content_frame = tk.Frame(full_content_frame)
    right_content_frame.pack(side="right", fill="both", expand=True)

    # Populate url/image on the right
    if s_data_type == "urls":
        content_frame2 = BrowserFrame(right_content_frame, o_player_2.s_name)
    elif s_data_type == "images":
        content_frame2 = ImageFrame(right_content_frame, o_player_2.s_name, f_width_coef=0.5)
    content_frame2.pack(side="top", fill="both", expand=True)

    # Create a frame to hold the buttons
    button_frame = tk.Frame(main_frame)
    button_frame.pack(side="top", fill="x")

    # Create a subframe for the left button
    left_button_frame = tk.Frame(button_frame, width=WIDTH / 2)
    left_button_frame.pack(side="left", fill="both", expand=True)

    # Add button to the left
    button1 = tk.Button(left_button_frame, text="Pick Me!", command=lambda: button_callback(o_player_1, o_player_2))
    button1.pack(side="top", pady=10)

    # Create a subframe for the right button
    right_button_frame = tk.Frame(button_frame, width=WIDTH / 2)
    right_button_frame.pack(side="right", fill="both", expand=True)

    # Add button to the right
    button2 = tk.Button(right_button_frame, text="Pick Me!", command=lambda: button_callback(o_player_2, o_player_1))
    button2.pack(side="top", pady=10)

    # Bind arrow keys to button presses
    root.bind("<Left>", lambda event: button1.invoke())
    root.bind("<Right>", lambda event: button2.invoke())

    # Integrate CEF message loop with Tkinter event loop
    def check_cef_messages():
        cef.MessageLoopWork()
        root.after(10, check_cef_messages)

    # Clean up
    root.after(10, check_cef_messages)
    root.mainloop()
    cef.Shutdown()


if __name__ == "__main__":

    # Define key variables
    s_base_dir = "adventures"
    s_url_file = "urls.txt"
    s_img_dir = "images"

    # Get name of your adventure
    s_adventure = input("\nPlease enter adventure name: ")
    while not any([True for d in os.listdir(s_base_dir) if d == s_adventure]):
        s_adventure = input("\nName not recognized!\n\nPlease enter adventure name: ")
    s_adventure_dir = os.path.join(s_base_dir, s_adventure)

    # Get URLs or images
    s_url_file = os.path.join(s_base_dir, s_adventure, s_url_file)
    s_img_dir = os.path.join(s_base_dir, s_adventure, s_img_dir)
    if os.path.exists(s_url_file) and not os.path.exists(s_img_dir):
        s_data_type = "urls"
        ls_paths = read_urls_from_file(s_url_file)
    elif not os.path.exists(s_url_file) and os.path.exists(s_img_dir):
        s_data_type = "images"
        ls_paths = read_img_from_dir(s_img_dir)
    elif os.path.exists(s_url_file) and os.path.exists(s_img_dir):
        s_data_type = input("\nRun on urls or images: ")
        while s_data_type not in ["urls", "images"]:
            s_data_type = input("\nInput not recognized!\n\nRun on urls or images: ")
        if s_data_type == "urls":
            ls_paths = read_urls_from_file(s_url_file)
        elif s_data_type == "images":
            ls_paths = read_img_from_dir(s_img_dir)
    else:
        assert False, \
            f"\nError!\tFile {s_url_file} or directory {s_img_dir} must be present in {s_base_dir}/{s_adventure}"

    # Get name of user
    s_user = input("\nPlease enter your name: ")

    # Initialize players
    lo_players = [Player(s_path) for s_path in ls_paths]

    # Open GUI
    create_window(lo_players, s_data_type)

    # Save results
    pd.to_pickle(lo_players, os.path.join(s_adventure_dir, f"{s_adventure}__{s_data_type}__{s_user}.pkl"))


