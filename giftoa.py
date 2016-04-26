#!/usr/bin/python3

# Copyright (c) 2016, Teriks
# All rights reserved.

# giftoa is distributed under the following BSD 3-Clause License

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived 
#    from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import sys
import os.path
import tempfile
import subprocess
import re
import argparse


def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]


def jp2a_cvars_into_file(env, file_out, var_name, image_filename, jp2a_args):
    jp2a = ["jp2a", image_filename]
    jp2a.extend(jp2a_args)

    success = True
    first_line = True

    with subprocess.Popen(jp2a, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env) as p:
        data = p.communicate()

        for line in data[1].decode().split('\n'):
            if line != "":
                print(line, file=sys.stderr)
                success = False
                
        if not success:
            return False
        
        for line in data[0].decode().split('\n'):
            if line != "":
                if first_line:
                    file_out.write("const char* " + var_name + "= \"\\\n" + line.rstrip() + "\\n\\\n")
                    first_line = False
                else:
                    file_out.write(line.rstrip() + "\\n\\\n")
        file_out.write("\";\n\n")
    return success


c_headers = """
#include "signal.h"
#include "curses.h"
#include "unistd.h"
#include "stdlib.h"


"""

c_program = """
WINDOW * mainwin = 0;

void cleanup()
{
    if(mainwin!=0)
    {
        delwin(mainwin);
        endwin();
        refresh();
    }
}

void signal_handler(int s)
{
    cleanup();
    exit(EXIT_SUCCESS);
}


int main(int argc, char *argv[]) 
{

    struct sigaction sigIntHandler;

    sigIntHandler.sa_handler = signal_handler;
    sigemptyset(&sigIntHandler.sa_mask);
    sigIntHandler.sa_flags = 0;

    sigaction(SIGINT, &sigIntHandler, NULL);


    
    const float framesleep = !FRAMESLEEP!;

    if ( (mainwin = initscr()) == NULL ) {
        fprintf(stderr, "Error initialising ncurses.\\n");
        exit(EXIT_FAILURE);
    }
    
    
    const char * frames[] = FRAMES_INIT;
    int framecnt = sizeof(frames) / sizeof(const char*);


    int frame = 0;

    nodelay(mainwin, 1);

    while(true) 
    {
        if(getch() == 27)
        {
            break;
        }

        clear();

        mvaddstr(0, 0, frames[frame]);
        refresh();
        usleep(framesleep);

        frame = frame == framecnt-1 ? 0 : frame+1;
    }

    cleanup();

    return EXIT_SUCCESS;
}
"""


def is_valid_file(parser, file):
    if os.path.isfile(file):
        return file
    else:
        parser.error('The file "{file}" does not exist.'.format(file=file))


parser = argparse.ArgumentParser(
    prog="giftoa",
    description="Compile a GIF into an native executable that plays the GIF in ASCII on the console using libncurses.",
    epilog=
    "All arguments following the arguments listed above will be passed as options to jp2a.  ANSI colors are not supported...  "
    "Also note that this program requires: gcc, libncurses-dev, jp2a and ImageMagick."
)

parser.add_argument('-i', '--input', help="The GIF file.", required=True, type=lambda file: is_valid_file(parser, file))

parser.add_argument('-o', '--output',
                    help="The name of the output file, if none is supplied it is taken from the name of the GIF.",
                    dest="out_file")

parser.add_argument('-fs', '--framesleep', type=str, default="100*1000",
                    help="The number of microseconds to sleep before moving to the next frame of the GIf. "
                         "The default is 100*1000;  this value can be an expression.")

parser.add_argument('-cc', '--compiler', type=str, default="cc",
                    help="The command used to invoke the C compiler, default is 'cc'.")



def main():
    args = parser.parse_known_args()
    jp2a_args = args[1]
    args = args[0]

    in_file = args.input
    out_file = os.path.splitext(os.path.basename(in_file))[0] if not args.out_file else args.out_file
    compiler = args.compiler

    env = os.environ.copy()

    if "TERM" not in env:
        env["TERM"] = 'xterm'

    with tempfile.TemporaryDirectory() as work_dir:

        convert_cmd = ["convert", "-coalesce", in_file, os.path.join(work_dir, "%d.jpg")]

        subprocess.call(convert_cmd);

        images = sorted(os.listdir(work_dir), key=natural_sort_key)

        program_file = os.path.join(work_dir, "program.c")

        with open(program_file, "w") as file:

            frames = []
            frame = 0

            file.write(c_headers)

            for image in images:

                frames.append("frame_" + str(frame))

                success = jp2a_cvars_into_file(env=env,
                                               file_out=file,
                                               var_name="frame_" + str(frame),
                                               image_filename=work_dir + "/" + image,
                                               jp2a_args=jp2a_args)

                if not success:
                    return 1

                frame += 1

            file.write("#define FRAMES_INIT {" + ",".join(frames) + "}")
            file.write(c_program.replace("!FRAMESLEEP!", args.framesleep, 1))

        compiler = [compiler, program_file, "-o", out_file, "-lcurses"]
        subprocess.call(compiler)

        return 0


if __name__ == "__main__":
    sys.exit(main())
