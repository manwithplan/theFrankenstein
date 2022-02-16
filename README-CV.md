# Computer Vision


Below are examples of *object recognition* and *detection* from a live feed of the game **Elite: Dangerous**, a space simulator
video game where we are trying to detect the action the player is currently undertaking in real time. This is combined with
music playback capabilities to make a live soundtrack to the game.

Using **OpenCV** all these detections are marked as flags, and combined in a decision tree to extract the current player's state.
All of them use **HSV filtering** as opposed to **RGB** to take lighting changes into account, as well as a focused cropped out area
as a Region Of Interest. The whole image is calibrated by rotation and scaling on each frame to take into account player 
movements.

In the examples below you can see the analyzed ROI in the top corners.

## Docking



From time to time the player docks with massive space stations, to among others refuel. We can detect this action by looking 
for an authorisation screen that pops up just above the minimap. These consist of a light blue text inside a few lines. When 
we filter for these colors and apply probabilistic Hough lines detection we can detect the presence of these lines and mark
it detected.



![](./theResources/docking.gif)


## Speed



To detect the player's ship speed, we can take a look at the speed gauge on the right of the minimap. Again we filter out 
the color, but this time we dilate the image so the green bars flow into each other and make one large blob. When we detect
the contours then, we can select the largest one and the ratio of the surface are can be used to measure speed.



![](./theResources/speed.gif)


## Conflict Detection



In this case we want to detect whether the player is engaged in a conflict. If he is the ship he is currently targetting, which 
is represented by it's icon in the bottom-left of the screen turns a certain kind of red. The detection is triggered when the are 
we are cropping out has a large amount of these red pixels in them.



![](./theResources/conflict.gif)



## Conflict Zone Detection



When a player is engaging more than one opponent there is still only one targetted ship, so the detection of multiple is made using 
the minimap in the bottom-center of the screen. Using the dilation and erosion the shapes are closed and once the surface area 
is above a certain threshold an enemy is counted.



![](./theResources/conflict-multiple.gif)
