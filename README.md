# 🖼️ ansi_stdio

Terminal text composition and animation library.

```sh
$ uv ansi_stdio
```

## Tools

* `ansi-quantize` - terminal filter to help you strip out log dump noise from
  asciinema recordings

## notes from Claude

Here's a summary of our plan for the ANSI stdio library:

Core Architecture

Clock system with parent-child relationships (already implemented)
Buffer system with support for multiple implementations
Actor system for composable animations

Next Steps

Create an animated buffer class
Create a recorder for capturing terminal sessions with timing
Implement keyframe + delta storage format for efficient animations
Build a playback system using Rich for display

Technical Approach:

Use pyte to handle terminal emulation and ANSI sequences
Create timing wrappers and callbacks to capture animation frames
Store animations using keyframes and sparse deltas

Long-term Goals:

Build "OBS for the terminal" type functionality
Support streaming and real-time display
Allow composition of multiple animation sources
Create a web-friendly output format

## To do

* Actor class
* Test data
* Load and save buffers
* Animated buffers
* Animation file format
* Serialization base class

