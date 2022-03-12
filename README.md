# PyCSV Editor

Very Rich GUI based python CSV editor, made with kivy python library, there was not a decent CSV editor made with python on github, so I started making one myself, and then it have grown to a big project.

![Screenshot_9](https://user-images.githubusercontent.com/16827679/158036991-8efbebbd-4131-41d5-9888-fb3dfd62585f.png)


# How To Use

[PyCSV Doc.docx](https://github.com/AhmedAhmedEG/PyCSV/files/8238569/PyCSV.Doc.docx)


# Features

Modern and animated design.

Open, save, save as functions.

Find next/previos and Replace functions (supports partial searching/replacing).

Duplicated rows marking.

bulk application of duplicates edits, (edits made to an original row can be applied to all of it's duplicates)

Columns filtering, display spacific columns and hide the others, you still can view and edit the others from the details menu by right clicking an row number.

AI based spell checking with custom models.

Dragn n drop support.

Auto backup with custom interval with rolling scheme.

Navigation throug cells and columns eaisly with arrow keys.

Resizable columns with mouse draging.

Row hightlighting.

Theme changer.

And many more in the documentation...

# Spell Check

A standared small model is included.
You can download large full english models from here: https://github.com/hellohaptik/spello#get-started-with-pre-trained-models

# Requirments

python -m pip install kivy[full] kivy_examples

pip install unicodecsv

pip install plyer

pip install spello

Python v2.9+

PyCSV.py and PyCSV.kv and MEIRYI.TTC must be in the same directory.
