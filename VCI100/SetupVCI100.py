# * Imports
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE


# * Variables
MIDI_NOTES = {"C-2"  : 0,   "C#-2" : 1,   "D-2"  : 2,  "D#-2"  : 3,   "E-2"  : 4,   "F-2"  : 5,
              "F#-2" : 6,   "G-2"  : 7,   "G#-2" : 8,   "A-2"  : 9,   "A#-2" : 10,  "B-2"  : 11,
              "C-1"  : 12,  "C#-1" : 13,  "D-1"  : 14, "D#-1"  : 15,  "E-1"  : 16,  "F-1"  : 17,
              "F#-1" : 18,  "G-1"  : 19,  "G#-1" : 20,  "A-1"  : 21,  "A#-1" : 22,  "B-1"  : 23,
              "C0"   : 24,  "C#0"  : 25,  "D0"   : 26, "D#0"   : 27,  "E0"   : 28,  "F0"   : 29,
              "F#0"  : 30,  "G0"   : 31,  "G#0"  : 32,  "A0"   : 33,  "A#0"  : 34,  "B0"   : 35,
              "C1"   : 36,  "C#1"  : 37,  "D1"   : 38, "D#1"   : 39,  "E1"   : 40,  "F1"   : 41,
              "F#1"  : 42,  "G1"   : 43,  "G#1"  : 44,  "A1"   : 45,  "A#1"  : 46,  "B1"   : 47,
              "C2"   : 48,  "C#2"  : 49,  "D2"   : 50, "D#2"   : 51,  "E2"   : 52,  "F2"   : 53,
              "F#2"  : 54,  "G2"   : 55,  "G#2"  : 56,  "A2"   : 57,  "A#2"  : 58,  "B2"   : 59,
              "C3"   : 60,  "C#3"  : 61,  "D3"   : 62, "D#3"   : 63,  "E3"   : 64,  "F3"   : 65,
              "F#3"  : 66,  "G3"   : 67,  "G#3"  : 68,  "A3"   : 69,  "A#3"  : 70,  "B3"   : 71,
              "C4"   : 72,  "C#4"  : 73,  "D4"   : 74, "D#4"   : 75,  "E4"   : 76,  "F4"   : 77,
              "F#4"  : 78,  "G4"   : 79,  "G#4"  : 80,  "A4"   : 81,  "A#4"  : 82,  "B4"   : 83,
              "C5"   : 84,  "C#5"  : 85,  "D5"   : 86, "D#5"   : 87,  "E5"   : 88,  "F5"   : 89,
              "F#5"  : 90,  "G5"   : 91,  "G#5"  : 92,  "A5"   : 93,  "A#5"  : 94,  "B5"   : 95,
              "C6"   : 96,  "C#6"  : 97,  "D6"   : 98, "D#6"   : 99,  "E6"   : 100, "F6"   : 101,
              "F#6"  : 102, "G6"   : 103, "G#6"  : 104, "A6"   : 105, "A#6"  : 106, "B6"   : 107,
              "C7"   : 108, "C#7"  : 109, "D7"   : 110, "D#7"  : 111, "E7"   : 112, "F7"   : 113,
              "F#7"  : 114, "G7"   : 115, "G#7"  : 116, "A7"   : 117, "A#7"  : 118, "B7"   : 119,
              "C8"   : 120, "C#8"  : 121, "D8"   : 122, "D#8"  : 123, "E8"   : 124, "F8"   : 125,
              "F#8"  : 126, "G8"   : 127}

NUM_TRACKS_MAX  = 25 # Maximum number of tracks (could be even larger)
NUM_TRACKS_CLP  = 8
NUM_TRACKS      = 8
NUM_ROWS        = 2
GLOBAL_CHANNEL  = 0
NANOPAD_CHANNEL = 2
TEMPO_MAX       = 200
TEMPO_MIN       = 60
BUT_CENTRE      = 'on-off' # Valid values: ['dev-clip', 'on-off']

