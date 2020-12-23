import unicodecsv as csv
from os.path import join, dirname, exists
from datetime import datetime
from string import punctuation
from copy import deepcopy
from os.path import basename
from threading import Thread
import ast
from re import search
from functools import partial
from collections import defaultdict
from spello.model import SpellCorrectionModel
from kivy.config import Config

Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('graphics', 'minimum_width', '999')
Config.set('graphics', 'minimum_height', '721')
Config.set('graphics', 'width', '999')
Config.set('graphics', 'height', '721')

from kivy.core.window import Window
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from plyer import filechooser
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.scatterlayout import ScatterLayout
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.graphics.vertex_instructions import RoundedRectangle
from kivy.uix.widget import WidgetException
import kivy.metrics

ver = "v3.4.1"
word_theme = [[42 / 255, 87 / 255, 154 / 255, 1], [235 / 255, 245 / 255, 250 / 255, 1], [230 / 255, 230 / 255, 230 / 255, 1]]
excel_theme = [[33/255,  115/255,  70/255,  1], [235 / 255, 245 / 255, 250 / 255, 1], [230 / 255, 230 / 255, 230 / 255, 1]]
powerpoint_theme = [[183/255,  71/255,  42/255,  1], [235 / 255, 245 / 255, 250 / 255, 1], [230 / 255, 230 / 255, 230 / 255, 1]]
teams_theme = [[70/255,  71/255,  117/255,  1], [235 / 255, 245 / 255, 250 / 255, 1], [230 / 255, 230 / 255, 230 / 255, 1]]
Access_theme = [[164/255,  55/255,  58/255,  1], [235 / 255, 245 / 255, 250 / 255, 1], [230 / 255, 230 / 255, 230 / 255, 1]]
onedrive_theme = [[20/255,  144/255,  223/255,  1], [235 / 255, 245 / 255, 250 / 255, 1], [230 / 255, 230 / 255, 230 / 255, 1]]
current_theme = [[42 / 255, 87 / 255, 154 / 255, 1], [235 / 255, 245 / 255, 250 / 255, 1], [230 / 255, 230 / 255, 230 / 255, 1]]
editor = None
window_instance = None
an_cell_on_focus = False
args = []
c = 0
global_font_size = 15
curr_col = None
col_c = None


def load_config():
    global args
    with open(join(dirname(__file__), "config.txt"), 'r', encoding='utf-8') as cfg:
        args = []
        for line in cfg:
            line = line.strip("\n")
            line = line.split("=")[1]

            if ',' in line:
                temp = line.split(',')
                args.append(temp)

            else:
                args.append(line)


def save_to_do(sc, sc2):

    if len(editor.do) > 20:
        editor.do.pop(0)

    sc_list = sc[:]
    sc2_list = sc2[:]

    tt_list = []
    for i in editor.title_grid.children:
        tt_list.append(i.size[:])

    editor.do.append([deepcopy(sc_list), deepcopy(sc2_list), deepcopy(tt_list)])


load_config()
sp = SpellCorrectionModel(language='en')
sp.load(join(dirname(__file__), args[4] + ".pkl"))


class JoTitle(GridLayout):
    text = StringProperty(None)
    spacing = [1, 0]

    def __init__(self, **kw):
        super().__init__(**kw)
        self.size_hint = [None, None]
        self.cols = 3
        self.add_widget(JoButtonLabel(text=self.text, font_name='MEIRYO.TTC', font_size='15sp',
                                      size_hint=[1, None], height=35))

        def color_switch(ins):
            if ins.background_color == current_theme[0]:

                for i in editor.title_grid.children:
                    i.children[1].background_color=current_theme[0]

                ins.background_color = [0, 0, 0, 1]
                editor.dup_col = len(editor.title_grid.children) + (editor.title_grid.children.index(ins.parent) * -1)
                Clock.schedule_once(lambda dt: editor.loading("Marking Duplicates...", editor.mark_duplicates))

        self.add_widget(JoButtonLabel(width=20, text='D', size_hint=[None, None], height=35, on_release=lambda a: color_switch(a)))
        self.add_widget(JoButtonLabel(width=20, text='>', size_hint=[None, None], height=35))


class JoScatterLayout(ScatterLayout):
    title = StringProperty(None)
    theme = ListProperty(current_theme)
    close = BooleanProperty(True)

    def __init__(self, **kw):
        super().__init__(**kw)

        strip_height = 30
        background_height = self.height - strip_height

        with self.canvas.before:

            #Borders
            Color(rgba=self.theme[0])
            Rectangle(size=(self.width + 4, background_height + 4), pos=(self.x-2, self.y-2))
            RoundedRectangle(size=(self.width + 4, strip_height + 4), pos=(self.x - 2, self.y - 2 + background_height), radius=[16, 16, 0, 0])

            #Strip
            Color(rgba=self.theme[0])
            RoundedRectangle(size=(self.width, strip_height), pos=(self.x, self.y + background_height), radius=[16, 16, 0, 0])

            #Background
            Color(rgba=self.theme[1])
            Rectangle(size=(self.width, background_height), pos=(self.x, self.y))

        if self.close:
            self.add_widget(JoButtonLabel(text="X", halign="right", size_hint=(None, None), size=(15, strip_height*0.6), pos=(self.x + self.width - 25, self.y + background_height + (strip_height/6)), on_release=lambda a: editor.for_float.remove_widget(self)))

        self.add_widget(Label(text=self.title, color=self.theme[1], font_size=17, size_hint=(None, None), pos=(self.x, self.y + background_height-35)))

    def on_touch_move(self, touch):
        super().on_touch_move(touch)
        self.pos_hint = {}


