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


C_HEADERS = """
#include "signal.h"
#include "curses.h"
#include "stdlib.h"
#include "time.h"

"""

C_PROGRAM = """
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
    struct timespec frameDelay;
    !FRAMESLEEP_INIT!


    struct sigaction sigIntHandler;

    sigIntHandler.sa_handler = signal_handler;
    sigemptyset(&sigIntHandler.sa_mask);
    sigIntHandler.sa_flags = 0;

    sigaction(SIGINT, &sigIntHandler, NULL);


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
        nanosleep(&frameDelay, NULL);

        frame = frame == framecnt-1 ? 0 : frame+1;
    }

    cleanup();

    return EXIT_SUCCESS;
}
"""


def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]


def jp2a_cvars_into_file(environment, file_out, var_name, image_filename, jp2a_args):
    jp2a = ['jp2a', image_filename]
    jp2a.extend(jp2a_args)

    success = True
    first_line = True

    with subprocess.Popen(jp2a, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment) as p:
        data = p.communicate()

        for line in data[1].decode().split('\n'):
            if line != '':
                print(line, file=sys.stderr)
                success = False

        if not success:
            return False

        for line in data[0].decode().split('\n'):
            if line != '':
                if first_line:
                    file_out.write('const char* ' + var_name + '= "\\\n' + line.rstrip() + '\\n\\\n')
                    first_line = False
                else:
                    file_out.write(line.rstrip() + '\\n\\\n')

        file_out.write('";\n\n')

    return success


def is_valid_file(parser, file):
    if os.path.isfile(file):
        return file
    else:
        parser.error('The file "{file}" does not exist.'.format(file=file))


def is_valid_framesleep_seconds(parser, sleep):
    i_value = int(sleep)
    if i_value > 2147483647:
        parser.error('--framesleep-seconds cannot be given a value greater than 2147483647.')
    if i_value < 0:
        parser.error('--framesleep-seconds cannot be given a value less than 0.')
    return sleep


def is_valid_framesleep_nanoseconds(parser, sleep):
    i_value = int(sleep)
    if i_value > 999999999:
        parser.error('--framesleep-nanoseconds cannot be given a value greater than 999999999.')
    if i_value < 0:
        parser.error('--framesleep-nanoseconds cannot be given a value less than 0.')
    return sleep


parser = argparse.ArgumentParser(
    prog='giftoa',

    description=
    'Compile a GIF into an native executable that plays the GIF in ASCII on the console using libncurses.',

    epilog=
    'All arguments following the arguments listed above will be '
    'passed as options to jp2a.  ANSI colors are not supported...  '
    'Also note that this program requires: gcc, libncurses-dev, jp2a and graphicsmagick.'
)

parser.add_argument('-i', '--input', help='The GIF file.', required=True, dest='input_gif',
                    type=lambda file: is_valid_file(parser, file))

parser.add_argument('-o', '--output',
                    help='The name of the output file.  If none is supplied it is taken from the name of the GIF.',
                    dest='out_file')


parser.add_argument('-fss', '--framesleep-seconds', default='0', dest='framesleep_seconds',

                    type=lambda sleep: is_valid_framesleep_seconds(parser, sleep),

                    help='The number of seconds to sleep before moving to the next frame of the GIF.  '
                         'This is in addition to the number of nanoseconds specified by "-fsn".  '
                         'The default is 0, the value cannot be greater than 2147483647.'
                    )

parser.add_argument('-fsn', '--framesleep-nanoseconds', default='100000000', dest='framesleep_nanoseconds',

                    type=lambda sleep: is_valid_framesleep_nanoseconds(parser, sleep),

                    help='The number of nanoseconds to sleep before moving to the next frame of the GIF. '
                         'This is in addition to the number of seconds specified by "-fss."  '
                         'The default is 100000000, the value cannot be greater than 999999999.'
                    )

parser.add_argument('-cc', '--compiler', type=str, default='cc',
                    help='The command used to invoke the C compiler, default is "cc".')


def main():
    giftoa_args = parser.parse_known_args()
    jp2a_args = giftoa_args[1]
    giftoa_args = giftoa_args[0]

    in_gif_path = giftoa_args.input_gif
    out_file = os.path.splitext(os.path.basename(in_gif_path))[0] if not giftoa_args.out_file else giftoa_args.out_file
    compiler = giftoa_args.compiler

    environment = os.environ.copy()

    if 'TERM' not in environment:
        environment['TERM'] = 'xterm'

    frame_sleep_init = 'frameDelay.tv_nsec = {nanoseconds};frameDelay.tv_sec = {seconds};'\
                       .format(nanoseconds=giftoa_args.framesleep_nanoseconds,
                               seconds=giftoa_args.framesleep_seconds)

    with tempfile.TemporaryDirectory() as temp_dir:

        file_spec = os.path.join(temp_dir, '%d.jpg')

        subprocess.call([
            'convert', 
            '-background', 'none', 
            in_gif_path, 
            '-coalesce', 
            '-bordercolor', 'none', 
            '-frame', '0', file_spec])

        images = sorted(os.listdir(temp_dir), key=natural_sort_key)

        program_file = os.path.join(temp_dir, 'program.c')

        with open(program_file, 'w') as file:

            frames = []
            frame = 0

            file.write(C_HEADERS)

            for image in images:

                frames.append('frame_' + str(frame))

                success = jp2a_cvars_into_file(environment=environment,
                                               file_out=file,
                                               var_name='frame_' + str(frame),
                                               image_filename=temp_dir + '/' + image,
                                               jp2a_args=jp2a_args)

                if not success:
                    return 1

                frame += 1

            file.write('#define FRAMES_INIT {' + ','.join(frames) + '}')
            file.write(C_PROGRAM.replace('!FRAMESLEEP_INIT!', frame_sleep_init, 1))

        subprocess.call([compiler, program_file, '-o', out_file, '-lcurses'])

        return 0


if __name__ == '__main__':
    sys.exit(main())
