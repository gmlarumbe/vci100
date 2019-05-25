from __future__ import absolute_import, print_function, unicode_literals
import Live
from Live import MidiMap

from _Framework.ControlSurface import ControlSurface
from _Framework.EncoderElement import EncoderElement
from _Framework.TransportComponent import TransportComponent
from _Framework.SessionComponent import SessionComponent
from _Framework.DeviceComponent import DeviceComponent
from _Framework.MixerComponent import MixerComponent

from .DeviceNavComponent import DeviceNavComponent
from .DeviceClipSwitcherComponent import DeviceClipSwitcherComponent
from .SetupVCI100 import *



class VCI100(ControlSurface):
    """ Script for the Vestax VCI-100 MIDI Controller plus KORG nanoPAD for clip launching """

# * Setup
    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        with self.component_guard():
            self._suggested_input_port = 'Vestax PC-CONTROLLER'
            self._suggested_output_port = 'Vestax PC-CONTROLLER'
            self._set_subclasses_logs()
            self._init_values()
            self._setup_framework_interface()
            self._setup_custom_interface()
            self._setup_nanopad(self._session)
            self._live_api_listeners()
            self._update_view_mode_cfg()
        return


    def _init_values(self):
        # Indices within `Audio Effects` browser Item for Item Browser
        self._compressor_idx = 7
        self._eq8_idx = 12
        self._reverb_idx = 31
        self._delay_idx = 33
        # Volume tweaking
        self._last_current_track_volume_value = None
        self._last_current_track_volume_value_fine = None
        self._TweakFineVol = False
        # Panning tweaking
        self._last_current_track_pan_value = None
        self._last_current_track_pan_value_fine = None
        self._TweakFinePan = False
        # Tempo tweaking
        self._last_tempo_value = None
        self._TweakCoarseTempo = False
        self._TweakFineTempo = False
        self._init_tempo_value = self.song().tempo
        self._TweakTempoSlider = False
        # Others
        self._last_timebar = self.song().get_current_beats_song_time().beats
        self._browser_focused = False
        self._current_track_index = 0
        self._prev_track_index = 0
        # Following attributes will be used by self._update_view_mode_cfg()
        self._alternate_mode = False
        if self.application().view.is_view_visible('Session'):
            self._mode_index = 1 # Start in session by default
        else:
            self._mode_index = 0 # Start in arranger by default


    def _live_api_listeners(self):
        """ Associate buttons with listeners directly related to calls to Live API
        """
        self.application().view.add_is_view_visible_listener('Session', self._on_view_changed)
        self.song().add_tempo_listener(self._tempo_change)
        self.song().add_is_playing_listener(self._song_playing_change)
        self.song().add_current_song_time_listener(self._song_time_change)
        self.song().master_track.add_output_routings_listener(self._test_output_routings)
        self.song().master_track.add_output_sub_routings_listener(self._test_output_sub_routings)


    def _set_subclasses_logs(self):
        DeviceNavComponent.set_log(self.log_message)
        DeviceClipSwitcherComponent.set_log(self.log_message)


    def _update_view_mode_cfg(self):
        if self._mode_index == 0: # ARRANGER VIEW
            self._mixer.set_select_buttons(self._but_cross_bottom, self._but_cross_top)
            self._session.set_select_buttons(None, None)
            self._session.selected_scene().clip_slot(self._current_track_index).set_launch_button(None)
            self._device_nav.set_device_nav_buttons(self._but_cross_left, self._but_cross_right)
            if BUT_CENTRE == 'dev-clip':
                self._dev_clip_sw.set_device_clip_switch_button(self._but_cross_centre)
            elif BUT_CENTRE == 'on-off':
                self._device.set_on_off_button(self._but_cross_centre)
            else:
                self.log_message("Invalid value for cross centre button @ arrangement view")

        else: # SESSION VIEW
            self._mixer.set_select_buttons(self._but_cross_right, self._but_cross_left)
            self._session.set_select_buttons(self._but_cross_bottom, self._but_cross_top)
            self._session.selected_scene().clip_slot(self._current_track_index).set_launch_button(self._but_cross_centre)
            self._device_nav.set_device_nav_buttons(None, None)
            if BUT_CENTRE == 'dev-clip':
                self._dev_clip_sw.set_device_clip_switch_button(None)
            elif BUT_CENTRE == 'on-off':
                self._device.set_on_off_button(None)
            else:
                self.log_message("Invalid value for cross centre button @ session view")

        # ALTERNATE MODE
        if self._alternate_mode: # Disable external wheels
            self.show_message("BOLO Mode!!")
            self._transport.set_seek_buttons(None, None)
            self._transport.set_nudge_buttons(None, None)
        else:
            self.show_message("STUDIO Mode!!") # Reenable external wheels
            self._transport.set_seek_buttons(self._but_seek_back, self._but_seek_fwd)
            self._transport.set_nudge_buttons(self._but_nudge_back, self._but_nudge_fwd)

        return


    def disconnect(self):
        ControlSurface.disconnect(self)
        return


    def _toggle_but_light(self, button):
        assert isinstance(button, VCINoteButton)
        if button.light:
            button.light = False
        else:
            button.light = True
        button.set_light(button.light)



