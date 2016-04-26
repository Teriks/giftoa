## Details

Compiles a native binary that plays a GIF file in ASCII on the terminal using ncurses.


## Requirements

* gcc or compatible compiler, you can specify the compiler with `-cc` or `--compiler`
* Python 3.x
* ImageMagick
* jp2a
* libncurses-dev development package for your distro


## Usage

`giftoa.py -i gif_file.gif -o output_exe [jp2a options...]`

**or**

`giftoa.py -i gif_file.gif [jp2a options...]`  (Executable is named after GIF file)


===


`-fs` or `--framesleep` can be used to adjust the delay in nanoseconds between GIF frames.

100000000 nanoseconds, (0.1 second) is the default.  

The maximum value is 999999999 nanoseconds.

examples:

`giftoa.py -i gif_file.gif -fs 100000000 -o output_exe [jp2a options...]`


===


`-cc` or `--compiler` can be used to specify the compiler used to compile the binary

examples:

`giftoa.py -i gif_file.gif -cc clang -o output_exe [jp2a options...]`


===


See `jp2a -h` for more options once it is installed.