class JoDropDown(DropDown):
    addition = NumericProperty(None)
    auto_width = False

    def _reposition(self, *largs):
        # calculate the coordinate of the attached widget in the window
        # coordinate system
        win = self._win
        widget = self.attach_to
        if not widget or not win:
            return
        wx, wy = widget.to_window(*widget.pos)
        wright, wtop = widget.to_window(widget.right, widget.top)

        # set width and x
        if self.auto_width:
            self.width = wright - wx

        # ensure the dropdown list doesn't get out on the X axis, with a
        # preference to 0 in case the list is too wide.
        # x = wx
        x = widget.to_window(*widget.cursor_pos)[0]
        if x + self.width > win.width:
            x = win.width - self.width
        if x < 0:
            x = 0
        obj = kivy.metrics.Metrics
        self.x = x - (self.width * 72/obj.dpi) - 4

        # determine if we display the dropdown upper or lower to the widget
        if self.max_height is not None:
            height = min(self.max_height, self.container.minimum_height)
        else:
            height = self.container.minimum_height

        h_bottom = wy - height
        h_top = win.height - (wtop + height)
        if h_bottom > 0:
            self.top = wy
            self.height = height
        elif h_top > 0:
            self.y = wtop
            self.height = height
        else:
            # none of both top/bottom have enough place to display the
            # widget at the current size. Take the best side, and fit to
            # it.

            if h_top < h_bottom:
                self.top = self.height = wy
            else:
                self.y = wtop
                self.height = win.height - wtop


class FindTextInput(TextInput):
    pass


class JoButton(Button):
    theme = current_theme


class ReplaceButton(Button):
    theme = current_theme


class JoButtonLabel(Button):
    theme = current_theme
    extra = ListProperty(None)

    def on_touch_move(self, touch):
        super().on_touch_move(touch)
        global curr_col
        global col_c

        if (col_c == self or self.collide_point(*touch.pos)) and 'JoTitle' in str(self.parent) and self.parent.children.index(self) == 0 and self.state == "down":
            col_c = self

            if (touch.ppos[0] - self.parent.x) > 110:
                self.parent.width = touch.ppos[0] - self.parent.x

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        global col_c
        if col_c == self and 'JoTitle' in str(self.parent) and self.parent.children.index(self) == 0:

            def apply():
                col_num = (editor.title_grid.children.index(self.parent) * -1) - 1

                for i in range(col_num, len(editor.scroll.data), editor.row_len):
                    size = self.parent.size[:]
                    editor.scroll.data[i]["dyn_size"] = size


                editor.scroll.refresh_from_data()

            editor.loading("Applying changes...", apply)
            col_c = None


    def on_release(self):
        super().on_release()
        if self.parent in editor.title_grid.children and self.parent.children.index(self) == 2:

            if self.background_color != [0, 0, 0, 1]:

                for i in editor.title_grid.children:
                    i.children[2].background_color = current_theme[0]

                self.background_color = [0, 0, 0, 1]
                editor.found_list = []
                editor.find_col = ((editor.title_grid.children.index(self.parent) - (editor.row_len - 1)) * -1)
                print(editor.find_col)

        if self.text == "No.":
            scatter = JoScatterLayout(pos_hint={"x": editor.width/2 - 150/2, "y": editor.height/2 - 58/2}, size_hint=(None, None), size=(150, 58), title="")
            layout = GridLayout(cols=2, size_hint=(1, None), height=58 - 30, spacing=[0, 2], pos=(scatter.x, scatter.y))
            goinput = JoTextInput(hint_text="Enter an row.", size_hint=(1, 1), halign="center", multiline=False, on_text_validate=lambda a: editor.calculate_location(int(a.text)-1) if not a.text == "" else editor.calculate_location(0))
            layout.add_widget(JoButtonLabel(text="Go To", font_name='MEIRYO.TTC', size_hint=(None, 1), width=50, on_press=lambda a: editor.calculate_location(int(goinput.text)-1) if not goinput.text == "" else editor.calculate_location(0)))
            layout.add_widget(goinput)
            scatter.add_widget(layout)
            editor.for_float.add_widget(scatter)

        elif self.last_touch.button == "right" and self.extra:
            titles = [i + ": " for i in editor.title_grid2.children[0].extra]
            extra_data = self.extra
            details = [x for i in zip(titles, extra_data) for x in i]
            scatter_height = (int(len(details) / 2) * 32) + 30
            layout = GridLayout(cols=2, size_hint=(1, None), height=scatter_height - 30, spacing=[0, 2])

            for i in enumerate(details):
                if ": " in i[1]:
                    layout.add_widget(Label(text=i[1], font_size=12, font_name='MEIRYO.TTC', size_hint=(None, 1), width=120, color=(0, 0, 0, 1)))

                else:
                    layout.add_widget(JoTextInput(multiline=False, text=i[1], size_hint=(1, None), height=30, font_size=12, font_name='MEIRYO.TTC', index=int((i[0]-1)/2)+1))

            needed_width = 150 + len(sorted(self.extra, key=lambda s: len(s))[-1]) * 7

            if needed_width < 300:
                needed_width = 300

            scatter = JoScatterLayout(size_hint=(None, None), size=(needed_width, scatter_height), title="Details " + self.text)
            scatter.add_widget(layout)
            editor.for_float.add_widget(scatter)

        elif self.last_touch.button == "left" and self in editor.rows_grid.children:

            current_label = int(self.text) - 1

            if self.background_color == editor.theme[0]:
                editor.scroll2.data[current_label]['background_color'] = [0, 0, 0, 1]
                self.background_color = [0, 0, 0, 1]
                editor.marked_rows.append(current_label)

            elif self.background_color == [0, 0, 0, 1]:
                editor.scroll2.data[current_label]['background_color'] = editor.theme[0]
                self.background_color = editor.theme[0]
                editor.marked_rows.remove(current_label)

            elif self.background_color == [128/255, 128/255, 128/255, 1]:
                editor.calculate_location(editor.duplicates_list[current_label][0])

            else:
                for dup in editor.duplicates_list:
                    if current_label in editor.duplicates_list[dup]:
                        editor.duplicates_list[dup].remove(current_label)
                        editor.duplicates_list[dup].insert(0, current_label)
                        editor.calculate_location(dup)


