# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Axiom_AIR_Mini32/DeviceNavComponent.py
# Compiled at: 2018-04-23 20:27:04
from __future__ import absolute_import, print_function, unicode_literals
import Live
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent

class DeviceNavComponent(ControlSurfaceComponent):
    u""" Component that can navigate the selection of devices """

    @staticmethod
    def set_log(func):
        DeviceNavComponent.log_message = func

    def __init__(self):
        ControlSurfaceComponent.__init__(self)
        self._left_button = None
        self._right_button = None
        self.log_message("Created DeviceNavComponent!")
        return


    def disconnect(self):
        if self._left_button != None:
            self._left_button.remove_value_listener(self._nav_value)
            self._left_button = None
        if self._right_button != None:
            self._right_button.remove_value_listener(self._nav_value)
            self._right_button = None
        return


    def set_device_nav_buttons(self, left_button, right_button):
        identify_sender = True
        if self._left_button != None:
            self._left_button.remove_value_listener(self._nav_value)
        self._left_button = left_button
        if self._left_button != None:
            self._left_button.add_value_listener(self._nav_value, identify_sender)
        if self._right_button != None:
            self._right_button.remove_value_listener(self._nav_value)
        self._right_button = right_button
        if self._right_button != None:
            self._right_button.add_value_listener(self._nav_value, identify_sender)
        self.update()
        return


    def on_enabled_changed(self):
        self.update()


    def _nav_value(self, value, sender):
        if self.is_enabled() and (not sender.is_momentary() or value != 0):
            app_view = self.application().view
            if not app_view.is_view_visible('Detail') or not app_view.is_view_visible('Detail/DeviceChain'):
                app_view.show_view('Detail')
                app_view.show_view('Detail/DeviceChain')
            else:
                modifier_pressed = True
                directions = Live.Application.Application.View.NavDirection
                if sender == self._right_button:
                    direction = directions.right
                elif sender == self._left_button:
                    direction = directions.left

                app_view.scroll_view(direction, 'Detail/DeviceChain', not modifier_pressed)
