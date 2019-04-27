# PyGame
A simple game made via Python and PyGame for school.

Using the left and right arrow keys along with the space bar, you have to navigate across a 2d block world and reach the portal.
While it may sound simple there are a few tricks: false blocks, invisible blocks, and blocks that will just kill you. Not only this but the portal color is random, therefore the portal has a chance of being the same color as the background.

Custom maps can be created if you follow the 'map#.txt' template. However, the number must be sequential and greater than 0.


To build a map use the following values to create the world:

0 - Used as filler however this can be any value other than the ones listed below  
1 - A normal tile  
2 - A fake tile  
3 - Portal to the next level    
4 - Tile that will kill you once you collide with it  
5 - Player spawn (must be present, if more than 1 then the first one found is used)  
6 - Invisible tile
