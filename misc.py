

# Do imports
import os
import copy
import numpy as np
import pandas as pd
import tkinter as tk
from cefpython3 import cefpython as cef
from PIL import Image, ImageTk
from tqdm import tqdm


# Define global variables
WIDTH = 1200
HEIGHT = 700


class BrowserFrame(tk.Frame):
    def __init__(self, master, url, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.browser = None
        self.url = url
        self.bind("<Configure>", self.on_configure)
        self.bind("<Map>", self.on_map)

    def embed_browser(self):
        window_info = cef.WindowInfo()
        rect = [0, 0, self.winfo_width(), self.winfo_height()]
        window_info.SetAsChild(self.winfo_id(), rect)
        self.browser = cef.CreateBrowserSync(window_info, url=self.url)
        self.on_configure(None)
        self.browser.SetClientHandler(LoadHandler())

    def on_configure(self, event):
        if self.browser:
            self.browser.SetBounds(0, 0, self.winfo_width(), self.winfo_height())

    def on_map(self, event):
        if not self.browser:
            self.embed_browser()

    def load(self, new_url):
        self.browser.LoadUrl(new_url)


class LoadHandler:
    def OnLoadingStateChange(self, browser, is_loading, **_):
        if not is_loading:
            print(f"Page {browser.GetUrl()} loaded successfully!")


class ImageFrame(tk.Frame):
    def __init__(self, master, image_path, f_width_coef, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.image_label = tk.Label(self)
        self.image_label.pack(anchor="center", expand=True)
        self.f_width_coef = f_width_coef
        self.load(image_path)

    def load(self, new_image_path):

        # Open the image
        img = Image.open(new_image_path)

        # Resize the image if needed
        max_width = WIDTH * self.f_width_coef
        max_height = HEIGHT - 100
        width, height = img.size
        if width > max_width or height > max_height:
            img.thumbnail((max_width, max_height))

        # Convert Image object to PhotoImage object for Tkinter
        img_tk = ImageTk.PhotoImage(img)

        # Update the existing label with the new image
        self.image_label.config(image=img_tk)
        self.image_label.image = img_tk


class Player:

    def __init__(self, s_name):
        self.s_name = s_name
        self.f_elo = 1500.0


def get_players(lo_players):

    # Get player elos
    na_elo = np.array([o_player.f_elo for o_player in lo_players])

    # Select a random player
    o_player_1 = np.random.choice(lo_players)

    # Calculate players most similar
    na_selection_coef = 1.0 / (np.abs(na_elo - o_player_1.f_elo) + 1.0)
    na_selection_pct = na_selection_coef / np.sum(na_selection_coef)

    # Select a second player
    while True:
        o_player_2 = np.random.choice(lo_players, p=na_selection_pct)
        if o_player_2 != o_player_1:
            break
    
    # Return
    return o_player_1, o_player_2


def update_elos(o_winner, o_loser):

    # Get elos
    f_winner_elo = o_winner.f_elo
    f_loser_elo = o_loser.f_elo

    # Calculate percent likelihood of victory
    f_winner_exp = 1.0 / (1.0 + (10.0 ** ((f_loser_elo - f_winner_elo) / 400.0)))
    f_loser_exp = 1.0 / (1.0 + (10.0 ** ((f_winner_elo - f_loser_elo) / 400.0)))

    # Calculate updated elos
    f_winner_elo = f_winner_elo + (32.0 * (1.0 - f_winner_exp))
    f_loser_elo = f_loser_elo + (32.0 * (0.0 - f_loser_exp))

    # Update elos
    o_winner.f_elo = f_winner_elo
    o_loser.f_elo = f_loser_elo


def check_convergence_progress(lo_players):

    # Calculate the worst score possible
    f_worst_score = (len(lo_players) ** 2) / 2.0

    # Get players ground truth value ranks
    na_players_gt = pd.Series([int(o_player.s_name) for o_player in lo_players]).rank(method='dense', ascending=True).values

    # Get players elo ranks
    na_players_elo = pd.Series([o_player.f_elo for o_player in lo_players]).rank(method='dense', ascending=True).values

    # Calculate score
    f_score = np.sum(np.abs(na_players_gt - na_players_elo))

    # Calculate progress
    f_progress = 1.0 - (f_score / f_worst_score)

    # Return
    return f_progress


def calc_suggested_num_iters(lo_players, i_mc_total=100, f_convergence_thresh=0.75):

    '''
        This function uses monte carlo simulations to determine the approximate
        number of iterations needed to achieve a good result.

        Luckily, it seems there's a very simple rule of thumb:  Use a number
        of iterations equal to x2 the number of players.  This is derived from 
        the data below:

            Number of Players:      10, 20, 40,  80, 160, 320
            Suggested Iterations:   15, 35, 78, 167, 340, 808
    '''

    # Define key variables
    i_num_players = len(lo_players)

    # Do monte carlo simulation
    li_iters = []
    for _ in tqdm(range(i_mc_total), desc="Monte Carlo Approximation"):

        # Initialize players
        lo_players = [Player(str(i)) for i in range(i_num_players)]

        # Run until we get a good result
        i_iters = 0
        while True:

            # Increment counter
            i_iters += 1

            # Get two players to compare
            o_player_1, o_player_2 = get_players(lo_players)

            # Assess winner
            o_winner = o_player_1 if int(o_player_1.s_name) >= int(o_player_2.s_name) else o_player_2
            o_loser = o_player_2 if int(o_player_2.s_name) <= int(o_player_1.s_name) else o_player_1

            # Update elos
            update_elos(o_winner, o_loser)

            # Get progress
            f_progress = check_convergence_progress(lo_players)
            if f_progress >= f_convergence_thresh:
                break

        # Store number of iterations
        li_iters.append(i_iters)

    # Calculate suggested number of iterations
    i_iters_suggested = np.median(li_iters)

    # Return
    return i_iters_suggested


def read_urls_from_file(filename):
    urls = []
    with open(filename, "r") as file:
        for line in file:
            urls.append(line.strip())
    return urls


def read_img_from_dir(s_img_dir):
    ls_img_ext = ["png", "jpg", "jpeg"]
    imgs = [os.path.join(s_img_dir, f) for f in os.listdir(s_img_dir) if f.split(".")[-1] in ls_img_ext]
    return imgs


def get_n_best(lo_players_rated, s_heur, i_n_best=None):

    # Create array of elos
    na_elos = np.array([[o_player.f_elo for o_player in to_players] for to_players in zip(*lo_players_rated)])

    # Apply group elo heuristic
    if s_heur == "min":
        na_elos_heur = np.min(na_elos, axis=1)
    elif s_heur == "avg":
        na_elos_heur = np.mean(na_elos, axis=1)
    elif s_heur == "max":
        na_elos_heur = np.max(na_elos, axis=1)
    else:
        assert False, \
            f"\nError! \"{s_hsur}\" not in [min, avg]"

    # Create new list
    lo_players = copy.deepcopy(lo_players_rated[0])
    for o_player, f_elo in zip(lo_players, na_elos_heur):
        o_player.f_elo = f_elo

    # Sort
    lo_players = sorted(lo_players, key=lambda x: x.f_elo)[::-1]

    # Parse
    if i_n_best is not None:
        lo_players = lo_players[:i_n_best]

    # Return
    return lo_players


