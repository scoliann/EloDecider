This project uses Elo ranking and optimization to facilitate group decision making.

## Inspiration

Finding a group consensus becomes exponentially hard as the number of options increases.  Unfortunately, we face this problem all the time:

- Choosing among loads of TripAdvisor pages to plan vacation
- Deciding among a dozen restaurants for dinner
- Picking the most interesting spots to check out on Atlas Obscura
- Deciding which pictures are the best
- Etc.

When faced with deciding between two choices, however, the decision is easy.  This project uses the Elo algorithm to assign ratings, and then considers the ratings from all users to determine an optimal subset of options.

## Demo
A brief video demonstrating how to run this project can be found [here](www.youtube.com)!

## Setup
1. Create and activate conda environment via:
```
    conda env create -f environment.yml
    conda activate env_elo_deccider
```
2. Create a new directory as `/adventures/<new_adventure>`
3. Do one of the following:
    1. To decide among urls , add a file where each line is a url as `/adventures/<new_adventure>/urls.txt`
    2. To decide among images, add a directory of images as `/adventures/<new_adventure>/images`

## Execution
1. Have each member of the group do the following:
    1. Run `python elo_comparer.py`, enter the requested information, and swipe left/right until done
2.  Run `python elo_selector.py`, enter the requested information, view results in the GUI, and close
3.  After closing the GUI, the ranked results will be saved as one of the following:
    1.  `/adventures/<new_adventure>/urls_ranked__<user_names>.txt`
    2.  `/adventures/<new_adventure>/images_ranked__<user_names>`

## Miscellaneous
- In Execution Step #2, the user is prompted to choose a selection heuristic from `[min, avg, max]`

| Heuristic     | Meaning       | IRL Example   |
| ------------- | ------------- | ------------- |
| min           | Assigns the Elo of each option as the min across users. | When friends choose a restaurant and options get nixed because one member of the group would be unhappy, they are using the min heuristic. |
| mean | Assigns the Elo of each option as the mean across users. | When students rank multiple field trip options, and a winner is chosen, they are using the mean heuristic.  |
| max | Assigns the Elo of each option as the max across users. | When you go on a date and do an activity of little personal interest, but great interest to your partner, you are using the max heuristic. | 



