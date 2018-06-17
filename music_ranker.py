#!/usr/bin/env python3

import os
import sys
import re
import time
import subprocess as sp
import numpy as np
import unicodedata

if __name__ == '__main__':
    # get list of files to run over
    files = []
    if len(sys.argv) == 2:
        for music_basedir, music_dir, music_files in os.walk(sys.argv[1]):
            if len(music_dir) != 0:
                continue
            for mf in music_files:
                files.append(music_basedir + "/" + mf)

    # DEFINITIONS
    # player commands
    file_length_query = "mplayer -ao null -identify -frames 0 {0}"
    player_command = "mplayer -really-quiet -ss {0} -endpos {1} {2}"

    window_length = 30
    max_tries = 5

    # queue music
    for filename in np.random.permutation(files):
        # PROPER FILENAME FORMATTING
        # songs cannot have a tab in the name
        if "\t" in filename:
            print("tab in filename {0}".format(filename))
            continue
        # proper formatting for CLI
        special_characters = [" ", "'", "\"", "&", "(", ")", ";"]
        filename_bash = filename
        for sc in special_characters:
            filename_bash = filename_bash.replace(sc, "\\" + sc)

        # PLAYING SONG
        # figure out song length in seconds
        p = sp.Popen(file_length_query.format(filename_bash), shell=True, stdout=sp.PIPE)
        out, err = p.communicate()
        #out = str(out, "utf-8")
        out = str(out)
        exp = re.compile(r"ID_LENGTH=\d*\.*\d*")
        # e.g. ID_LENGTH=270.00
        if exp is not None:
            try:
                length = exp.search(out).group(0).split("=")[1]
            except:
                print("failed to extract length {0}".format(filename))
                sys.exit()
            length = int(length.split(".")[0])
        else:
            print("could not parse song length: {0}".format(filename))
            continue

        # songs must be less than window length + 2 seconds
        if length <= window_length + 2:
            print("song too short: {0}".format(filename))
            continue
       
        # equal chances of picking start/middle/end of song
        song_idx = np.random.randint(0, 6) 
        if song_idx in (0,1,2):
            song_part = "start"
            start_pos = 0
        elif song_idx in (3,4):
            song_part = "middle"
            start_pos = np.random.randint(1, length - window_length - 1)
        elif song_idx in (5,):
            song_part = "end"
            start_pos = length - window_length

        # play music
        sp.call(player_command.format(start_pos, window_length, filename_bash), shell=True)

        # GET/WRITE RANK
        # query user for rank
        allowed_inputs = ("yy", "y", "m", "n", "nn", "q")
        rank_input = None
        tries = 0
        while rank_input not in allowed_inputs and tries < max_tries:
            rank_input = input("Enter yy/y/m/n/nn\n")
            tries += 1

        if rank_input == "q":
            print("exiting")
            sys.exit()

        if rank_input not in allowed_inputs:
            print("bad input, exiting")
            sys.exit()

        # record rank
        print("recording preference: {0}".format(rank_input))
        write_header = False
        if not os.path.exists("like_record.tsv"):
            write_header = True

        try:
            rec = open("like_record.tsv","a")
        except IOError:
            print("record file open failed")
            sys.exit()

        if write_header:
            rec.write(
                "user_time\ttime_stamp\tfile_name\tshort_file_name\tsong_part\tstart_position\tplay_window\tsong_length\trank\n"
            )

        time_stamp = time.time()
        rec.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\n".format(
            time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(time_stamp)),
            int(np.around(time_stamp*1000)),
            filename,
            os.path.basename(filename),
            song_part,
            start_pos,
            window_length,
            length,
            rank_input)
        )
        rec.close()
        print("done recording")
