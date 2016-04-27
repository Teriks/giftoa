## Details

Compiles a native binary that plays a GIF in ASCII on the terminal using ncurses.

![Demo](https://github.com/Teriks/giftoa/raw/master/readme_demo.gif)


`./giftoa.py -i cat.gif -o cat_gif --invert && ./cat_gif`


## Requirements

* gcc or compatible compiler, you can specify the compiler with `-cc` or `--compiler`
* Python 3.x
* ImageMagick
* jp2a
* libncurses-dev development package for your distro

On debian based distributions:

`sudo apt-get install gcc python3 imagemagick jp2a libncurses-dev`


## Basic Usage

`./giftoa.py -i gif_file.gif -o output_exe [jp2a options...]`

**or**

`./giftoa.py -i gif_file.gif [jp2a options...]`  (Executable is named after GIF file)

**or**

You can specify a directory containing .jpg or .jpeg files, the images in the directory
will be used as frames for the animation.  They will be sorted in natural order by name, so you
should include some kind of frame number at the beginning or end of each file name.

If you do this, you must specify the name of the output executable explicitly.


`./giftoa.py -i directory -o output_file_name_required.exe [jp2a options...]`


## Frame Delay / FPS


`-fps` or `--frames-per-second` can be used to set a target FPS for the animation.

If not specified, it defaults to 10 frames per second.

This option cannot be used together with `-fss` or `-fsn`.

The minimum value is 1 and the maximum value is 1000000000, the value must be a whole number.


example:

`./giftoa.py -i gif_file.gif -fps 25 -o output_exe [jp2a options...]`


===


`-fsn` or `--framesleep-nanoseconds` can be used to adjust the delay in nanoseconds between GIF frames.

This option cannot be used with `-fps` / `--frames-per-second`.


The minimum value is 0 and the maximum value is 999999999, the value must be a whole number.


example:

`./giftoa.py -i gif_file.gif -fsn 100000000 -o output_exe [jp2a options...]`


===


`-fss` or `--framesleep-seconds` can be used to adjust the delay in seconds between GIF frames.
This is in addition to whatever amount of nanoseconds you specify.

This option cannot be used with `-fps` / `--frames-per-second`.

`-fsn` will default to 0 when `-fss` is used and additional nanoseconds are not explicitly specified.


example (1 second and 100 nanoseconds):

`./giftoa.py -i gif_file.gif -fss 1 -fsn 100 -o output_exe [jp2a options...]`


The minimum value is 0 and the maximum value is 2147483647, the value must also be a whole number.


## C Compiler Selection


`-cc` or `--compiler` can be used to specify the compiler used to compile the binary

examples:

`./giftoa.py -i gif_file.gif -cc clang -o output_exe [jp2a options...]`


## jp2a Options


See `jp2a -h` for more options once it is installed.

jp2a homepage: https://csl.name/jp2a/
