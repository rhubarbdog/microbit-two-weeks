<h1>Two Weeks - a Fortnight clone for microbit</h1>
<b>
<code>host.py</code><br/><br/>
<code>microbit.py</code><br/><br/>
<code>game.py</code><br/><br/>
<code>gamezip.py</code><br/><br/>
</b>
There a 3 control methods avaialable for 'Two Weeks' one is the microbit
accelerometer, just tilt the board to move the player, press <code>button b
</code> to reveal the compass.  The second is the Kitronik Game
https://kitronik.co.uk/products/5644-game-controller the third is the  Kitronik
GameZip https://kitronik.co.uk/products/5626-game-zip-64-for-the-bbc-microbit.
The compass is displayed on the GameZip version on the microbit, on the Game
press fire button 2 on the controller to reveal the compass.
<br/><br/>
The game requires a version 2 microbit per player and a further version 2
microbit to host the game. Freshly flash the microbits with <code>uflash</code>
or copy a <code>microbit.hex</code> file directly to the microbit. Use microFS
or the file transfer facility in <code>mu-editor</code> to copy to programs
over. Each players microbit runs the program <code>gamezip.py</code>,
<code>game.py</code> or <code>microbit.py</code> copy the correct with the
commands similar to the following example<br/><br/>
<code>ufs put microbit.py main.py</code><br/><br/>
The final microbit which hosts the game running program <code>host.py</code>
copy it to the microbit as follows.<br/><br/>
<code>ufs put host.py main.py</code><br/><br/>

Reset the host, switch on or reset each player there is a thirty second period
to automatically enroll for the game, the host will be scrolling the
message 'Two Weeks' and each player should be scrolling their player number.
Then 5, 4, 3, 2, 1 the game has started. You have been abandonned in a unknown
world, use the compass to find the exit, first player there wins.
Playing <code>gamezip.py</code> guide the red sprite to the purple exit.  With
<code>microbit.py</code> and <code>game.py</code> the player fades from bright
to dim, the walls are brightest and the exit is flashing.
<br/><br/>
This is a genuine multi player game.  To start a new game just reset all
microbits, ensure the host is ready to receive your enrollment requests.