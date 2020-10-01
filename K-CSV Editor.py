import unicodecsv as csv
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from plyer import filechooser
from kivy.core.window import Window

Window.size = (1000, 590)


class CsvEditor(Widget):

    grid = ObjectProperty(None)
    records = []
    row_len = 0
    file_path = ""

    # def __init__(self, **kwargs):
    #     super(CsvEditor, self).__init__(**kwargs)

    def load(self, drag=""):
        global row_len

        if drag == "":
            self.file_path = filechooser.open_file(title="Pick a CSV file..",
                                                   filters=[("Comma-separated Values", "*.csv")])[0]
        else:
            self.file_path = drag

        cell_num = 0
        with open(self.file_path, 'rb') as f:

            self.grid.children = []
            row_num = 0
            for row in csv.reader(f, encoding='utf-8'):
                row_len = len(row) + 1
                self.grid.cols = row_len
                self.grid.add_widget(Label(text=str(row_num), width=50, height=40,
                                           font_name='C:\\Users\\PC\\AppData\\Local\\Microsoft\\Windows\\Fonts\\MEIRYO.TTC',
                                           size_hint=[None, None],
                                           color=[29/255, 111/255, 66/255, 1]))
                row_num += 1
                for i in row:
                    self.grid.add_widget(TextInput(multiline=False, text=i, height=40,
                                                   font_name='C:\\Users\\PC\\AppData\\Local\\Microsoft\\Windows\\Fonts\\MEIRYO.TTC',
                                                   size_hint=[1, None],
                                                   background_normal='',
                                                   background_color=[235/255, 242/255, 250/255, 1]))
                    cell_num += 1

    def save_as(self):
        self.save_file(as_new=True)

    def save_file(self, as_new=False):
        global row_len

        if as_new:
            new_path = filechooser.save_file(title="Save As..",
                                             filters=[("Comma-separated Values", "*.csv")])[0]

            if new_path:
                self.file_path = new_path

        with open(self.file_path, 'wb') as f:
            data = []

            for child in self.grid.children:

                try:
                    #Checking if the child is an TextInput
                    child.background_normal
                    data.append(child.text)

                except AttributeError:
                    pass

            data.reverse()
            row_len -= 1
            for i in range(0, int(len(data)/row_len)):
                temp = data[0:row_len]
                del data[0:row_len]
                data.append(temp)

            csv_writer = csv.writer(f, encoding='utf-8')

            for i in range(0, len(data)):
                csv_writer.writerow(data[i])

    def on_file_drop(self, window, drag_file_path):
        self.load(drag=drag_file_path.decode('utf-8'))

    # def on_keyboard(self, window, key, scancode, codepoint, modifier):
    #     if modifier == ['ctrl'] and codepoint == '+':



class KCsvEditor(App):

    def build(self):
        editor = CsvEditor()
        Window.bind(on_dropfile=editor.on_file_drop)
        # Window.bind(on_keyboard=editor.on_keyboard)
        self.title = 'Jo\'s K-CSV Editor'
        return editor




if __name__ == '__main__':
    KCsvEditor().run()