# * Framework interface methods
    def _setup_framework_interface(self):
        # Cross buttons
        self._but_cross_top = VCINoteButton("G#5")
        self._but_cross_bottom = VCINoteButton("A5")
        self._but_cross_left = VCINoteButton("C6")
        self._but_cross_right = VCINoteButton("C#6")
        self._but_cross_centre = VCINoteButton("A#5")
        # Seek/Nudge buttons
        self._but_seek_back = VCINoteButton("A#2")
        self._but_seek_fwd = VCINoteButton("B2")
        self._but_nudge_back = VCINoteButton("C3")
        self._but_nudge_fwd = VCINoteButton("C#3")
        # Create Components
        self._browser = self.application().browser
        self._transport = TransportComponent()
        self._mixer = MixerComponent(NUM_TRACKS_MAX)
        self._session = SessionComponent(NUM_TRACKS_CLP, NUM_ROWS)
        self._device = DeviceComponent(device_selection_follows_track_selection=True)
        self._device_nav = DeviceNavComponent()
        self._dev_clip_sw = DeviceClipSwitcherComponent()
        # Subroutines to initialize components using the _Framework layer
        self._setup_transport_control()
        self._setup_mixer_control()
        self._setup_session_control()
        self._setup_device_control()


    def _setup_transport_control(self):
        self._transport.set_stop_button(VCINoteButton("E2")) # Used instead of `set_play_button' since it was resumed after the Green Marker
        self._transport.set_record_button(VCINoteButton("F#2"))
        self._transport.set_loop_button(VCINoteButton("G3"))
        self._transport.set_metronome_button(VCINoteButton("B3"))
        self._transport.set_overdub_button(VCINoteButton("G2")) # 'Session Record' Button


    def _setup_mixer_control(self):
        self._mixer.set_prehear_volume_control(VCIKnob(88))
        self._mixer.selected_strip().set_mute_button(VCINoteButton("D4"))
        self._mixer.selected_strip().set_solo_button(VCINoteButton("D#4"))
        self._mixer.selected_strip().set_arm_button(VCINoteButton("C4"))
        send_control_a = VCIKnob(28)
        send_control_b = VCIKnob(29)
        current_send_controls = []
        current_send_controls.append(send_control_a)
        current_send_controls.append(send_control_b)
        self._mixer.selected_strip().set_send_controls(current_send_controls)

    def _setup_session_control(self):
        self._session.set_scene_bank_buttons(VCINoteButton("E6"), VCINoteButton("D6"))


    def _setup_device_control(self):
        self._device.set_parameter_controls(tuple([EncoderElement(MIDI_CC_TYPE, GLOBAL_CHANNEL, 20 + index, Live.MidiMap.MapMode.absolute) for index in range(8)]))
        self.set_device_component(self._device)



