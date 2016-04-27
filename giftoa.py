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

    GIFTOA_FRAMESLEEP_INIT

    struct sigaction sigIntHandler;

    sigIntHandler.sa_handler = signal_handler;
    sigemptyset(&sigIntHandler.sa_mask);
    sigIntHandler.sa_flags = 0;

    sigaction(SIGINT, &sigIntHandler, NULL);


    if ( (mainwin = initscr()) == NULL ) {
        fprintf(stderr, "Error initialising ncurses.\\n");
        exit(EXIT_FAILURE);
    }
    
    
    const char * frames[] = GIFTOA_FRAMES_INIT;
    int framecnt = sizeof(frames) / sizeof(const char*);


    int frame = 0;

    nodelay(mainwin, 1);

    struct timespec startTime;
    struct timespec endTime;
    struct timespec computedDelay;

    while(true) 
    {
        if(getch() == 27)
        {
            break;
        }

        clock_gettime(CLOCK_MONOTONIC, &startTime);

        clear();
        mvaddstr(0, 0, frames[frame]);
        refresh();

        clock_gettime(CLOCK_MONOTONIC, &endTime);

        computedDelay.tv_sec = frameDelay.tv_sec - (endTime.tv_sec - startTime.tv_sec);
        computedDelay.tv_nsec = frameDelay.tv_nsec - (endTime.tv_nsec - startTime.tv_nsec);

        nanosleep(&computedDelay, NULL);

        frame = frame == framecnt-1 ? 0 : frame+1;
    }

    cleanup();

    return EXIT_SUCCESS;
}
"""


def is_valid_input(parser, file_or_dir):
    if os.path.isfile(file_or_dir):
        return file_or_dir
    elif os.path.isdir(file_or_dir):
        return file_or_dir
    else:
        parser.error('The path "{path}" is not a file or directory.'.format(path=file_or_dir))


def is_valid_frames_per_second(parser, sleep):
    err_prefix = 'argument -fps/--frames-per-second: '

    try:
        i_value = int(sleep)
    except ValueError:
        parser.error(err_prefix + 'Value must be a whole / integral number.')
        # parser.error calls exit(2), this is to silence pre-commit code analysis
        return None

    if i_value > 1000000000:
        parser.error(err_prefix + 'Value cannot be greater than 1000000000.')
    if i_value < 1:
        parser.error(err_prefix + 'Value cannot be less than 1.')
    return i_value


def is_valid_framesleep_seconds(parser, sleep):
    err_prefix = 'argument -fsn/--framesleep-nanoseconds: '

    try:
        i_value = int(sleep)
    except ValueError:
        parser.error(err_prefix + 'Value must be a whole / integral number.')
        # parser.error calls exit(2), this is to silence pre-commit code analysis
        return None

    if i_value > 2147483647:
        parser.error(err_prefix + 'Value cannot be greater than 2147483647.')
    if i_value < 0:
        parser.error(err_prefix + 'Value cannot be less than 0.')
    return i_value


def is_valid_framesleep_nanoseconds(parser, sleep):
    err_prefix = 'argument -fsn/--framesleep-nanoseconds: '

    try:
        i_value = int(sleep)
    except ValueError:
        parser.error(err_prefix + 'Value must be a whole / integral number.')
        # parser.error calls exit(2), this is to silence pre-commit code analysis
        return None

    if i_value > 999999999:
        parser.error(err_prefix + 'Value cannot be greater than 999999999.')
    if i_value < 0:
        parser.error(err_prefix + 'Value cannot be less than 0.')
    return i_value


parser = argparse.ArgumentParser(
    prog='giftoa',

    description=
    'Compile a GIF into an native executable that plays the GIF in ASCII on the console using libncurses.',

    epilog=
    'All arguments following the arguments listed above will be '
    'passed as options to jp2a.  ANSI colors are not supported...  '
    'Also note that this program requires: gcc, libncurses-dev, jp2a and ImageMagick.'
)

parser.add_argument('-i', '--input',
                    help='A GIF file or a directory full of jp2a compatible image frames (jpegs).  '
                         'If you provide a directory, the jpeg images are sorted by name in natural order, '
                         'you should include a frame number.  Specifying the output file with --output is '
                         'required when a directory is passed to --input.',

                    required=True, dest='input_path',
                    type=lambda file_or_dir: is_valid_input(parser, file_or_dir))

parser.add_argument('-o', '--output',
                    help='The name of the output executable.  '
                         'If a GIF file is passed and no output name is supplied '
                         'the name of the file without its extension is used.  '
                         'When passing a directory to -i / --input, you must specify an output file name.',
                    dest='out_file')

parser.add_argument('-fps', '--frames-per-second', default=None, dest='frames_per_second',

                    type=lambda sleep: is_valid_frames_per_second(parser, sleep),

                    help='The frames per second to attempt to play the animation at (defaults to 10).  '
                         'The minimum value is 1 and the maximum value is 1000000000, FPS must be a whole number.  '
                         'This cannot be used when either -fss or -fsn is specified.'
                    )

parser.add_argument('-fss', '--framesleep-seconds', default=None, dest='framesleep_seconds',

                    type=lambda sleep: is_valid_framesleep_seconds(parser, sleep),

                    help='The number of seconds to sleep before moving to the next frame of the GIF.  '
                         'This is in addition to the number of nanoseconds specified by "-fsn".  '
                         'The value cannot be greater than 2147483647.'
                    )

parser.add_argument('-fsn', '--framesleep-nanoseconds', default=None, dest='framesleep_nanoseconds',

                    type=lambda sleep: is_valid_framesleep_nanoseconds(parser, sleep),

                    help='The number of nanoseconds to sleep before moving to the next frame of the GIF. '
                         'This is in addition to the number of seconds specified by "-fss."  '
                         'The value cannot be greater than 999999999.'
                    )

parser.add_argument('-cc', '--compiler', type=str, default='cc',
                    help='The command used to invoke the C compiler, default is "cc".')

jp2a_known_extensions = {'.jpg', '.jpeg'}


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


def get_framesleep_init_string(args):
    if args.frames_per_second:
        if args.frames_per_second == 1:
            frame_sleep_seconds = 1
            frame_sleep_nanoseconds = 0
        else:
            frame_sleep_seconds = 0
            frame_sleep_nanoseconds = 1000000000 // args.frames_per_second
    else:
        frame_sleep_seconds = args.framesleep_seconds if \
            args.framesleep_seconds else 0

        # default to 10 fps, 0.1 second frame delay
        frame_sleep_nanoseconds = args.framesleep_nanoseconds if \
            args.framesleep_nanoseconds else 100000000

    return 'frameDelay.tv_nsec = {nanoseconds};' \
           'frameDelay.tv_sec = {seconds};' \
           .format(nanoseconds=frame_sleep_nanoseconds,
                   seconds=frame_sleep_seconds)


def main():

    args = parser.parse_known_args()
    jp2a_args = args[1]
    args = args[0]

    if args.frames_per_second and args.framesleep_seconds or args.framesleep_nanoseconds:
        parser.error('-fss (--framesleep-seconds) and -fsn (--framesleep-nanoseconds) '
                     'cannot be used with -fps (--frames-per-second).')
        # parser.error calls exit(2) immediately

    input_path = args.input_path
    out_file = args.out_file
    compiler = args.compiler

    environment = os.environ.copy()

    if 'TERM' not in environment:
        environment['TERM'] = 'xterm'

    frame_sleep_init_string = get_framesleep_init_string(args)

    with tempfile.TemporaryDirectory() as temp_dir:

        if os.path.isfile(input_path):
            if not out_file:
                out_file = os.path.splitext(os.path.basename(input_path))[0]

            subprocess.call([
                'convert',
                '-background', 'none',
                input_path,
                '-coalesce',
                '-bordercolor', 'none',
                '-frame', '0', os.path.join(temp_dir, '%d.jpg')])

            image_paths = sorted(os.listdir(temp_dir), key=natural_sort_key)
            image_paths = (os.path.join(temp_dir, path) for path in image_paths)
        else:
            if not out_file:
                parser.error('No output file specified, an output file must be specified '
                             'when passing a directory to --input or -i.')
                # parser.error calls exit(2) immediately

            image_paths = (file for file in os.listdir(input_path) if os.path.splitext(file)[1] in jp2a_known_extensions)
            image_paths = sorted(image_paths, key=natural_sort_key)

            if len(image_paths) == 0:
                parser.error('No jp2a compatible images found in directory "{dir}".'.format(dir=input_path))
                # parser.error calls exit(2) immediately

            image_paths = (os.path.join(input_path, path) for path in image_paths)

        program_file = os.path.join(temp_dir, 'program.c')

        with open(program_file, 'w') as out_c_source:

            frame_cvar_names = []

            out_c_source.write(C_HEADERS)

            for frame, image_path in enumerate(image_paths):

                cvar_name = 'frame_' + str(frame)

                frame_cvar_names.append(cvar_name)

                success = jp2a_cvars_into_file(environment=environment,
                                               file_out=out_c_source,
                                               var_name=cvar_name,
                                               image_filename=image_path,
                                               jp2a_args=jp2a_args)

                if not success:
                    return 1

            out_c_source.write('#define GIFTOA_FRAMES_INIT {' + ','.join(frame_cvar_names) + '}\n')
            out_c_source.write('#define GIFTOA_FRAMESLEEP_INIT ' + frame_sleep_init_string + '\n')
            out_c_source.write(C_PROGRAM)

        subprocess.call([compiler, program_file, '-o', out_file, '-lcurses'])

        return 0


if __name__ == '__main__':
    sys.exit(main())
