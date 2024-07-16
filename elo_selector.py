

# Do imports
import os
import sys
import shutil
import tkinter as tk
from cefpython3 import cefpython as cef


# Do local imports
from misc import *


def create_window(lo_players, s_data_type):

    # Get initial player
    i_player_idx = 0
    o_player = lo_players[i_player_idx]

    # Define what to do when scrolling through
    def button_callback(i_idx_delta):

        # Get variables
        nonlocal i_player_idx, o_player

        # Calculate next player index
        i_player_idx = (i_player_idx + i_idx_delta) % len(lo_players)

        # Update player
        o_player = lo_players[i_player_idx]

        # Update content
        content_frame.load(o_player.s_name)

        # Update counter label
        counter_label.config(text=f"{i_player_idx + 1} / {len(lo_players)}")

    # Set up window
    sys.excepthook = cef.ExceptHook
    cef.Initialize()
    root = tk.Tk()
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.title("Review Options!")

    # Create a frame to hold the content frame and the button frames
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    # Create a counter label
    counter_label = tk.Label(main_frame, text="1 / " + str(len(lo_players)), font=("Arial", 12))
    counter_label.pack(side="top", pady=5, fill="x")

    # Create a frame to hold the url/image
    full_content_frame = tk.Frame(main_frame)
    full_content_frame.pack(side="top", fill="both", expand=True)

    # Populate url/image
    if s_data_type == "urls":
        content_frame = BrowserFrame(full_content_frame, o_player.s_name)
    elif s_data_type == "images":
        content_frame = ImageFrame(full_content_frame, o_player.s_name, f_width_coef=1.0)
    content_frame.pack(side="top", fill="both", expand=True)

    # Create a frame to hold the buttons
    button_frame = tk.Frame(main_frame)
    button_frame.pack(side="top", fill="x")

    # Create a subframe for the left button
    left_button_frame = tk.Frame(button_frame)
    left_button_frame.pack(side="left", fill="both", expand=True)

    # Add button to the left
    button1 = tk.Button(left_button_frame, text="    <--    ", command=lambda: button_callback(-1))
    button1.pack(side="top", pady=10)

    # Create a subframe for the right button
    right_button_frame = tk.Frame(button_frame)
    right_button_frame.pack(side="right", fill="both", expand=True)

    # Add button to the right
    button2 = tk.Button(right_button_frame, text="    -->    ", command=lambda: button_callback(1))
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


def main():

    # Define key variables
    s_base_dir = "adventures"
    s_url_file = "urls.txt"
    s_img_dir = "images"

    # Get name of your adventure
    s_adventure = input("\nPlease enter adventure name: ")
    while not any([True for d in os.listdir(s_base_dir) if d == s_adventure]):
        s_adventure = input("\nInput not recognized!\n\nPlease enter adventure name: ")
    s_adventure_dir = os.path.join(s_base_dir, s_adventure)

    # Get URLs or images
    s_url_file = os.path.join(s_base_dir, s_adventure, s_url_file)
    s_img_dir = os.path.join(s_base_dir, s_adventure, s_img_dir)
    if os.path.exists(s_url_file) and not os.path.exists(s_img_dir):
        s_data_type = "urls"
    elif not os.path.exists(s_url_file) and os.path.exists(s_img_dir):
        s_data_type = "images"
    elif os.path.exists(s_url_file) and os.path.exists(s_img_dir):
        s_data_type = input("\nRun on urls or images: ")
        while s_data_type not in ["urls", "images"]:
            s_data_type = input("\nInput not recognized!\n\nRun on urls or images: ")
    else:
        assert False, \
            f"\nError!\tFile {s_url_file} or directory {s_img_dir} must be present in {s_base_dir}/{s_adventure}"

    # Get names of users to optimze for
    ls_rating_files = [os.path.join(s_adventure_dir, f) for f in os.listdir(s_adventure_dir) if f"{s_adventure}__{s_data_type}" in f]
    ls_users_available = [s_rating_file.split(f"{s_data_type}__")[-1].split(".pkl")[0] for s_rating_file in ls_rating_files]
    assert len(ls_users_available) > 0, \
        "\nError!\tNo users available!"

    # Check which users to optimize for
    ls_users = []
    f_continue_message = ""
    while True:
        s_user = input(f"\nEnter user to optimimize from [{', '.join(ls_users_available)}]{f_continue_message}: ")
        if len(ls_users) > 0 and s_user == "":
            break
        elif s_user in ls_users_available:
            ls_users.append(s_user)
            ls_users_available.remove(s_user)
            if len(ls_users_available) == 0:
                break
            f_continue_message = ", or press ENTER"
        else:
            print("\nError!\tUser not recognized!")
    ls_users = sorted(ls_users)

    # Choose selection heuristic
    s_heur = input(f"\nChoose election heuristic from [min, avg, max]: ")
    while s_heur not in ["min", "avg", "max"]:
        s_heur = input(f"\nInput not recognized!\n\nChoose election heuristic from [min, avg, max]: ")

    # Read in data for each user
    lo_players_rated = [pd.read_pickle(os.path.join(s_adventure_dir, f"{s_adventure}__{s_data_type}__{s_user}.pkl")) for s_user in ls_users]
        
    # Apply heuristic and get N best
    lo_players = get_n_best(lo_players_rated, s_heur, i_n_best=None)

    # Open GUI
    create_window(lo_players, s_data_type)

    # Save ranked content    
    if s_data_type == "urls":
        s_url_ranked_file = s_url_file.replace(".txt", f"_ranked__{'_'.join(ls_users)}.txt")
        with open(s_url_ranked_file, 'w') as file:
            for o_player in lo_players:
                file.write(f"{o_player.s_name}\n")
    elif s_data_type == "images":
        s_img_ranked_dir = f"{s_img_dir}_ranked__{'_'.join(ls_users)}"
        if os.path.exists(s_img_ranked_dir):
            shutil.rmtree(s_img_ranked_dir)
        os.makedirs(s_img_ranked_dir)
        for i_rank, o_player in enumerate(tqdm(lo_players, desc="Copying Photos")):
            s_img_path_from = o_player.s_name
            s_img_path_to = os.path.join(s_img_ranked_dir, f"{i_rank+1}__{os.path.basename(s_img_path_from)}")
            shutil.copy2(s_img_path_from, s_img_path_to)


if __name__ == '__main__':
    main()