# * Custom methods
# ** Setup
    def _setup_custom_interface(self):
        """ Dynamic creation of attributes and listeners depending on setup variables.
        Makes use of metaprogramming to avoid cluttering code with numerous attributes.
        Configuration is therefore done by setting up listening functions and filling
        dictionaries accordingly.
        """
        for but, params in BUTTONS.items():
            attr = "_" + but + '_button'                     # Private attribute
            note = params['note']                            # Parse button note
            function = getattr(self, "_" + params['func'])   # Parse listener function
            setattr(self, attr, VCINoteButton(note))         # Create button attribute
            getattr(self, attr).add_value_listener(function) # Create listener function

        for knob, params in KNOBS.items():
            attr = "_" + knob + '_button'
            value = params['value']
            function = getattr(self, "_" + params['func'])
            setattr(self, attr, VCIKnob(value))
            getattr(self, attr).add_value_listener(function)

        for slider, params in SLIDERS.items():
            attr = "_" + slider + '_button'
            value = params['value']
            function = getattr(self, "_" + params['func'])
            setattr(self, attr, VCIKnob(value))
            getattr(self, attr).add_value_listener(function)


# ** Volume
    # Fetched from: /home/martigon/Repos/githubExamples/AbletonLive10_MIDIRemoteScripts/_Framework/ChannelStripComponent.py:168
    def _set_volume_control_coarse(self, value):
        self._TweakFineVol = False
        param_value = value/127.0
        self.song().view.selected_track.mixer_device.volume.value = param_value
        self._last_current_track_volume_value = param_value


    def _set_volume_control_fine(self, value):
        param_value = value/127.0
        fine_factor = 4

        if not self._TweakFineVol:
            self._last_current_track_volume_value_fine = param_value

        if self._last_current_track_volume_value is None or self._last_current_track_volume_value_fine is None: # Coarse or fine parameters not tweaked before (e.g when switching a track)
            self._last_current_track_volume_value = self.song().view.selected_track.mixer_device.volume.value
            self._last_current_track_volume_value_fine = param_value

        current_vol = self._last_current_track_volume_value
        current_vol_fine = self._last_current_track_volume_value_fine

        new_value = current_vol + ((param_value - current_vol_fine)/fine_factor)
        new_value = min(new_value, 1.0)
        new_value = max(new_value, 0.0)

        self.song().view.selected_track.mixer_device.volume.value = new_value
        self._TweakFineVol = True


# ** Panning
    def _set_pan_control_coarse(self, value):
        self._TweakFinePan = False
        param_value = (value*2/127.0)-1
        self.song().view.selected_track.mixer_device.panning.value = param_value
        self._last_current_track_pan_value = param_value


    def _set_pan_control_fine(self, value):
        param_value = value/127.0
        fine_factor = 2

        if not self._TweakFinePan:
            self._last_current_track_pan_value_fine = param_value

        if self._last_current_track_pan_value is None or self._last_current_track_pan_value_fine is None: # Coarse or fine parameters not tweaked before (e.g when switching a track)
            self._last_current_track_pan_value = self.song().view.selected_track.mixer_device.panning.value
            self._last_current_track_pan_value_fine = param_value

        current_pan = self._last_current_track_pan_value
        current_pan_fine = self._last_current_track_pan_value_fine

        new_value = current_pan + ((param_value - current_pan_fine)/fine_factor)
        new_value = min(new_value, 1.0)
        new_value = max(new_value, -1.0)

        self.song().view.selected_track.mixer_device.panning.value = new_value
        self._TweakFinePan = True


    def _set_pan_reset_current_track(self, value):
        if not self._pan_reset_button.is_momentary() or value is not 0:
            self.song().view.selected_track.mixer_device.panning.value = 0


