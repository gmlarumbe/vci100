from __future__ import absolute_import, print_function, unicode_literals
import Live
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ViewControlComponent import ViewControlComponent


class DeviceClipSwitcherComponent(ControlSurfaceComponent):
    u""" Component that allows switching between devices and clip at Detail view
    In practice makes use of cross centre button to switch between device/clip instead of turning current device on/off"""

    @staticmethod
    def set_log(func):
        DeviceClipSwitcherComponent.log_message = func


    def __init__(self):
        ControlSurfaceComponent.__init__(self)
        self._switch_button = None
        self._view_control = ViewControlComponent()
        self.log_message("Created DeviceClipSwitcherComponent!")
        return

    def disconnect(self):
        if self._switch_button != None:
            self._switch_button.remove_value_listener(self._switch_value)
            self._switch_button = None
        return

    def set_device_clip_switch_button(self, button):
        identify_sender = True
        if self._switch_button != None:
            self._switch_button.remove_value_listener(self._switch_value)
        self._switch_button = button
        if self._switch_button != None:
            self._switch_button.add_value_listener(self._switch_value, identify_sender)
        self.update()
        return


    def on_enabled_changed(self):
        self.update()


    def _switch_value(self, value, sender):
        if self.is_enabled() and (not sender.is_momentary() or value != 0):
            app_view = self.application().view
            if app_view.is_view_visible('Detail/Clip'):
                self._view_control.show_view('Detail/DeviceChain')
            elif app_view.is_view_visible('Detail/DeviceChain'):
                self._view_control.show_view('Detail/Clip')
            else:
                pass
        return
