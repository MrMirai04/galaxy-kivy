from kivy.config import Config
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')
from kivy import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics import Color, Line
from kivy.metrics import dp
from kivy.properties import NumericProperty, Clock, BooleanProperty
from kivy.uix.widget import Widget


class MainWidget(Widget):
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_NB_LINES = 6
    V_LINES_SPACING = .25
    vertical_lines = []

    H_NB_LINES = 20
    H_LINES_SPACING = .1
    horizontal_lines = []

    current_offset_y = 0
    SPEED = 4

    SPEED_X = 12
    current_offset_x = 0

    current_speed = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # super(MainWidget, self).__init__(**kwargs)
        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
            self._keyboard.bind(on_key_up=self._on_keyboard_up)

        self.init_vertical_lines()
        self.init_horizontal_lines()
        Clock.schedule_interval(self.update, 1/60)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard.unbind(on_key_up=self._on_keyboard_up)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'a':
            self.current_speed = self.SPEED_X
        elif keycode[1] == 'd':
            self.current_speed = -self.SPEED_X

    def _on_keyboard_up(self, keyboard, keycode):
        self.current_speed = 0


    def on_parent(self, widget, parent):
        pass

    def on_size(self, *args):
        # self.perspective_point_x = self.width/2
        # self.perspective_point_y = self.height * .75
        self.update_vertical_lines()
        self.update_horizontal_lines()

    def on_perspective_point_x(self, widget, value):
        pass

    def on_perspective_point_y(self, widget, value):
        pass

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)

            for n in range(self.V_NB_LINES):
                self.vertical_lines.append(Line())

            '''
            self.line = Line(
                points=[dp(100), dp(0), dp(100), dp(100)]
            )
            '''

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)

            for n in range(self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_vertical_lines(self):
        # take half width from window (self.width/2)
        # V_LINES_SPACING * self.width is exactly one cell
        # the central_line_x is now 1/2 a cell to the right
        central_line_x = int(self.width / 2) + \
                         (self.V_LINES_SPACING * self.width)/2
        # spacing is equivalent to exactly one cell's width
        spacing = self.V_LINES_SPACING * self.width

        # offset is half the amount of vertical lines
        offset = (-1) * int(self.V_NB_LINES/2)
        for n in range(self.V_NB_LINES):
            # line_x is primarily dependent on the variable offset
            # as offset is half the amount of vertical lines
            # half the lines are rendered before central_line_x
            line_x = int(central_line_x + offset*spacing + self.current_offset_x)

            # convert 2D to 2.5D (optional)
            # y-values are from bottom to top

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[n].points = [x1, y1, x2, y2]

            # goes on to render the next vertical line
            offset += 1
            
    def update_horizontal_lines(self):
        # central_line_x is in the middle of the screen
        central_line_x = int(self.width/2)

        # spacing is equivalent to exactly one cell's width
        spacing = self.V_LINES_SPACING * self.width

        # offset is half the amount of vertical lines - half a line
        # of 8 it is 3.5
        offset = (-1) * int(self.V_NB_LINES/2) + .5

        # x_min and x_max are determined s.t. the horizontal lines
        # occupy exactly the coverage of the vertical lines
        x_min = central_line_x+self.current_offset_x+offset*spacing
        x_max = central_line_x+self.current_offset_x-offset*spacing

        # for the amount of space between each horizontal line
        # the multiplication with self.height makes it responsive
        spacing_y = self.H_LINES_SPACING*self.height

        for n in range(self.H_NB_LINES):
            line_y = n*spacing_y-self.current_offset_y

            x1, y1 = self.transform(x_min, line_y)
            x2, y2 = self.transform(x_max, line_y)
            self.horizontal_lines[n].points = [x1, y1, x2, y2]

    def transform(self, x, y):
        # return self.transform_2D(x, y)
        return self.transform_perspective(x, y)

    def transform_2D(self, x, y):
        return int(x), int(y)

    def transform_perspective(self, x, y):
        lin_y = y * self.perspective_point_y / self.height
        if lin_y > self.perspective_point_y:
            lin_y = self.perspective_point_y

        diff_x = x-self.perspective_point_x
        diff_y = self.perspective_point_y-lin_y
        factor_y = diff_y/self.perspective_point_y
        factor_y = pow(factor_y, 4)

        proportion_y = diff_y/self.perspective_point_y

        tr_x = self.perspective_point_x + diff_x*factor_y
        tr_y = self.perspective_point_y-factor_y*self.perspective_point_y

        return int(tr_x), int(tr_y)

    def on_touch_down(self, touch):
            if touch.x < self.width/4:
                self.current_speed += self.SPEED_X
            if touch.x > self.width*.75:
                self.current_speed -= self.SPEED_X
    def on_touch_up(self, touch):
        self.current_speed = 0

    def is_desktop(self):
        if platform in ('linux', 'win', 'macosx'):
            return True
        else:
            return False


    def update(self, delta_time):
        time_factor = delta_time*60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.current_offset_y += self.SPEED * time_factor

        # Reset after exactly one tile has gone off screen
        spacing_y = self.H_LINES_SPACING * self.height
        if self.current_offset_y >= spacing_y:
            self.current_offset_y -= spacing_y

        # Move vertical lines to the left or right
        # depending on user input
        self.current_offset_x += self.current_speed * time_factor


class GalaxyApp(App):
    pass


if __name__ == '__main__':
    GalaxyApp().run()