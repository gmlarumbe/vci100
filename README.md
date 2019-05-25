# Overview #

Unofficial repository for Ableton Live 10 MIDI Remote Scripts Python Sources by Julien Bayle.
You can find more informations on this page:
https://julienbayle.studio/ableton-live-midi-remote-scripts


This repository includes a Python Remote Script for the combination of a Vestax VCI100 with a
KORG nanoPAD2. All the sources are contained in the VCI100 folder.


Two VCI100 instances should be set up in the MIDI section of Live preferences. This is necessary
to link the two devices together and control the behaviour of the nanoPAD with the VCI100.



# VCI100 #

The script remaps MIDI controls of this marvelous DJ Controller into a mixing table.

<img src="https://www.mixxx.org/wiki/lib/exe/fetch.php/vci100_45_big.jpg" width="500">


### Description ###

  * Left channel handles coarse controls and right channel handles fine controls: current track volume, pan and tempo.

  * Jogwheels are used to step through the song and slightly change tempo.

  * Left channel transport controls handle play/pause and cue set while right channel handles record and stepping through cues.

  * Left/right channels knobs for frequency adjustment handle current selected device controls.

  * Gain knobs set send controls for current track: reverb and delay.

  * There are some buttons that are not related to current track but they have a fixed function.
    These are the 8 buttons over the jogwheels and are mainly related to the arrangement view.

  * The cross buttons at the left of the left channel EQ are used in a different manner depending on current view (arrangement or session).
    They control movement over tracks plus clip launching.

  * The three buttons on the top left corner are used in conjunction with nanoPAD 2 controller to step through scenes and launch them.


# nanoPAD2 #

<img src="http://djexpressions.net/wp-content/uploads/2015/01/5_controladores_korg.jpg" width="500">

### Description ###


  * First scene is used to create rhytms on drum kits for armed tracks.


  * For the second and third nanoPAD scenes the script launches the clips on current Live scene, previously selected with the top-left corner buttons on VCI100.


  * Fourth scene is reserved for use with custom MIDI controls depending on the needs of the project.


  * NOTE: It is assumed that nanoPAD flash has been previously set up with appropriate notes and controls.


# Misc  #

RIP Vestax
