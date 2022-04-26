# 3D-Rendering-in-Python

*Type of project:* Experimental, self-learning
*State of completion:* Complete and archived

A (very) crude 3D rendering engine I made in Python as a learning experience when learning about the theory behind 3D games!

Currently, just for fun and a bit of experimenting, so it doesn't quite support the features that Unreal 5 might have just yet (as may become somewhat obvious when its run).

The motivation for this project came when I started considering the graphics for Taking London; at the time I was using placeholder graphics either ripped from other
pixel-art games, or hastily drawn myself, meaning the game looked...crap, frankly.

I'm no artist, so I struggle with drawing anything more than a stickman and as such was struggling to get the lighting and shadows to look acceptable in my sprites.
I therefore had the theory that if one was to render a model in 3D, the ambient lighting physics would take care of all of that for you, meaning you would only have
to draw the 2D textures, and then you could take 2D screenshots of your rendered model to use as your sprites. Clash of Clans works this way, and the result is a 
surprisingly polished end product whilst still having the simplicity of a 2D game!

I started doing this in C++ with the OpenGL libraries, but I became intrigued as to how rendering worked from first principles. You don't get a whole lot of exposure
to that in OpenGL where you're basically just calling various library methods, so I decided to have a crack myself in Python.