class JoTextInput(TextInput):
    theme = current_theme
    global_font_size = 15
    index = NumericProperty(None)
    extra_index = NumericProperty(None)
    font_size = NumericProperty(global_font_size)
    indices = []
    ct = ""
    text_validate_unfocus = False
    suggestions = JoDropDown()

    def populate_duplicate(self, btn_ins):
        label = int(self.index / editor.row_len)
        for i in editor.duplicates_list[label]:
            cell_pos = ((i * editor.row_len) + (editor.dup_col - 1))
            editor.scroll.data[cell_pos]['text'] = self.text

        self.focus = False

        del editor.do[editor.do_index + 1:]
        save_to_do(editor.scroll.data, editor.scroll2.data)
        editor.do_index = len(editor.do) - 1

        editor.scroll.refresh_from_data()
        editor.for_float.remove_widget(btn_ins.parent.parent.parent.parent)

    def sug_replace(self):
        if len(self.indices) == 2:
            self.text = self.text[:self.indices[0]] + self.ct + self.text[self.indices[1] + 1:]

        else:
            self.text = self.text[:self.indices[0]] + self.ct

        self.suggestions.dismiss()
        editor.data[self.index]['text'] = self.text
        self.focus = False
        self.focus = True

    def _on_focus(self, instance, value, *largs):
        super()._on_focus(instance, value, *largs)
        global an_cell_on_focus

        if value:
            an_cell_on_focus = True

        else:
            an_cell_on_focus = False

    def on_text_validate(self):
        super().on_text_validate()
        if self.index and self.suggestions.children[0].children:
            self.sug_replace()

        elif "JoScatterLayout" in str(self.parent):
            if self.text == "":
                self.text = "1"
            editor.calculate_location(int(self.text)-1)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        super().keyboard_on_key_down(window, keycode, text, modifiers)

        if keycode[1] == "spacebar":
            self.indices = []
            self.suggestions.dismiss()

        if keycode[1] == "insert":
            text = "You are about to apply the changes made to this cell for all it's duplicates, are you sure you want to continue?"
            editor.warning(text, self.populate_duplicate)

    def keyboard_on_key_up(self, window, keycode):
        super().keyboard_on_key_up(window, keycode)

        if self.index:

            if "RecycleGridLayout" in str(self.parent):
                editor.scroll.data[self.index]['text'] = self.text
                cur = self.cursor_index()
                self.indices = []
                word = []

                if self.text != "" and self.text[cur-1] != punctuation + " " and cur != 0:

                    while True:

                        if cur != 0 and self.text[cur-1] not in punctuation + " ":
                            word.insert(0, self.text[cur-1])
                            cur -= 1
                        else:
                            self.indices.append(cur)
                            break

                    cur = self.cursor_index()

                    while True:

                        if cur != len(self.text) and self.text[cur] not in punctuation + " ":
                            word.append(self.text[cur])
                            cur += 1

                        else:
                            if cur != len(self.text):
                                self.indices.append(cur-1)
                            break

                    word = "".join(word)
                    self.ct = sp.spell_correct(word)['spell_corrected_text']

                    if self.ct != word:
                        btn = ReplaceButton(text=self.ct, font_name='MEIRYO.TTC', size_hint=(None, None), height=20, width=len(word) * 14, halign="center")
                        btn.bind(on_release=lambda b: self.suggestions.select(self.ct))
                        self.suggestions.width = btn.width
                        self.suggestions.clear_widgets()
                        self.suggestions.add_widget(btn)

                        self.suggestions.bind(on_select=self.sug_replace)

                        try:
                            self.suggestions.open(self)

                        except WidgetException:
                            pass

                    else:

                        try:
                            self.suggestions.dismiss()

                        except WidgetException:
                            pass

            elif self.parent != editor.cells_grid:
                row = int(self.parent.parent.parent.title[-1]) - 1
                editor.scroll2.data[row]['extra'][self.index - 1] = self.text

                for i in editor.rows_grid.children:
                    if i.text == str(row+1):
                        i.extra[self.index - 1] = self.text


