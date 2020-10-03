import unicodecsv as csv
from kivy.config import Config
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.graphics import Color
from kivy.graphics import Rectangle
from kivy.animation import Animation
from plyer import filechooser
from kivy.properties import ObjectProperty

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Window.size = (1000, 610)


class FindTextInput(TextInput):
    pass


class Label2(Label):
    pass


class TextInput2(TextInput):
    pass


class CsvEditor(Widget):

    grid = ObjectProperty(None)
    scroll = ObjectProperty(None)
    find = ObjectProperty(None)
    grid1 = ObjectProperty(None)
    row_len = 0
    row_num = 0
    file_path = ""
    focused_cell = 0

    # def __init__(self, **kwargs):
    #     super(CsvEditor, self).__init__(**kwargs)



    def find_anim(self, instance, fo=True):

        if fo:
            anim = Animation(size=(350, 30), t='out_bounce')
        else:
            anim = Animation(size=(20, 30), t='out_bounce')

        anim.start(instance)

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
                self.file_path = filechooser.open_file(title="Pick a CSV file..", filters=[("Comma-separated Values", "*.csv")])[0]

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
                        self.grid.add_widget(Label2(width=50, height=30,
                                                    size_hint=[None, None]))
                        self.row_num += 1

                    else:
                        self.grid.add_widget(Label2(text=f'[ref={str(self.row_num)}]{str(self.row_num)}[/ref]', markup=True, width=50, height=30,
                                                    font_name='MEIRYO.TTC',
                                                    font_size='15sp',
                                                    size_hint=[None, None],
                                                    on_ref_press=self.label_highlight))
                        self.row_num += 1

                    for i in row:

                        if self.row_num == 1:
                            self.grid.add_widget(Label2(text=i, height=30,
                                                        font_name='MEIRYO.TTC',
                                                        font_size='15sp',
                                                        size_hint=[1, None]))
                        else:
                            self.grid.add_widget(TextInput2(multiline=False, text=i, height=30,
                                                            font_name='MEIRYO.TTC',
                                                            font_size='14sp',
                                                            size_hint=[1, None]))

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
                    if self.find.text in child.text:
                        child.focus = True
                        child.select_all()
                        ind = data.index(i)
                        break


            #Scroll Per Row
            spr = 1/self.row_num

            self.scroll.scroll_y = 1-(ind*spr)

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

    def label_highlight(self, instance, text):

        current_label = self.grid.children[self.grid.children.index(instance)]
        if current_label.color != [31/255, 58/255, 147/255, 1]:
            current_label.color = [31/255, 58/255, 147/255, 1]
            with current_label.canvas.before:
                Color(rgba=[52/255, 152/255, 219/255, 1])
                Rectangle(size=current_label.size, pos=current_label.pos)

        else:
            current_label.color = [0, 0, 0, 1]
            with current_label.canvas.before:
                Color(rgba=[230/255, 230/255, 230/255, 1])
                Rectangle(size=current_label.size, pos=current_label.pos)



class KCsvEditor(App):

    def build(self):
        editor = CsvEditor()
        Window.bind(on_dropfile=editor.on_file_drop)
        Window.bind(on_keyboard=editor.on_keyboard)
        self.title = 'Jo\'s K-CSV Editor v0.3'
        return editor


if __name__ == '__main__':
    KCsvEditor().run()
