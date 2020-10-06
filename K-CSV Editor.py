import unicodecsv as csv
from datetime import datetime
from os.path import basename
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'resizable', 0)
from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from plyer import filechooser
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty, ListProperty

Window.size = (1000, 610)
word_theme = [[42 / 255, 87 / 255, 154 / 255, 1], [235 / 255, 245 / 255, 250 / 255, 1], [230 / 255, 230 / 255, 230 / 255, 1]]
excel_theme = [[33/255,  115/255,  70/255,  1], [235 / 255, 245 / 255, 250 / 255, 1], [230 / 255, 230 / 255, 230 / 255, 1]]
powerpoint_theme = [[183/255,  71/255,  42/255,  1], [235 / 255, 245 / 255, 250 / 255, 1], [230 / 255, 230 / 255, 230 / 255, 1]]
teams_theme = [[70/255,  71/255,  117/255,  1], [235 / 255, 245 / 255, 250 / 255, 1], [230 / 255, 230 / 255, 230 / 255, 1]]
Access_theme = [[164/255,  55/255,  58/255,  1], [235 / 255, 245 / 255, 250 / 255, 1], [230 / 255, 230 / 255, 230 / 255, 1]]
onedrive_theme = [[20/255,  144/255,  223/255,  1], [235 / 255, 245 / 255, 250 / 255, 1], [230 / 255, 230 / 255, 230 / 255, 1]]
current_theme = ListProperty([[42 / 255, 87 / 255, 154 / 255, 1], [235 / 255, 245 / 255, 250 / 255, 1], [230 / 255, 230 / 255, 230 / 255, 1]])


class FindTextInput(TextInput):
    pass


class JoButton(Button):
    global current_theme
    theme = current_theme
    pass


class ReplaceButton(Button):
    global current_theme
    theme = current_theme
    pass


class JoButtonLabel(Button):
    global current_theme
    theme = current_theme
    pass


class JoTextInput(TextInput):
    global current_theme
    theme = current_theme
    pass


def label_highlight(widget):
    global current_theme
    current_label = widget
    if current_label.background_color != [0, 0, 0, 1]:
        current_label.background_color = [0, 0, 0, 1]

    else:
        current_label.background_color = current_theme[0]