class CsvEditor(Widget):
    theme = ListProperty(current_theme)

    cells_grid = ObjectProperty(None)
    title_grid = ObjectProperty(None)
    title_grid2 = ObjectProperty(None)
    rows_grid = ObjectProperty(None)
    for_float = ObjectProperty(None)
    scroll = ObjectProperty(None)
    scroll2 = ObjectProperty(None)
    find_button = ObjectProperty(None)
    buttons_grid = ObjectProperty(None)
    open = ObjectProperty(None)
    save = ObjectProperty(None)
    save_as = ObjectProperty(None)
    find_textinput = ObjectProperty(None)
    find_textinput2 = ObjectProperty(None)
    find_next = ObjectProperty(None)
    find_prev = ObjectProperty(None)
    replace_all = ObjectProperty(None)

    do_index = 0
    do = []
    row_len = 0
    row_num = 0
    marked_rows = []
    file_path = ""
    found_list = []
    duplicates_list = []
    current_find = ""
    found_item = 0
    current_row = 0
    current_mins = 0
    current_secs = 0
    data = []
    data2 = []
    for_dup = []
    dup_col = 0
    find_col = 0
    title_row = []
    displayed_titles = []


    def change_theme(self, theme):
        global current_theme
        current_theme = theme
        self.theme = theme
        JoScatterLayout.theme = theme
        JoTextInput.theme = theme
        JoButton.theme = theme
        JoButtonLabel.theme = theme
        ReplaceButton.theme = theme
        self.open.color = theme[0]
        self.save.color = theme[0]
        self.save_as.color = theme[0]
        self.find_button.color = theme[0]
        self.find_next.color = theme[0]
        self.find_prev.color = theme[0]
        self.replace_all.color = theme[0]

        try:
            for child in self.scroll.data:
                child['background_color'] = theme[0]

            for child in self.scroll2.data:
                if child['background_color'] != [128/255, 128/255, 128/255, 1] and child['background_color'] != [211/255, 211/255, 211/255, 1] and child['background_color'] != [0, 0, 0, 1]:
                    child['background_color'] = theme[0]

            for child in self.title_grid.children:
                for title in child.children:
                    if title.background_color != [0, 0, 0, 1]:
                        title.background_color = theme[0]

            self.title_grid2.children[0].background_color = theme[0]
            self.scroll.refresh_from_data()
            self.scroll2.refresh_from_data()

        except IndexError:
            pass

    def on_file_drop(self, window, drag_file_path):
        Clock.schedule_once(lambda dt: self.load(drag=drag_file_path.decode('utf-8')), 0)

    def load(self, drag=""):

        now = datetime.now()
        self.current_mins = int(now.strftime("%M"))
        self.current_secs = int(now.strftime("%S"))
        original_len = 0

        if drag == "":

            try:
                self.file_path = filechooser.open_file(title="Pick a CSV file..", filters=[("Comma-separated Values", "*.csv")])[0]

            except IndexError:
                pass

        else:
            self.file_path = drag

        if self.file_path != '':

            f = open(self.file_path, 'rb')

            sizes = []
            if self.title_grid.children:
                for i in self.title_grid.children:
                    sizes.append(i.size)

            while len(self.title_grid.children) != 0:
                self.title_grid.remove_widget(self.title_grid.children[0])

            window_instance.title = 'Jo\'s PyCSV ' + ver + ' - ' + basename(self.file_path)
            self.scroll.scroll_y = 1
            self.scroll.scroll_x = 0
            self.cells_grid.clear_widgets()
            self.rows_grid.clear_widgets()
            self.title_grid.clear_widgets()
            self.title_grid2.clear_widgets()
            self.scroll.refresh_from_data()
            self.scroll2.refresh_from_data()

            self.found_list = []
            self.found_item = 0
            self.do = []
            self.data = []
            self.data2 = []

            self.scroll.data = self.data
            self.scroll2.data = self.data2

            self.row_num = 0
            load_config()

            def load_data():
                if not exists(self.file_path + ".pycsv"):
                    global original_len

                    for row in csv.reader(f, encoding='utf-8'):

                        if self.row_num == 0:
                            original_len = len(row)
                            if args[0]:

                                if int(args[0][-1]) > len(row):
                                    args[0] = ""
                                    self.row_len = len(row)

                                else:
                                    self.row_len = len(args[0])

                            else:
                                self.row_len = len(row)

                            self.title_grid.cols = self.row_len
                            self.cells_grid.cols = self.row_len
                            self.title_grid2.add_widget(JoButtonLabel(text="No.", width=50, height=35,
                                                                      size_hint=[None, None]))

                        while len(row) != original_len:
                            row.append("")

                        if args[0]:
                            extra_data = row[:]

                            if self.row_num == 0:
                                self.title_row = deepcopy(extra_data)

                            for i in sorted(args[0], reverse=True, key=lambda s: int(s)):
                                extra_data.pop(int(i) - 1)

                            if self.row_num == 0:
                                self.title_grid2.children[0].extra = extra_data

                            row = [row[int(i) - 1] for i in args[0]]

                            if self.row_num == 0:
                                self.displayed_titles = row

                        else:
                            extra_data = []


                        if self.row_num != 0:
                            #Adding row numbers
                            self.data2.append({'text': str(self.row_num), 'width': 50, 'height': 35, 'font_name': 'MEIRYO.TTC', 'font_size': '15sp', 'size_hint': [None, None], 'background_color': self.theme[0]})

                            if args[0]:
                                self.data2[-1]['extra'] = extra_data

                        for i in enumerate(row):

                            if self.row_num == 0:
                                #Adding titles

                                if sizes:

                                    try:
                                        self.title_grid.add_widget(JoTitle(text=i[1], size=sizes[(i[0] * -1) - 1]))

                                    except IndexError:
                                        self.title_grid.add_widget(JoTitle(text=i[1], size=[int(args[3]), 35]))
                                else:
                                    self.title_grid.add_widget(JoTitle(text=i[1], size=[int(args[3]), 35]))

                            else:
                                #Adding cells
                                size = self.title_grid.children[(i[0] * -1) - 1].size[:]

                                self.data.append({'dyn_size': size, 'multiline': False, 'text': i[1], 'font_name': 'MEIRYO.TTC', 'size_hint': [None, None], 'index': len(self.data)})

                                if args[0]:
                                    self.data[-1]['extra_index'] = int(args[0][i[0]])-1

                        self.row_num += 1

                    self.find_col = self.row_len - 1
                    self.title_grid.children[(self.find_col * -1) - 1].children[2].background_color = [0, 0, 0, 1]

                else:
                    with open(self.file_path + ".pycsv", 'r', encoding='utf-8') as df:
                        lines = []
                        for i in df:
                            lines.append(i)

                        self.title_row = ast.literal_eval(lines[0])
                        dc = ast.literal_eval(lines[1])
                        self.title_grid2.add_widget(JoButtonLabel(text="No.", width=50, height=35,
                                                                  size_hint=[None, None]))

                        for t in enumerate(dc):
                            self.title_grid.add_widget(JoTitle(text=t[1], size=ast.literal_eval(lines[2])[(t[0] * 1) - 1]))

                        self.title_grid2.children[0].extra = ast.literal_eval(lines[3])
                        self.args = ast.literal_eval(lines[4])

                        temp = lines[5].split(",")
                        self.row_num = int(temp[0])
                        self.row_len = int(temp[1])
                        self.find_col = int(temp[2].strip("\n"))

                        self.title_grid.cols = self.row_len
                        self.cells_grid.cols = self.row_len
                        self.title_grid.children[self.find_col].children[2].background_color = [0, 0, 0, 1]
                        self.duplicates_list = ast.literal_eval(lines[6])
                        self.marked_rows = ast.literal_eval(lines[7])
                        self.data2 = ast.literal_eval(lines[8])
                        self.data = ast.literal_eval(lines[9])


                self.scroll.data = self.data
                self.scroll2.data = self.data2

            self.loading("Loading File...", load_data)

            Clock.schedule_once(lambda dt: Clock.schedule_once(lambda dt2: save_to_do(self.scroll.data, self.scroll2.data), 0), 0)
            Clock.schedule_interval(lambda dt: self.auto_save(), 1)

    def save_file(self, save_as=False, clean=False):

        if save_as:
            new_path = filechooser.save_file(title="Save As..", filters=["csv"], path=self.file_path)

            if len(new_path) != 0:
                self.file_path = new_path[0]

        if self.file_path != "":

            with open(self.file_path, 'wb+') as f:
                f.truncate(0)
                f.seek(0)
                data = self.child_indexing("dic", textinput_only=False)

                csv_writer = csv.writer(f, encoding='utf-8')
                title = []

                if self.title_grid2.children[0].extra:

                    title = self.title_row

                else:
                    temp = self.title_grid.children[:]
                    temp.reverse()

                    for i in temp:
                        title.append(i.text)

                csv_writer.writerow(title)

                for i in data:

                    if self.title_grid2.children[0].extra:
                        row = deepcopy(i[0]['extra'])

                        for child in i[1:]:
                            row.insert(child['extra_index'], child['text'])

                    else:
                        row = []

                        for child in i[1:]:
                            row.append(child['text'])

                    csv_writer.writerow(row)

            if not clean:
                with open(self.file_path + ".pycsv", 'w+', encoding='utf-8') as df:
                    df.truncate(0)
                    df.seek(0)

                    sizes = []
                    for i in self.title_grid.children:
                        sizes.append(i.size)

                    df.write(str(title) + "\n")
                    df.write(str(self.displayed_titles) + "\n")
                    df.write(str(sizes) + "\n")
                    df.write(str(self.title_grid2.children[0].extra) + "\n")
                    df.write(str(args) + "\n")
                    df.write(f"{str(self.row_num)},{str(self.row_len)},{str(self.find_col)}\n")
                    df.write(str(self.duplicates_list) + "\n")
                    df.write(str(self.marked_rows) + "\n")
                    df.write(str(self.scroll2.data) + "\n")
                    df.write(str(self.scroll.data) + "\n")

    def child_indexing(self, ind_type, textinput_only=True):

        obj_data = []
        dic_data = []
        if len(self.cells_grid.children) != 0:

            if textinput_only:
                row_len = self.row_len

            else:
                row_len = self.row_len+1

            if ind_type == "obj":
                cells_inv = self.cells_grid.children[:]
                cells_inv.reverse()

                rows_inv = self.rows_grid.children[:]
                rows_inv.reverse()

                for child in cells_inv:

                    if textinput_only:
                        obj_data.append(child)

                    else:
                        if child.index % self.row_len == 0:
                            obj_data.append(rows_inv[int(child.index / self.row_len)])

                        obj_data.append(child)

                for i in range(0, int(len(obj_data) / row_len)):
                    temp = obj_data[0:row_len]
                    del obj_data[0:row_len]
                    obj_data.append(temp)

                return obj_data

            elif ind_type == "dic":

                for child in self.scroll.data:

                    if textinput_only:
                        dic_data.append(child)

                    else:

                        if child['index'] % self.row_len == 0:
                            dic_data.append(self.scroll2.data[int(child['index']/self.row_len)])

                        dic_data.append(child)

                for i in range(0, int(len(dic_data) / row_len)):
                    temp = dic_data[0:row_len]
                    del dic_data[0:row_len]
                    dic_data.append(temp)

                return dic_data

    def calculate_location(self, row):

        scroll = self.scroll.convert_distance_to_scroll(0, row * (self.rows_grid.children[0].height + 2))[1]
        self.scroll.scroll_y = 1 - scroll

    def populate_duplicates(self, btn_ins):

        for orig in self.duplicates_list:
            cell_text = self.scroll.data[(orig * self.dup_col) + 1]['text']
            for dup in self.duplicates_list[orig]:
                cell_pos = (dup * self.dup_col) + 1
                self.scroll.data[cell_pos]['text'] = cell_text

        del self.do[self.do_index + 1:]
        save_to_do(self.scroll.data, self.scroll2.data)
        self.do_index = len(self.do) - 1

        self.scroll.refresh_from_data()
        self.for_float.remove_widget(btn_ins.parent.parent.parent.parent)

    def font_resize(self, reverse=False):

        if not reverse:
            def enlarge():
                global global_font_size

                global_font_size += 1
                for i in self.title_grid.children:
                    w, h = i.size
                    i.size = (w + 20, h + 2)

                for i in self.scroll.data:
                    w, h = i["dyn_size"]
                    i["dyn_size"] = (w + 20, h + 2)
                    i["font_size"] = global_font_size

                for i in self.scroll2.data:
                    i["height"] += 2

                self.scroll.refresh_from_data()
                self.scroll2.refresh_from_data()

            if not global_font_size > 25:
                self.loading("Applying Changes", enlarge)

        else:
            def reduce():
                global global_font_size

                global_font_size -= 1
                for i in self.title_grid.children:
                    w, h = i.size
                    i.size = (w - 20, h - 2)

                for i in self.scroll.data:
                    w, h = i["dyn_size"]
                    i["dyn_size"] = (w - 20, h - 2)
                    i["font_size"] = global_font_size

                for i in self.scroll2.data:
                    i["height"] -= 2

                self.scroll.refresh_from_data()
                self.scroll2.refresh_from_data()

            if not global_font_size < 11:
                self.loading("Applying Changes", reduce)

    def replace_word(self, btn_ins=None):
        data = self.child_indexing("dic")
        for i in data:

            if self.find_textinput.text in i[self.find_col]['text']:
                i[self.find_col]['text'] = i[self.find_col]['text'].replace(self.find_textinput.text, self.find_textinput2.text)

        del self.do[self.do_index + 1:]
        save_to_do(self.scroll.data, self.scroll2.data)
        self.do_index = len(self.do) - 1

        self.scroll.refresh_from_data()

        if btn_ins is not None:
            self.for_float.remove_widget(btn_ins.parent.parent.parent.parent)

    def find_word(self):

        if self.find_textinput.text != "":
            self.found_list = []
            self.current_find = self.find_textinput.text
            data = self.child_indexing("dic")
            print(self.find_col)
            self.found_list = [[num, row[self.find_col]['index']] for num, row in enumerate(data) if self.find_textinput.text in row[self.find_col]['text']]

        else:
            pass

    def find_order(self, direction):

        if len(self.found_list) == 0 or self.find_textinput.text != self.current_find:
            self.find_word()

        if direction == "up":
            self.found_item -= 1
        elif direction == "down":
            self.found_item += 1

        if len(self.found_list) != 0:
            if self.found_item > len(self.found_list) - 1:
                self.found_item = 0

            elif self.found_item < -len(self.found_list):
                self.found_item = -1


            self.calculate_location(self.found_list[self.found_item][0])

            def operate(timing):
                for child in self.cells_grid.children:
                    if child.index == self.found_list[self.found_item][1]:
                        child.focus = True
                        s = child.text.index(self.current_find)
                        e = s + len(self.current_find)

                        if s == e:
                            e += 1

                        child.select_text(s, e)

            Clock.schedule_once(operate)

    def auto_save(self):
        global c
        if not args[2]:
            c = 0
        else:
            if c == int(args[2]):
                c = 0

        now = datetime.now()
        mins = int(now.strftime("%M"))
        secs = int(now.strftime("%S"))
        passed_mins = int(mins - self.current_mins)
        if passed_mins % int(args[1]) == 0 and secs == 0:
            name = basename(self.file_path)
            self.file_path = self.file_path.replace(name, name.replace(".csv", ".csv.bak" + str(c)))
            self.save_file(save_as=False, clean=True)
            self.file_path = self.file_path.replace(name.replace(".csv", ".csv.bak" + str(c)), name)
            c += 1

    def mark_duplicates(self):

        if self.duplicates_list:
            for i in self.scroll2.data:
                if i['background_color'] != self.theme[0] and i['background_color'] != [0, 0, 0, 1]:
                    i['background_color'] = self.theme[0]

            self.duplicates_list = []

        for_dup = [[i, self.scroll.data[(self.row_len * i) + (self.dup_col - 1)]['text']] for i in range(0, int(self.scroll2.data[-1]['text']))]

        d = defaultdict(list)
        for i, item in enumerate(for_dup):

            if len(d[item[1]]) == 0:
                d[item[1]].append(item[0])

            else:
                d[item[1]].append(i)

        self.duplicates_list = {v[0]: v[1:] for k, v in d.items() if len(v) > 1}

        for dup in self.duplicates_list:
            self.scroll2.data[dup]['background_color'] = [128/255, 128/255, 128/255, 1]

            for i in self.duplicates_list[dup]:
                self.scroll2.data[i]['background_color'] = [211/255, 211/255, 211/255, 1]

        self.scroll2.refresh_from_data()

    def warning(self, warn, func):
        scatter = JoScatterLayout(pos_hint={"x": editor.width / 2 - 400 / 2, "y": editor.height / 2 - 150 / 2}, size_hint=(None, None), size=(400, 150), title="Warning")
        layout = GridLayout(cols=1, size_hint=(0.99, None), height=150 - 32, spacing=[0, 2], pos=(scatter.x + 2, scatter.y + 2))
        layout.add_widget(Label(valign="bottom", halign="center", font_size=14, font_name='MEIRYO.TTC', text=warn, color=[0, 0, 0, 1], text_size=(400, None)))
        sublayout = GridLayout(cols=2, size_hint_y=None, height=40, spacing=[2, 0])
        sublayout.add_widget(JoButtonLabel(text="Yes", font_name='MEIRYO.TTC', size_hint=(1, 1), on_release=func))
        sublayout.add_widget(JoButtonLabel(text="No", font_name='MEIRYO.TTC', size_hint=(1, 1), on_release=lambda a: self.for_float.remove_widget(scatter)))
        layout.add_widget(sublayout)
        scatter.add_widget(layout)
        self.for_float.add_widget(scatter)

    def loading(self, warn, func, double=False):
        scatter = JoScatterLayout(pos_hint={"x": editor.width / 2 - 400 / 2, "y": editor.height / 2 - 80 / 2}, size_hint=(None, None), size=(400, 80), title="Loading...", close=False)
        layout = GridLayout(cols=1, size_hint=(0.99, None), height=80 - 32, spacing=[0, 2], pos=(scatter.x + 2, scatter.y + 2))
        layout.add_widget(Label(valign="bottom", halign="center", font_size=14, font_name='MEIRYO.TTC', text=warn, color=[0, 0, 0, 1], text_size=(400, None)))
        scatter.add_widget(layout)
        Clock.schedule_once(lambda dt: self.for_float.add_widget(scatter), -1)

        if double:
            Clock.schedule_once(lambda dt: Clock.schedule_once(lambda dt2: func(), 0), 0)

        else:
            Clock.schedule_once(lambda dt: func(), 0)

        Clock.schedule_once(lambda dt: Clock.schedule_once(lambda dt2: self.for_float.remove_widget(scatter), 0), 0)

    def on_motion(self, a, b, c):

        if c.is_mouse_scrolling:

            for i in self.cells_grid.children:

                if "JoTextInput" in str(i):
                    i.focus = False

    def on_keyboard(self, key, scancode, codepoint, modifier, mod):
        # Undo
        if 'ctrl' in mod and 'shift' not in mod and scancode == 122:
            if self.do:
                if self.do_index != 0:

                    def undo():
                        self.scroll.data = deepcopy(self.do[self.do_index - 1][0][:])
                        self.scroll2.data = deepcopy(self.do[self.do_index - 1][1][:])

                        for i in enumerate(self.do[self.do_index - 1][2]):
                            self.title_grid.children[i[0]].size = i[1]

                        self.do_index -= 1
                        self.scroll.refresh_from_data()
                        self.scroll2.refresh_from_data()

                    self.loading("Undoing...", undo, double=True)

        if 'ctrl' in mod and 'shift' in mod and scancode == 122:
            if self.do:
                if self.do_index != len(self.do) - 1:

                    def redo():
                        self.scroll.data = deepcopy(self.do[self.do_index + 1][0][:])
                        self.scroll2.data = deepcopy(self.do[self.do_index + 1][1][:])

                        for i in enumerate(self.do[self.do_index + 1][2]):
                            self.title_grid.children[i[0]].size = i[1]

                        self.do_index += 1
                        self.scroll.refresh_from_data()
                        self.scroll2.refresh_from_data()

                    self.loading("Redoing...", redo, double=True)

        if 'ctrl' in mod and 'shift' in mod and scancode == 100:

            text = "You are about apply all original texts changes to all their duplicates, are you sure you want to continue?"
            self.warning(text, self.populate_duplicates)

        if 'ctrl' in mod and (scancode == 270 or scancode == 269):

            if scancode == 270:
                self.font_resize()

            else:
                self.font_resize(reverse=True)

    def on_key_down(self, key, scancode, keycode, modifier, numlock):

        def locate(direction, timing):
            global an_cell_on_focus

            if direction == "up":
                if self.scroll.scroll_y < 1:
                    scroll = self.scroll.convert_distance_to_scroll(0, self.rows_grid.children[0].height + 2)[1]
                    self.scroll.scroll_y += scroll

                elif not an_cell_on_focus:
                    self.scroll.scroll_y = 0

            else:
                if self.scroll.scroll_y > 0:
                    scroll = self.scroll.convert_distance_to_scroll(0, self.rows_grid.children[0].height + 2)[1]
                    self.scroll.scroll_y -= scroll

                elif not an_cell_on_focus:
                    self.scroll.scroll_y = 1

            for child in self.cells_grid.children:

                if child.focused:

                    if direction == "up":

                        if child.index > self.row_len:

                            for cell in self.cells_grid.children:

                                if cell.index == child.index - self.row_len:
                                    cell.focus = True

                        else:
                            child.focus = False
                            self.scroll.scroll_y = 0

                        break

                    elif direction == "down":

                        if child.index < ((self.row_num-1) * self.row_len) - (self.row_len - 1):

                            try:
                                for cell in self.cells_grid.children:
                                    if cell.index == child.index + self.row_len:
                                        cell.focus = True

                            except IndexError:
                                pass

                        else:
                            child.focus = False
                            self.scroll.scroll_y = 1

                        break

        # Pressing Enter
        if keycode == 40 and (self.find_textinput.focused or self.find_textinput2.focused):
            if self.find_button.text == "Find/r" and self.find_textinput.focused and not self.find_button.disabled:
                self.found_item = 0
                self.find_order("")

            elif self.find_button.text == "f/Replace" and not self.find_button.disabled:
                text = f"You are about to replace every \"{self.find_textinput.text}\" in column \"{self.title_grid.children[(self.find_col * -1) - 1].text}\" with \"{self.find_textinput2.text}\", are you sure you want to continue?"
                self.warning(text, self.replace_word)

        #Press Up Key
        elif keycode == 82:

            try:
                Clock.schedule_once(partial(locate, "up"))

            except AttributeError:
                pass

        #Press Down Key
        elif keycode == 81:

            try:
                Clock.schedule_once(partial(locate, "down"))

            except AttributeError:
                pass

        #Left and Right Key
        elif keycode == 80 or keycode == 79:
            if not an_cell_on_focus:
                if keycode == 80:
                    self.scroll.scroll_x -= self.scroll.convert_distance_to_scroll(0, 2000)[1]

                    if self.scroll.scroll_x < 0:
                        self.scroll.scroll_x = 0
                else:
                    self.scroll.scroll_x += self.scroll.convert_distance_to_scroll(0, 2000)[1]

                    if self.scroll.scroll_x > 1:
                        self.scroll.scroll_x = 1
        #F11 and F12 Keys
        if keycode == 68 or keycode == 69:
            if not an_cell_on_focus:
                done = False

                row = self.rows_grid.children[:]
                row.sort(key=lambda a: int(a.text))

                if keycode == 68:
                    c2 = int(row[0].text)

                    for i in range(c2, int(self.row_num) - 1):

                        if self.scroll.data[(c2 * 2) + 1]['text'] == "":
                            self.calculate_location(int(self.scroll.data[(c2 * 2) + 1]['index'] / 2))
                            break

                        else:
                            for char in self.scroll.data[(c2 * 2) + 1]['text']:

                                if search(u'[\u3040-\u309F]+', char) or \
                                   search(u'[\u30A0-\u30FF]+', char) or \
                                   search(u'[\u4E00–\u9FBF]+', char) or \
                                   search(u'[\u3000–\u303F]+', char) or \
                                   search(u'[\uFF00–\uFFEF]+', char) or \
                                   search(u'[\u2E80-\u2FD5\u3190-\u319f\u3400-\u4DBF\u4E00-\u9FCC]+', char):

                                    self.calculate_location(int(self.scroll.data[(c2 * 2) + 1]['index'] / 2))
                                    done = True
                                    break

                            if done:
                                break
                        c2 += 1
                else:
                    c2 = int(row[0].text) - 2

                    for i in range(0, c2):

                        if self.scroll.data[(c2 * 2) + 1]['text'] == "":
                            self.calculate_location(int(self.scroll.data[(c2 * 2) + 1]['index'] / 2))
                            break

                        else:
                            for char in self.scroll.data[(c2 * 2) + 1]['text']:

                                if search(u'[\u3040-\u309F]+', char) or search(u'[\u30A0-\u30FF]+', char) or \
                                   search(u'[\u4E00–\u9FBF]+', char) or \
                                   search(u'[\u3000–\u303F]+', char) or \
                                   search(u'[\uFF00–\uFFEF]+', char) or \
                                   search(u'[\u2E80-\u2FD5\u3190-\u319f\u3400-\u4DBF\u4E00-\u9FCC]+', char):

                                    self.calculate_location(int(self.scroll.data[(c2 * 2) + 1]['index'] / 2))
                                    done = True
                                    break

                            if done:
                                break
                        c2 -= 1

        #Press PageUp Key Or PageDown Key
        elif keycode == 75 or keycode == 78:

            if len(self.marked_rows) != 0:

                if keycode == 75:
                    self.current_row -= 1

                else:
                    self.current_row += 1

                if self.current_row > len(self.marked_rows)-1:
                    self.current_row = 0

                elif self.current_row < -len(self.marked_rows):
                    self.current_row = -1

                self.calculate_location(int(self.marked_rows[self.current_row]))

    def menu_animation(self):

        Animation(height=42, t='out_bounce', duration=0.2).start(self.open)
        Animation(height=42, t='out_bounce', duration=0.4).start(self.save)
        Animation(height=42, t='out_bounce', duration=0.8).start(self.save_as)
        Animation(height=42, t='out_bounce', duration=1.2).start(self.find_button)

        a1 = Animation(height=30, t='in_out_expo', duration=0.9)
        a1 += Animation(width=50, t='out_expo', duration=0.5)
        a1.start(self.find_textinput)

        Animation(posy=0.12, t='out_expo').start(self.find_next)
        Animation(posx=1.79, t='out_bounce').start(self.find_prev)

    def replace_animation(self, reverse=False):

        def enable():
            self.find_button.disabled = False

        def replace_animation():
            textinput2_animation = Animation(posy=0.09, duration=0.2)
            textinput2_animation &= Animation(height=30, t='out_bounce', duration=0.6)
            textinput2_animation += Animation(width=260.8, t='out_expo')
            textinput2_animation.start(self.find_textinput2)

        if not reverse:

            findnext_animation = Animation(posy=1.46, t='out_expo', duration=0.5)
            findnext_animation += Animation(posx=5.01, t='out_expo')
            findnext_animation.start(self.find_next)

            Animation(posx=15.86, t='out_expo', duration=1).start(self.find_prev)
            Animation(width=260.8, t='out_expo').start(self.find_textinput)

            Clock.schedule_once(lambda dt: replace_animation(), 0.3)

            Animation(posx=6.27, t='out_expo').start(self.replace_all)
            Clock.schedule_once(lambda dt: enable(), 1.5)

        else:
            Animation(posx=15.86, t='out_expo').start(self.replace_all)

            textinput2_animation = Animation(height=1, t='out_expo', duration=0.6)
            textinput2_animation &= Animation(posy=-0.1)
            textinput2_animation += Animation(width=1, t='out_expo', duration=0.2)

            textinput2_animation.start(self.find_textinput2)

            Animation(width=400, t='in_out_expo').start(self.find_textinput)
            Animation(posy=0.12, t='out_expo', duration=0.7).start(self.find_next)
            Animation(posx=5.29, t='out_bounce', duration=1).start(self.find_prev)

            Clock.schedule_once(lambda dt: enable(), 1)

    @staticmethod
    def find_animation(widgets):


        textinput_animation = Animation(width=400, t='out_elastic')
        findnext_animation = Animation(posx=5, t='out_elastic')
        findprev_animation = Animation(posx=5.28, t='out_elastic')

        findnext_animation.start(widgets[1])
        findprev_animation.start(widgets[2])
        textinput_animation.start(widgets[0])


class PyCSV(App):

    def build(self):
        super().build()
        global editor
        global window_instance
        window_instance = self
        editor = CsvEditor()
        Window.bind(on_dropfile=editor.on_file_drop)
        Window.bind(on_key_down=editor.on_key_down)
        Window.bind(on_keyboard=editor.on_keyboard)
        Window.bind(on_motion=editor.on_motion)
        editor.menu_animation()
        self.title = 'PyCSV ' + ver
        return editor


if __name__ == '__main__':
    PyCSV().run()
