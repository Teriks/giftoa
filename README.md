## Details

Compiles a native binary that plays a GIF file in ASCII on the terminal using ncurses.


## Requirements

* gcc or compatible compiler, you can specify the compiler with `-cc` or `--compiler`
* Python 3.x
* ImageMagick
* jp2a
* libncurses-dev development package for your distro


`sudo apt-get install gcc python3 ImageMagick jp2a libncurses-dev`

On debian based distributions.


## Basic Usage

`giftoa.py -i gif_file.gif -o output_exe [jp2a options...]`

**or**

`giftoa.py -i gif_file.gif [jp2a options...]`  (Executable is named after GIF file)


## Frame Delay


`-fsn` or `--framesleep-nanoseconds` can be used to adjust the delay in nanoseconds between GIF frames.

100000000 nanoseconds, (0.1 second) is the default.

The maximum value is 999999999 nanoseconds, the value must be a whole number.

example:

`giftoa.py -i gif_file.gif -fsn 100000000 -o output_exe [jp2a options...]`


`-fss` or `--framesleep-seconds` can be used to adjust the delay in seconds between GIF frames.
This is in addition to whatever amount of nanoseconds you specify.


example (1 second and 100 nanoseconds):

`giftoa.py -i gif_file.gif -fss 1 -fsn 100 -o output_exe [jp2a options...]`


The maximum value for `-fss` is 2147483647, the value must also be a whole number.


## C Compiler Selection


`-cc` or `--compiler` can be used to specify the compiler used to compile the binary

examples:

`giftoa.py -i gif_file.gif -cc clang -o output_exe [jp2a options...]`


## jp2a Options


See `jp2a -h` for more options once it is installed.

jp2a homepage: https://csl.name/jp2a/
