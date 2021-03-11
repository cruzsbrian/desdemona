# Desdemona
Desdemona provides a server which generates matches, coordinates players, and allows viewing the game in real time,
and a player script which allows a text stream-based othello bot to communicate with the server.

## Installation
`pip install desdamona`

## Usage
The server is currently being hosted on [reversebreakdown.com](http://reversebreakdown.com).

After creating a match through the web interface, you are redirected to the viewing page for the match.
Anyone who accesses the viewing page (by url) becomes an observer for the match.

To start play, run `desdemona-player match_code color bot` 
where `match_code` is given on the viewing page, `color` is black or white, and `bot` is a path to the bot's executable.


## Bot text interface
`desdemona-player` will run the specified executable and communicate through text on stdin and stdout.
Any message the bot prints to stderr is passed through and ignored by `desdemona-player`.

On startup the bot should print a ready message, which can be anything and will be repeated by `desdemona-player` to the console.

Then `desdemona-player` will prompt the bot for each move with the message: `[row] [col] [ms_remaining]`, ending in newline.

- `row` and `col` specify the opponent's move as integers with (0,0) as the top left square. For a pass, both will be `-1`.
- `ms_remaining` gives the time left in the game for the bot in milliseconds as an integer (not yet implemented).

The bot should respond with `[row] [col]` or `pass` specifying it's move, also ending in newline.

## Running a local server
Running `desdemona-server` starts the server and prints a url.
If `desdamona-player` sees a local server, it will automatically connect to it before trying the default server.