# ** Tempo
    # Framework interface tempo control coarse is absolute. Hence another function is created to manage it.
    # These functions would replace `self._transport.set_tempo_control(VCISlider(14), VCISlider(15)) #(control, fine_control)'
    def _set_tempo_control_coarse(self, value):
        param_value = (value*2/127.0)-1 # Range between -1 and 1
        coarse_factor = 8

        if not self._TweakCoarseTempo:
            self._init_tempo_value = self.song().tempo
            self._last_tempo_value = param_value

        current_tempo = self._init_tempo_value
        current_tempo_fine = self._last_tempo_value

        new_value = current_tempo + ((param_value - current_tempo_fine)*coarse_factor)
        # Clamp values between min and max
        new_value = min(new_value, TEMPO_MAX)
        new_value = max(new_value, TEMPO_MIN)

        self._TweakTempoSlider = True
        self.song().tempo = new_value

        self._TweakCoarseTempo = True
        self._TweakFineTempo = False


    def _set_tempo_control_fine(self, value):
        param_value = (value*2/127.0)-1 # Range between -1 and 1
        fine_factor = 2

        if not self._TweakFineTempo:
            self._init_tempo_value = self.song().tempo
            self._last_tempo_value = param_value

        current_tempo = self._init_tempo_value
        current_tempo_fine = self._last_tempo_value

        new_value = current_tempo + ((param_value - current_tempo_fine)*fine_factor)
        # Clamp values between min and max
        new_value = min(new_value, TEMPO_MAX)
        new_value = max(new_value, TEMPO_MIN)

        self._TweakTempoSlider = True
        self.song().tempo = new_value

        self._TweakFineTempo = True
        self._TweakCoarseTempo = False


# ** Arrangement view controls
    def _follow_value(self, value):
        if self._follow_button is not None:
            if not self._follow_button.is_momentary() or value is not 0:
                self.song().view.follow_song = not self.song().view.follow_song
                if self.song().view.follow_song:
                    self._follow_button.set_light(True)
                else:
                    self._follow_button.set_light(False)
        return


    def _automation_arm_value(self, value):
        if not self._automation_arm_button.is_momentary() or value is not 0:
            self.song().session_automation_record = not self.song().session_automation_record
            self.log_message("automation_arm value")


    def _reenable_automation_value(self, value):
        if not self._reenable_automation_button.is_momentary() or value is not 0:
            self.song().re_enable_automation()
            self._reenable_automation_button.set_light(True)
        else:
            self._reenable_automation_button.set_light(False)


    def _capture_value(self, value):
        if not self._capture_button.is_momentary() or value is not 0:
            self.song().capture_midi()
            self._capture_button.set_light(True)
        else:
            self._capture_button.set_light(False)


    def _tap_tempo_value(self, value):
        if value > 0:
            self.song().tap_tempo()


    # Fetched from /home/martigon/Repos/githubExamples/AbletonLive10_MIDIRemoteScripts/LiveControl_2/LC2TransportComponent.py:125
    def _back_to_arranger_value(self, value):
        if not self._back_to_arranger_button.is_momentary() or value is not 0:
            self.song().back_to_arranger = not self.song().back_to_arranger
            self._back_to_arranger_button.set_light(True)
        else:
            self._back_to_arranger_button.set_light(False)


# ** Session view controls
    def _launch_selected_scene_value(self, value):
        if value > 0:
            if self._mode_index == 1:
                self._session.selected_scene().set_launch_button(self._browser_centre_button)



# ** Output controls
    def _output_monitor_select_value(self, value):
        if value < 64:
            self.song().master_track.output_routing_channel = self.song().master_track.available_output_routing_channels[0]
        else:
            self.song().master_track.output_routing_channel = self.song().master_track.available_output_routing_channels[2]


    def _master_output_volume_value(self, value):
        master_vol = value * 0.85 / 127.0 # Value ranges between 0 and 127. 0.85 corresponds to multiplier for 0dB max instead of 6dB
        self._mixer.master_strip()._track.mixer_device.volume.value = master_vol


    def _current_monitoring_state_change_value(self, value):
        if value is not 0 and self.song().view.selected_track in self.song().tracks:
            self.song().view.selected_track.current_monitoring_state = (self.song().view.selected_track.current_monitoring_state + 1) % 3
            if self.song().view.selected_track.current_monitoring_state is not 1: # Different from 'Auto'
                self._current_monitoring_state_button.set_light(True)
            else:
                self._current_monitoring_state_button.set_light(False)



