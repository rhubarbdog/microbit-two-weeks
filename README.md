<h1>Two Weeks - a Fortnight clone for microbit</h1>

<b>This is a genuine multi-player game</b> -  for version 2 microbit's<br/>

Reset the host first, then switch on each player.  There is a thirty second period to automatically enroll for the game.  The host will be scrolling the message 'Two Weeks - host' and each player should be scrolling their player number.  Then 5, 4, 3, 2, 1 the game has started. You have been abandonned in a unknown world, use the compass to find the exit, first player there wins.
<br/><br/>
<b><code>host.py</code></b><br/>
Tha actual game running in the ether.
<br/><br/>
<b><code>microbit.py</code></b><br/>
A version for the microbit only, just tilt the board to move the player, press
<code>button b</code> to reveal the compass.  The player fades from bright
to dim and back again, the walls are brightest, the exit is flashing and other players a medium brightness.
<br/><br/>
<b><code>game.py</code></b><br/>
The version is for the Kitronik Game
https://kitronik.co.uk/products/5644-game-controller. Use the cursor keys to move the player and press fire button 2 on the controller to reveal the compass.  The player fades from bright to dim, the walls are brightest, the exit is flashing and other players a medium brightness.
<br/><br/>
<b><code>gamezip.py</code></b><br/>
This version is for the  Kitronik
GameZip https://kitronik.co.uk/products/5626-game-zip-64-for-the-bbc-microbit.  Use the cursor keys to move the player the compass is displayed on the microbit.  Guide the red sprite to the purple exit avoiding the blue walls and other players which are yellow.
</br>
</br>
The game requires a version 2 microbit per player and a further version 2 microbit to host the game.  There are two installation methods.  Directly copy `host.hex` to one micro bit and then `microbit.hex`, `game.hex` or `gamezip.hex` to each player's microbit.  Or freshly flash the microbits using either <code>uflash</code> or copy <code>micropython.hex</code> file directly to the microbit. Then use microFS or the file transfer facility in <code>mu-editor</code> to copy to programs to each microbit.  Each player's microbit runs the program <code>gamezip.py</code>, <code>game.py</code> or <code>microbit.py</code> depending on which controller they have.  Copy the correct program with the following commands.
<br/>
<br/>
<code>ufs put microbit.py main.py</code><br/><br/>
<code>ufs put game.py main.py</code><br/><br/>
<code>ufs put gamezip.py main.py</code><br/><br/>
<br/>
The final microbit which hosts the game running program <code>host.py</code>
copy it to the microbit as follows.<br/><br/>
<code>ufs put host.py main.py</code><br/><br/>

There currently are a few issues with MicroPython and version 2 microbit's.  Try the `microbit.hex` in this repository which is a copy of MicroPython.

<h2>Futures for Two Weeks</h2>
<list>
<li>A gun with limitted bullets.</li>
<li>The Weather.</li>
<li>Sound Effects</li>
<li>Enemies controlled by the microbit<li/>
</list>

<h2>Future forks for this repository</h2>
<list>
<li>Call of Duty, one side the Allies the other the Nazi's.</li>
<li>Luigi's Mansion, one player Luigi with his torch, the rest ghosts.</li>
<li>Tron on light bikes</li>
<li>Multi player snake</li>
<li>World of War Craft</li>
<li>Orienteering, either all start in the same location and get the flags in order or all start in random locations collecting the flags as you find them.</li>
</list>