Requires Python 3.3 to run

Simply open MH3U Damage Calculator in IDLE and press F5 to run.

If any of my values are wrong, please let me know. Please forward
errors or suggestions to EphemeralRain on reddit.

To alter any weapon attack values, edit weapons.txt.

To alter enemy defenses, edit monsters.csv.

This program makes the following assumptions in calculating damage:

    1. All weapons are given an average attack multiplier instead of a
       multiplier for each attack. This is done to simplify the program.
       If you disagree with the averages I chose, modify the values in
       wepmod.txt.

       Note that these values, in my opinion, represent the general attacks
       you will use. I excluded attacks that are weak and used infrequently.

    2. All monsters are given an average defense instead of a defense per
       zone. This is done to simplify the calculations. These values should
       represent the average damage you do to a monster - I weighted higest
       the zones which are hit frequently and weakest to damage, and excluded
       those infrequently hit or always avoided due to high defense.

    3. Due to the nature of the ranking, status weapons aren't well represented.
       This is due to the difficulty in ranking the efficacy of poison, etc as
       a value.

    4. I couldn't find exact values for the other SA vials (poison, dragon). I
       assumed they functioned as free awaken in sword mode.

    5. If anyone has accurate values for Dire Miralis, please forward them to me.

    6. Average damage increase from affinity is accounted for.

    7. Not all weapons are included because I copied them all by hand after
       I couldn't find a nice bundled resource with the data. Only final stages
       of weapons are included for now; weapons that are obviously bad aren't
       included.

       If anyone can point me to a resource that I can easily extract all
       weapon and monster information from, I will gladly enhance the program
       to use all available information.