# ** Transport controls
    def _continue_playing_value(self, value):
        """ Starts where song was stopped (Shift+Space). Light is automatic (from VCI) for this button """
        if value > 0:
            if self.song().is_playing:
                self.song().stop_playing()
            else:
                self.song().continue_playing()


    def _play_selection_value(self, value):
        """ Starts where current marker is (Ctrl+Space). Light is automatic (from VCI) for this button """
        if value > 0:
            if self.song().is_playing:
                self.song().stop_playing()
            else:
                self.song().play_selection()


    def _set_or_delete_cue_value(self, value):
        if value > 0:
            self.song().set_or_delete_cue()
            self._set_or_delete_cue_button.set_light(True)
        else:
            self._set_or_delete_cue_button.set_light(False)


    def _jump_to_next_cue_value(self, value):
        if value > 0:
            self.song().jump_to_next_cue()
            self._jump_to_next_cue_button.set_light(True)
        else:
            self._jump_to_next_cue_button.set_light(False)


    def _jump_to_prev_cue_value(self, value):
        if value > 0:
            self.song().jump_to_prev_cue()
            self._jump_to_prev_cue_button.set_light(True)
        else:
            self._jump_to_prev_cue_button.set_light(False)




# ** Jog wheel
    # Fetched from: /home/martigon/Repos/githubExamples/AbletonLive10_MIDIRemoteScripts/MackieControl/Transport.py
    def _handle_jog_wheel_rotation(self, value):
        """ Jog wheel without vinyl mode
        """
        backwards = value <= 64
        step = max(1.0, (value - 64) / 2.0)
        if self.song().is_playing:
            if backwards:
                self.song().scrub_by(-step)
            else:
                self.song().scrub_by(step)
        else:
            if backwards:
                self.song().jump_by(-step)
            else:
                self.song().jump_by(step)


    def _handle_jog_wheel_scratch(self, value):
        """ Jog wheel with vinyl mode
        """
        backwards = value <= 64
        step = max(1.0, (value - 64) / 2.0)
        if self.song().is_playing:
            if backwards:
                self.song().scrub_by(-step)
            else:
                self.song().scrub_by(step)
        else:
            if backwards:
                self.song().jump_by(-step)
            else:
                self.song().jump_by(step)


    def _handle_jog_wheel_rotation_fine(self, value):
        """ Jog wheel without vinyl mode
        """
        backwards = value <= 64
        step = max(1.0, (value - 64) / 2.0)
        step = step / 4
        if self.song().is_playing:
            if backwards:
                self.song().scrub_by(-step)
            else:
                self.song().scrub_by(step)
        else:
            if backwards:
                self.song().jump_by(-step)
            else:
                self.song().jump_by(step)


    def _handle_jog_wheel_scratch_fine(self, value):
        """ Jog wheel with vinyl mode
        """
        backwards = value <= 64
        step = max(1.0, (value - 64) / 2.0)
        step = step / 4
        if self.song().is_playing:
            if backwards:
                self.song().scrub_by(-step)
            else:
                self.song().scrub_by(step)
        else:
            if backwards:
                self.song().jump_by(-step)
            else:
                self.song().jump_by(step)




