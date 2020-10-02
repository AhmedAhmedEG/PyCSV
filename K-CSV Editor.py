import unicodecsv as csv
from kivy.app import App
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from plyer import filechooser
from kivy.properties import ObjectProperty

from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Canvas
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout

Window.size = (1000, 610)


class Label2(Label):
    pass


class TextInput2(TextInput):
    pass


class CsvEditor(Widget):

    grid = ObjectProperty(None)
    scroll = ObjectProperty(None)
    find = ObjectProperty(None)
    row_len = 0
    row_num = 0
    file_path = ""
    focused_cell = 0

    # def __init__(self, **kwargs):
    #     super(CsvEditor, self).__init__(**kwargs)

    def child_indexing(self, row_len, textinput_only=True):

        data = []

        for child in self.grid.children:

            if textinput_only:
                try:
                    # Checking if the child is an TextInput
                    child.background_normal
                    data.append(child)

                except AttributeError:
                    pass

            else:
                data.append(child)

        data.reverse()
        for i in range(0, int(len(data) / row_len)):
            temp = data[0:row_len]
            del data[0:row_len]
            data.append(temp)

        return data

    def load(self, drag=""):

        if drag == "":

            try:
                self.file_path = filechooser.open_file(title="Pick a CSV file..",filters=[("Comma-separated Values", "*.csv")])[0]

            except IndexError:
                pass

        else:
            self.file_path = drag

        if self.file_path != '':
            with open(self.file_path, 'rb') as f:

                while len(self.grid.children) != 0:
                    self.grid.remove_widget(self.grid.children[0])

                self.row_num = 0

                for row in csv.reader(f, encoding='utf-8'):

                    self.row_len = len(row) + 1
                    self.grid.cols = self.row_len

                    if self.row_num == 0:
                        self.grid.add_widget(Label(width=50, height=30,
                                                   size_hint=[None, None]))
                        self.row_num += 1

                    else:
                        self.grid.add_widget(Label2(text=str(self.row_num), width=50, height=30,
                                                    font_name='MEIRYO.TTC',
                                                    font_size='15sp',
                                                    size_hint=[None, None],
                                                    color=[0, 0, 0, 1]))
                        self.row_num += 1

                    for i in row:

                        if self.row_num == 1:
                            self.grid.add_widget(Label2(text=i, height=30,
                                                        font_name='MEIRYO.TTC',
                                                        font_size='15sp',
                                                        size_hint=[1, None],
                                                        color=[0, 0, 0, 1]))
                        else:
                            self.grid.add_widget(TextInput2(multiline=False, text=i, height=30,
                                                            font_name='MEIRYO.TTC',
                                                            font_size='14sp',
                                                            size_hint=[1, None],
                                                            background_normal='',
                                                            background_color=[235/255, 242/255, 250/255, 1]))

    def save_as(self):
        self.save_file(as_new=True)

    def save_file(self, as_new=False):

        if as_new:
            new_path = filechooser.save_file(title="Save As..", filters=[("Comma-separated Values", "*.csv")])[0]

            if new_path:
                self.file_path = new_path

        with open(self.file_path, 'wb') as f:
            data = self.child_indexing(self.row_len, textinput_only=False)

            for i in data:
                for child in i:
                    data[data.index(i)][i.index(child)] = child.text

            csv_writer = csv.writer(f, encoding='utf-8')

            for i in range(0, len(data)):
                csv_writer.writerow(data[i][1:])

    def on_file_drop(self, window, drag_file_path):
        self.load(drag=drag_file_path.decode('utf-8'))

    def find_ind(self):

        if self.find.text != "":

            ind = 0

            data = self.child_indexing(self.row_len-1)

            for i in data:
                for child in i:
                    if child.text == self.find.text:
                        child.focus = True
                        child.select_all()
                        ind = data.index(i)
                        break


            #Scroll Per Row
            spr = 1/self.row_num

            self.scroll.scroll_y = 1-(ind*spr)
            self.find.text = ""

        else:
            pass

    def on_keyboard(self, keyboard, keycode, text, modifiers, numlock):

        def locate():
            row_ind = 0
            child_ind = 0
            data = self.child_indexing(self.row_len-1)

            for i in data:
                for child in i:
                    if child.focused:
                        row_ind = data.index(i)
                        child_ind = i.index(child)
                        break
            return data, row_ind, child_ind

        if keycode == 13:
            self.find_ind()

        elif keycode == 274:
            data, row_ind, child_ind = locate()

            try:
                data[row_ind+1][child_ind].focus = True

            except IndexError:
                pass

        elif keycode == 273:

            try:
                data, row_ind, child_ind = locate()
                data[row_ind-1][child_ind].focus = True

            except IndexError:
                pass

        # elif keycode == 276:
        #
        #     try:
        #         data, row_ind, child_ind = locate()
        #         data[row_ind][child_ind-1].focus = True
        #
        #     except IndexError:
        #         pass
        #
        # elif keycode == 275:
        #
        #     try:
        #         data, row_ind, child_ind = locate()
        #         data[row_ind][child_ind-1].focus = True
        #
        #     except IndexError:
        #         pass


class KCsvEditor(App):

    def build(self):
        editor = CsvEditor()
        Window.bind(on_dropfile=editor.on_file_drop)
        Window.bind(on_keyboard=editor.on_keyboard)
        self.title = 'Jo\'s K-CSV Editor'
        return editor


if __name__ == '__main__':
    KCsvEditor().run()
