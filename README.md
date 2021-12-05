# fsiforum-scraper
Little script for downloading materials from File Thingie at FSI Forum.

## Instalation
You have to have installed Python 3.8 or newer and git.

Instalation is pretty simple.

In command line / terminal use `pip install git+https://github.com/ArcasCZ/fsiforum-scraper`

Don't forget that on Windows you should run CMD as Administrator, otherwise you can run into some problems with PATH (Module not found error)

## Usage

All data are downloaded in newly created folder `index` in current working directory.

Because folder / file list is behind login, you have to login on FSI Forum first and then use SESSION ID as parameter to run this script. 

The fastest way is to login on forum, copy `index.php` as cURL (tutorial here: https://everything.curl.dev/usingcurl/copyas) and then paste it into some text editor (notepad++ would be enough. Then find part with `PHPSESSID=somenonsensecharactersandnumbers;` and copy that part between `PHPSESSID=` and `;`. This is your session.

Now you can run this script using `python -m fsiforum --session somenonsensecharactersandnumbers`.

There are more parameters you can add (before or after `--session`.

 - `--stats` only shows, how many folders and files are there and then ends
 - `--diff` works only with files you are missing
 - `--log` prints relative path and file URL into `log.txt`
 - `--text-only` log into `log.txt` without downloading (can be combined with `--diff`)

## Known problems