# ** Browser controls
    def _browser_button_up_value(self, value):
        if not self._browser_button_up.is_momentary() or value is not 0:
            self.log_message("browser_button_up")
            app_view = self.application().view
            app_view.focus_view('Browser')
            modifier_pressed = True
            directions = Live.Application.Application.View.NavDirection
            app_view.scroll_view(directions.up, 'Browser', not modifier_pressed)

    def _browser_button_centre_value(self, value):
        if not self._browser_centre_button.is_momentary() or value is not 0:
            self.log_message("browser button centre")
            app_view = self.application().view
            app_view.focus_view('Browser')
            modifier_pressed = True
            directions = Live.Application.Application.View.NavDirection
            app_view.scroll_view(directions.right, 'Browser', not modifier_pressed)


    def _browser_button_down_value(self, value):
        if not self._browser_button_down.is_momentary() or value is not 0:
            self.log_message("browser button down")
            app_view = self.application().view
            app_view.focus_view('Browser')
            modifier_pressed = True
            directions = Live.Application.Application.View.NavDirection
            app_view.scroll_view(directions.down, 'Browser', not modifier_pressed)


    def _browser_view_focus(self, value):
        if not self._browser_centre_button.is_momentary() or value is not 0:
            app_view = self.application().view
            if not self._browser_focused:
                app_view.focus_view('Browser')
                self._browser_focused = True
            else:
                self._browser_focused = False
                if app_view.is_view_visible('Session'):
                    app_view.focus_view('Session')
                else:
                    app_view.focus_view('Arranger')


# ** Alternate mode
    def _shift_value(self, value):
        if value > 64:
            self._alternate_mode = True
        else:
            self._alternate_mode = False
        self._update_view_mode_cfg()
        return



# ** Change listeners
    def _on_view_changed(self):
        if self.application().view.is_view_visible('Session'):
            self._mode_index = 1
        else:
            self._mode_index = 0
        self._update_view_mode_cfg()


    # Fetched from ProjectX
    def _on_selected_track_changed(self):
        """This is an override to add special functionality: we want to move the session to the selected track when it changes.
        """
        _prev_track_index = self._current_track_index
        ControlSurface._on_selected_track_changed(self) # This will run component.on_selected_track_changed() for all components
        # Get selected track
        selected_track = self.song().view.selected_track # This is how to get the currently selected track, using the Live API
        all_tracks = ((self.song().tracks + self.song().return_tracks) + (self.song().master_track,)) # This is from the MixerComponent's _next_track_value method
        assert selected_track in all_tracks
        index = list(all_tracks).index(selected_track) # And so is this
        # Assign/deassign proper clip values depending on indices only in session View
        if self._mode_index == 1:
            self._session.selected_scene().clip_slot(_prev_track_index).set_launch_button(None)
            self._session.selected_scene().clip_slot(index).set_launch_button(self._but_cross_centre)
        # Update internal status indices
        self._prev_track_index = _prev_track_index
        self._current_track_index = index
        # Other settings for selected track fine control
        self._last_current_track_volume_value = None
        self._last_current_track_volume_value_fine = None
        self._last_current_track_pan_value = None
        self._last_current_track_pan_value_fine = None
        self._TweakFineVol = False
        self._TweakFinePan = False
        # Light stuff for custom lighted buttons (in fact it's only for monitoring input)
        if selected_track in self.song().tracks:
            if self.song().view.selected_track.current_monitoring_state is not 1: # Different from 'Auto'
                self._current_monitoring_state_button.set_light(True)
            else:
                self._current_monitoring_state_button.set_light(False)
        else: # Master or return tracks
            self._current_monitoring_state_button.set_light(False)


    def _tempo_change(self):
        if not self._TweakTempoSlider: # Tempo change was due to a manual change (mouse/keyboard) not due to a slider movement
            self._init_tempo_value = self.song().tempo
            self._TweakCoarseTempo = False
            self._TweakFineTempo = False

        self._TweakTempoSlider = False # Reset flag


    def _song_playing_change(self):
        if not self.song().is_playing:
            self._tap_tempo_button.light = False
            self._tap_tempo_button.set_light(self._tap_tempo_button.light)
            self._play_selection_button.set_light(False)
        else:
            self._play_selection_button.set_light(True)


    def _song_time_change(self):
        if self.song().is_playing:
            timebar = self.song().get_current_beats_song_time().beats
            if self._last_timebar != timebar:
                self._last_timebar = timebar
                self._toggle_but_light(self._tap_tempo_button)
        else:
            if self._tap_tempo_button.light:
                self._tap_tempo_button.light = False
                self._tap_tempo_button.set_light(self._tap_tempo_button.light)


