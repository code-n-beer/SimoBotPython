SimoBotPython
=============

IRC bot written in Python. Uses separate, stoppable threads for running feature calls outside actual IRC client core. All features can be reloaded at run time by calling !reload from irc


Features
========

Calculator
-------
`!c <calculation>` Calculates 'n' stuff. Currently supports operators `+`, `-`, `*`, `/`, `%`, `^`, and parenthesis `(`, `)`.

Drinkify
-------
`!drinkify <artist>` Suggests you what to drink while listening to `<artist>`. `!drinkify np` suggests a drink according to your Last.fm now playing track. See [Last.fm](#lastfm) from below.

Expl
----
`!expl <word>` Shows and explanation for a word.

`!add <word> <explanation>` Adds an expl topic.

`!remove <word> <explanation>` Removes an expl topic or just one expl.

Horoscope
-----

`!horos <sign>` Returns your daily horoscope.

Last.fm
-------

`!np <username>` Returns currently playing or last played song from Last.fm.

`!setlastfm <username>` Sets your last.fm username for your irc-nick so `!np` works without parameters.

News
----

`!news` Returns todays most relevant news, delivered to you randomly.

Pirkkaniksi
-----------

`!niksi` Returns a random Pirkka Niksi.

Pizza-randomer
--------------

`!pizza 1-8` Returns a pizza with random toppings, if no amount of toppings is specified, randoms the amount of toppings too.

Reittiopas
----------

`!reittiopas <start> - <destination>, <time>` Returns HSL public transport route from start to destination, length and duration. If no time is specified uses current time. Uses `-`, `,` or `>` as separators.

Reverse
-------

`!r <input>` Returns input reversed.

Twitter
-------

`!tweet <input>` Tweets input.
`!follow <handle>` Follows user.
`!unfollow <handle>` Unfollows user.

Uguu
----

`!uguu <input>` Uguu

Unicafe
-------

`!uc` Returns Chemicum and Exactum Unicafe menus for today.

Urltitle
-------

Returns the title for pasted webpages.


Weather
-------

`!weather <location>` Returns current weather for location.

