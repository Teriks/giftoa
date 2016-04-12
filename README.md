## Details

Compiles a native binary that plays a GIF file in ASCII on the terminal using ncurses.


## Requirements

* gcc
* Python 3.x
* ImageMagick
* jp2a
* libncurses development package for your distro


## Usage

`giftoa gif_file.gif -o output_exe [jp2a options...]`

**or**

`giftoa gif_file.gif [jp2a options...]`  (Executable is named after GIF file)


===


`-fs` or `--framesleep` can be used to adjust the delay in microseconds between GIF frames.

examples:

`giftoa gif_file.gif -fs 100*1000 -o output_exe [jp2a options...]`

===

See `jp2a -h` for more options once it is installed.