# ** Insert Audio/Midi FX
    # Fetched from /home/martigon/Repos/githubExamples/AbletonLive10_MIDIRemoteScripts/Push2/browser_component.py:557
    def _insert_compressor(self, value):
        if not self._insert_compressor_button.is_momentary or value is not 0:
            item = self._browser.audio_effects
            compressor = item.children[self._compressor_idx]
            self._browser.load_item(compressor)


    def _insert_eq8(self, value):
        if not self._insert_eq8_button.is_momentary or value is not 0:
            item = self._browser.audio_effects
            eq8 = item.children[self._eq8_idx]
            self._browser.load_item(eq8)


    def _insert_reverb(self, value):
        if not self._insert_reverb_button.is_momentary or value is not 0:
            item = self._browser.audio_effects
            reverb = item.children[self._reverb_idx]
            self._browser.load_item(reverb)


    def _insert_delay(self, value):
        if not self._insert_delay_button.is_momentary or value is not 0:
            item = self._browser.audio_effects
            delay = item.children[self._delay_idx]
            self._browser.load_item(delay)




# ** Debug listeners
    def _test_function(self, value):
        if value > 0:
            current_arm = self.song().view.selected_track.arm
            self.log_message("current_arm={}".format(current_arm))

    def _test_output_routings(self):
        # self.log_message("Output routings listener!!")
        pass

    def _test_output_sub_routings(self):
        # self.log_message("Output sub_routings listener!!")
        pass



# ** Nanopad
    def _setup_nanopad(self, session):
        """ Used in conjunction with VCI100: 2 rows on a specific NanoPad scene
        """
        session.set_offsets(0,0)
        self.set_highlighting_session_component(session)
        # Here we set up the clip launch assignments for the session
        clip_launch_notes =   ["F2", "G2", "A2", "B2", "C#3", "D#3", "F3", "G3"]
        clip2_launch_notes =  ["E2", "F#2", "G#2", "A#2", "C3", "D3", "E3", "F#3"]

        for index in range(NUM_TRACKS_CLP):
            session.scene(0).clip_slot(index).set_launch_button(NanoButton(clip_launch_notes[index]))
            session.scene(1).clip_slot(index).set_launch_button(NanoButton(clip2_launch_notes[index]))

        session._link()


    def _setup_nanopad_standalone(self, session):
        """ Standalone/Debug purposes: up to 3 clip launch rows and 1 stop clip row in different scenes
        """
        session.set_offsets(0,0)
        self.set_highlighting_session_component(session)
        session.set_scene_bank_buttons(NanoButton("F#3"), NanoButton("G3"))

        # This is 'per track'
        stop_track_buttons = []
        stop_track_buttons_list = ["F2", "G2", "A2", "B2", "C#3", "D#3", "F3"]
        for index in range(NUM_TRACKS):
            stop_track_buttons.append(NanoButton(stop_track_buttons_list[index]))
        session.set_stop_track_clip_buttons(tuple(stop_track_buttons)) # Array size needs to match num_tracks

        # Here we set up the clip launch assignments for the session
        clip_launch_notes =  ["E2", "F#2", "G#2", "A#2", "C3", "D3", "E3"]
        clip2_launch_notes = ["A3", "B3", "C#4", "D#4", "F4", "G4", "A4"]
        clip3_launch_notes = ["G#3", "A#3", "C4", "D4", "E4", "F#4", "G#4"]

        for index in range(NUM_TRACKS):  #step through scenes and assign a note to first slot of each
            session.scene(0).clip_slot(index).set_launch_button(NanoButton(clip_launch_notes[index]))
            session.scene(1).clip_slot(index).set_launch_button(NanoButton(clip2_launch_notes[index]))
            session.scene(2).clip_slot(index).set_launch_button(NanoButton(clip3_launch_notes[index]))

        session._link()