BUTTONS = {
    "follow"                   : {'note' : "A#3"  , 'func' : "follow_value"},
    "back_to_arranger"         : {'note' : "F#3"  , 'func' : "back_to_arranger_value"},
    "tap_tempo"                : {'note' : "A3"   , 'func' : "tap_tempo_value"},
    "browser_centre"           : {'note' : "D#6"  , 'func' : "launch_selected_scene_value"},
    "insert_compressor"        : {'note' : "F6"   , 'func' : "insert_compressor"},
    "insert_eq8"               : {'note' : "F#6"  , 'func' : "insert_eq8"},
    "insert_reverb"            : {'note' : "G6"   , 'func' : "insert_reverb"},
    "insert_delay"             : {'note' : "G#6"  , 'func' : "insert_delay"},
    "current_monitoring_state" : {'note' : "C#4"  , 'func' : "current_monitoring_state_change_value"},
    "continue_playing"         : {'note' : "D#2"  , 'func' : "continue_playing_value"},
    "play_selection"           : {'note' : "D2"   , 'func' : "play_selection_value"},
    "set_or_delete_cue"        : {'note' : "F2"   , 'func' : "set_or_delete_cue_value"},
    "jump_to_next_cue"         : {'note' : "A2"   , 'func' : "jump_to_next_cue_value"},
    "jump_to_prev_cue"         : {'note' : "G#2"  , 'func' : "jump_to_prev_cue_value"},
    "pan_reset"                : {'note' : "A#-1" , 'func' : "set_pan_reset_current_track"}
    }


KNOBS = {
    "scrub_normal"         : {'value' : 18, 'func' : "handle_jog_wheel_rotation"},
    "scrub_scratch"        : {'value' : 16, 'func' : "handle_jog_wheel_scratch"},
    "scrub_normal_fine"    : {'value' : 19, 'func' : "handle_jog_wheel_rotation_fine"},
    "scrub_scratch_fine"   : {'value' : 17, 'func' : "handle_jog_wheel_scratch_fine"},
    "master_output_volume" : {'value' : 7,  'func' : "master_output_volume_value"},
    "output_routing"       : {'value' : 89, 'func' : "output_monitor_select_value"},
    "crossfader"           : {'value' : 8,  'func' : "shift_value"},
    "pan_control"          : {'value' : 30, 'func' : "set_pan_control_coarse"},
    "pan_control_fine"     : {'value' : 31, 'func' : "set_pan_control_fine"}
    }


SLIDERS = {
    "volume_control"      : {'value' : 12, 'func' : "set_volume_control_coarse"},
    "volume_control_fine" : {'value' : 13, 'func' : "set_volume_control_fine"},
    "tempo_control"       : {'value' : 14, 'func' : "set_tempo_control_coarse"},
    "tempo_control_fine"  : {'value' : 15, 'func' : "set_tempo_control_fine"}
    }



# * Aux Classes
class VCINoteButton(ButtonElement):
    "Docu"
    def __init__(self, note):
        super(VCINoteButton, self).__init__(True, MIDI_NOTE_TYPE, GLOBAL_CHANNEL, note2midi(note))
        self.light = False
        self.set_light(self.light)


class VCIKnob(ButtonElement):
    "Docu"
    def __init__(self, cc_value):
        super(VCIKnob, self).__init__(True, MIDI_CC_TYPE, GLOBAL_CHANNEL, cc_value)


class VCISlider(SliderElement):
    "Docu"

    def __init__(self, cc_value):
        super(VCISlider, self).__init__(MIDI_CC_TYPE, GLOBAL_CHANNEL, cc_value)


class NanoButton(ButtonElement):
    "Docu"
    def __init__(self, note):
        super(NanoButton, self).__init__(True, MIDI_NOTE_TYPE, NANOPAD_CHANNEL, note2midi(note))



# * Aux Functions
def note2midi(note):
    return MIDI_NOTES[note]
