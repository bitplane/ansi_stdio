# 🖼️ ANSI stdio

ANSI text composition and animation library.

* Sparse buffer class based on 1 char `rich.Segment`
* Bounding box
* Nested clock

Here's a summary of our plan for the ANSI stdio library:

Core Architecture:

Clock system with parent-child relationships (already implemented)
Buffer system with support for multiple implementations
Actor/Sprite system for composable animations

Next Steps:

Integrate pyte for terminal emulation
Create a recorder for capturing terminal sessions with timing
Implement keyframe + delta storage format for efficient animations
Build a playback system using Rich for display

Technical Approach:

Use pyte to handle terminal emulation and ANSI sequences
Create timing wrappers and callbacks to capture animation frames
Store animations using keyframes and sparse deltas
Support multiple buffer implementations for different use cases

Long-term Goals:

Support streaming and real-time display
Allow composition of multiple animation sources
Create a web-friendly output format
Build "OBS for the terminal" type functionality

We've already tested with cmatrix and confirmed that the approach
should be efficient enough even for intensive animations.

## To do

* Sprite class
* Instances
* Load and save
* Test data
* Serialization base class