class CsvEditor(Widget):
    global current_theme
    theme = current_theme
    cells_grid = ObjectProperty(None)
    title_grid = ObjectProperty(None)
    scroll = ObjectProperty(None)
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
    row_len = 0
    row_num = 0
    file_path = ""
    focused_cell = 0
    found_list = []
    current_find = ""
    found_item = 0
    current_row = 0
    current_mins = 0
    current_secs = 0
    # def __init__(self, **kwargs):
    #     super(CsvEditor, self).__init__(**kwargs)

    def change_theme(self, theme):
        self.theme = theme
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

        for child in self.cells_grid.children:
            if "JoButtonLabel" in str(child):
                child.background_color = theme[0]

        for child in self.title_grid.children:
            child.background_color = theme[0]

    def on_file_drop(self, window, drag_file_path):
        self.load(drag=drag_file_path.decode('utf-8'))

    def load(self, drag=""):

        now = datetime.now()
        self.current_mins = int(now.strftime("%M"))
        self.current_secs = int(now.strftime("%S"))

        if drag == "":

            try:
                self.file_path = filechooser.open_file(title="Pick a CSV file..", filters=[("Comma-separated Values", "*.csv")])[0]

            except IndexError:
                pass

        else:
            self.file_path = drag

        if self.file_path != '':
            with open(self.file_path, 'rb') as f:

                while len(self.cells_grid.children) != 0:
                    self.cells_grid.remove_widget(self.cells_grid.children[0])

                while len(self.title_grid.children) != 0:
                    self.title_grid.remove_widget(self.title_grid.children[0])

                self.row_num = 0

                for row in csv.reader(f, encoding='utf-8'):

                    self.row_len = len(row) + 1
                    self.title_grid.cols = self.row_len
                    self.cells_grid.cols = self.row_len

                    if self.row_num == 0:
                        self.title_grid.add_widget(JoButtonLabel(text="No.", width=50, height=30,
                                                                 size_hint=[None, None]))
                        self.row_num += 1

                    else:
                        self.cells_grid.add_widget(JoButtonLabel(text=str(self.row_num), width=50, height=30,
                                                                 font_name='MEIRYO.TTC',
                                                                 font_size='15sp',
                                                                 size_hint=[None, None],
                                                                 on_press=label_highlight))
                        self.row_num += 1

                    for i in row:

                        if self.row_num == 1:
                            self.title_grid.add_widget(JoButtonLabel(text=i, height=30,
                                                                     font_name='MEIRYO.TTC',
                                                                     font_size='15sp',
                                                                     size_hint=[1, None]))
                        else:
                            self.cells_grid.add_widget(JoTextInput(multiline=False, write_tab=False,
                                                                   text=i, height=30,
                                                                   font_name='MEIRYO.TTC',
                                                                   font_size='14sp',
                                                                   size_hint=[1, None]))
        Clock.schedule_interval(lambda dt: self.auto_save(), 1)

    def save_file(self, save_as=False):

        if save_as:
            new_path = filechooser.save_file(title="Save As..", filters=[("Comma-separated Values", "*.csv")])

            if len(new_path) != 0:
                self.file_path = new_path[0]

        if self.file_path != "":
            with open(self.file_path, 'wb') as f:
                data = self.child_indexing(textinput_only=False)

                for i in data:
                    for child in i:
                        data[data.index(i)][i.index(child)] = child.text

                csv_writer = csv.writer(f, encoding='utf-8')

                title = []
                for i in self.title_grid.children[0:-1]:
                    title.append(i.text)

                title.reverse()
                csv_writer.writerow(title)

                for i in range(0, len(data)):
                    csv_writer.writerow(data[i][1:])

    def child_indexing(self, textinput_only=True):

        data = []

        if len(self.cells_grid.children) !=0:

            if textinput_only:
                row_len = self.row_len-1

            else:
                row_len = self.row_len

            for child in self.cells_grid.children:

                if textinput_only:
                    if "JoTextInput" in str(child):
                        data.append(child)
                else:
                    data.append(child)

            data.reverse()
            for i in range(0, int(len(data) / row_len)):
                temp = data[0:row_len]
                del data[0:row_len]
                data.append(temp)

        return data

    def calculate_location(self, row):

        # Scroll Needed Per Row
        spr = 1 / self.row_num

        # Error reduction
        er = float((row / 10) * 0.000329)

        self.scroll.scroll_y = float(1 - (row * spr) - er)

    def replace_word(self):
        self.current_find = self.find_textinput.text

        data = self.child_indexing()

        for i in data:
            for child in i:
                if self.find_textinput.text in child.text:
                    child.text = child.text.replace(self.find_textinput.text, self.find_textinput2.text)

    def find_word(self):

        if self.find_textinput.text != "":

            self.found_list = []
            self.current_find = self.find_textinput.text

            data = self.child_indexing()

            for i in data:
                for child in i:
                    if self.find_textinput.text in child.text:
                        temp = child.text
                        s = temp.index(self.current_find)
                        e = s + len(self.current_find)

                        if s == e:
                            e += 1

                        self.found_list.append([data.index(i), child, s, e])

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
            print(self.found_item)
            if self.found_item > len(self.found_list) - 1:
                self.found_item = 0

            elif self.found_item < -len(self.found_list):
                self.found_item = -1

            self.found_list[self.found_item][1].focus = True
            start = self.found_list[self.found_item][2]
            end = self.found_list[self.found_item][3]
            self.found_list[self.found_item][1].select_text(start, end)

            self.calculate_location(self.found_list[self.found_item][0])

    def auto_save(self):

        now = datetime.now()
        mins = int(now.strftime("%M"))
        secs = int(now.strftime("%S"))
        passed_mins = int(mins - self.current_mins)
        print(secs)
        if secs == 10:
            name = basename(self.file_path)
            self.file_path = self.file_path.replace(name, name.replace(".csv", ".csv.backup"))
            self.save_file(save_as=False)
            self.file_path = self.file_path.replace(name.replace(".csv", ".csv.backup"), name)

    def on_key_up(self, scancode, keycode, modifier):

        def locate_next():
            row = 0
            child_loc = 0
            data = self.child_indexing()
            for i in data:
                for child in i:
                    if child.focused:
                        row = data.index(i)
                        child_loc = i.index(child)
                        break
            return data, row, child_loc

        #Pressing Enter
        if keycode == 13:
            if self.find_button.text == "F/r":
                self.find_order("")

            else:
                self.replace_word()



        #Press CTRL Key Or SHIFT
        elif keycode == 305 or keycode == 304:
            widgets = self.child_indexing(textinput_only=False)
            row_nums = []

            for i in widgets:
                if i[0].background_color == [0, 0, 0, 1]:
                    row_nums.append(i)

            if len(row_nums) != 0:

                if keycode == 304:
                    self.current_row -= 1
                else:
                    self.current_row += 1

                if self.current_row > len(row_nums)-1:
                    self.current_row = 0

                elif self.current_row < -len(row_nums):
                    self.current_row = -1

                #Somehow calling calculate_location function from here makes it give the location of the NEXT location by mistake god knows why, although it has been given the row number correctly, so i added -1 for it.
                self.calculate_location(int(row_nums[self.current_row][0].text)-1)
                row_nums[self.current_row][-1].focus = True

    def on_key_down(self, key, scancode, keycode, modifier, numlock):

        def locate_next():
            row = 0
            child_loc = 0
            data = self.child_indexing()
            for i in data:
                for child in i:
                    if child.focused:
                        row = data.index(i)
                        child_loc = i.index(child)
                        break
            return data, row, child_loc

        #Press Up Key
        if keycode == 82:

            data, row, child_loc = locate_next()

            if row != 0:
                data[row-1][child_loc].focus = True

            # Scroll Needed Per Row
            spr = 1 / self.row_num

            # Error reduction
            er = float((1 / 10) * 0.000329)

            self.scroll.scroll_y += float(spr)+er

        #Press Down Key
        elif keycode == 81:
            data, row, child_loc = locate_next()

            if row != -1:
                data[row+1][child_loc].focus = True

            # Scroll Needed Per Row
            spr = 1 / self.row_num

            # Error reduction
            er = float((1 / 10) * 0.000329)

            self.scroll.scroll_y -= float(spr)+er

    def menu_animation(self):

        Animation(height=42, t='out_bounce', duration=0.2).start(self.open)
        Animation(height=42, t='out_bounce', duration=0.4).start(self.save)
        Animation(height=42, t='out_bounce', duration=0.8).start(self.save_as)
        Animation(height=42, t='out_bounce', duration=1.2).start(self.find_button)

        a1 = Animation(height=30, t='in_out_expo', duration=0.9)
        a1 += Animation(width=50, t='out_expo', duration=0.5)
        a1.start(self.find_textinput)

        Animation(y=556, t='out_expo').start(self.find_next)
        Animation(x=520, t='out_bounce').start(self.find_prev)


    def replace_animation(self, reverse=False):
        def enable():
            self.find_button.disabled = False

        if not reverse:

            findnext_animation = Animation(y=615, t='out_expo', duration=0.5)
            findnext_animation += Animation(x=841, t='out_expo')
            findnext_animation.start(self.find_next)

            Animation(x=1002, t='out_expo', duration=1).start(self.find_prev)
            Animation(width=260.8, t='out_expo').start(self.find_textinput)

            textinput2_animation = Animation(height=30, t='out_expo', duration=0.6)
            textinput2_animation &= Animation(y=555, duration=0.5)
            textinput2_animation += Animation(width=260.8, t='out_expo')
            textinput2_animation.start(self.find_textinput2)

            Animation(x=968, t='out_expo').start(self.replace_all)
            Clock.schedule_once(lambda dt: enable(), 1.5)

        else:
            Animation(x=1007, duration=0.1).start(self.replace_all)

            textinput2_animation = Animation(height=0, duration=0.2)
            textinput2_animation += Animation(width=1, t='out_expo', duration=0.2)
            textinput2_animation &= Animation(y=530)
            textinput2_animation.start(self.find_textinput2)

            Animation(width=400, t='in_out_expo').start(self.find_textinput)
            Animation(y=556, t='out_expo', duration=0.5).start(self.find_next)
            Animation(x=869, t='out_bounce').start(self.find_prev)

            Clock.schedule_once(lambda dt: enable(), 1)


    def find_animation(self, widgets):


        textinput_animation = Animation(width=400, t='out_elastic')
        findnext_animation = Animation(x=841, t='out_elastic')
        findprev_animation = Animation(x=869, t='out_elastic')

        findnext_animation.start(widgets[1])
        findprev_animation.start(widgets[2])
        textinput_animation.start(widgets[0])


class KCsvEditor(App):

    def build(self):
        editor = CsvEditor()
        Window.bind(on_dropfile=editor.on_file_drop)
        Window.bind(on_key_up=editor.on_key_up)
        Window.bind(on_key_down=editor.on_key_down)
        editor.menu_animation()
        self.title = 'Jo\'s K-CSV Editor v0.9'
        return editor


if __name__ == '__main__':
    KCsvEditor().run()
