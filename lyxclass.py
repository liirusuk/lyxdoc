from typing import List
import re
from six import string_types
import numpy as np

class LyxObject:
    """
    Represents a basic LyX object with a tag and an optional attribute.
    """
    tag: str
    attribute: str

    def __init__(self, tag, attribute=None):
        """
        Initializes a LyxObject.

        :param tag: The tag for the LyX object.
        :param attribute: The optional attribute for the LyX object.
        """
        self.tag = tag
        self.attribute = attribute

    def tostring(self):
        """
        Converts the LyX object to a string representation.

        :return: The string representation of the LyX object.
        """
        _string = '\\\\' + self.tag
        if self.attribute is not None:
            _string += ' ' + self.attribute
        return _string

    def __str__(self):
        """
        Converts the LyX object to a string.

        :return: The string representation of the LyX object.
        """
        return self.tostring()

    def __repr__(self):
        """
        Provides a detailed string representation of the LyX object.

        :return: The detailed string representation of the LyX object.
        """
        return str(self.__class__.__name__) + ' ' + self.tag + (
            ' ' + self.attribute if self.attribute is not None else ''
        )

class LyxContainer:
    """
    Represents a container for multiple LyX objects.
    """
    tag: str
    attribute: str
    content: List

    def __init__(self, tag, attribute=None, content=None):
        """
        Initializes a LyxContainer.

        :param tag: The tag for the LyX container.
        :param attribute: The optional attribute for the LyX container.
        :param content: The optional content for the LyX container.
        """
        self.tag = tag
        self.attribute = attribute
        if content is None:
            self.content = []
        else:
            self.content = content

    def tostring(self):
        """
        Converts the LyX container and its content to a string representation.

        :return: The string representation of the LyX container and its content.
        """
        _string = '\n'.join(['\\\\begin_' + self.tag + (' ' + self.attribute if self.attribute is not None else ''),
                             *[str(x) for x in self.content],
                             '\\\\end_' + self.tag])
        return _string

    def append(self, item):
        """
        Appends an item to the content of the LyX container.

        :param item: The item to be appended.
        """
        self.content.append(item)

    def text(self, sep: str = ' '):
        """
        Joins the text content of the LyX container.

        :param sep: The separator to use between text content.
        :return: The joined text content.
        """
        text_content = []
        for obj in self.content:
            if isinstance(obj, str):
                text_content.append(obj)
            else:
                text_content.append(str(obj))
        return sep.join(text_content)

    def __repr__(self):
        """
        Provides a detailed string representation of the LyX container.

        :return: The detailed string representation of the LyX container.
        """
        return str(self.__class__.__name__) + ' ' + self.tag + (
            ' ' + self.attribute if self.attribute is not None else ''
        )

    def __str__(self):
        """
        Converts the LyX container to a string.

        :return: The string representation of the LyX container.
        """
        return self.tostring()

    def __getitem__(self, key):
        """
        Gets an item from the content by index.

        :param key: The index of the item.
        :return: The item at the specified index.
        """
        return self.content[key]

class CloseTag:
    """
    Represents a closing tag for a LyX object.
    """
    tag: str

    def __init__(self, tag):
        """
        Initializes a CloseTag.

        :param tag: The tag to close.
        """
        self.tag = tag

    def tostring(self):
        """
        Converts the closing tag to a string representation.

        :return: The string representation of the closing tag.
        """
        return '\\\\end_' + self.tag

    def __str__(self):
        """
        Converts the closing tag to a string.

        :return: The string representation of the closing tag.
        """
        return self.tostring()

class LyxLabel(LyxContainer):
    """
    Represents a LyX label inset.
    """
    def __init__(self, input_label):
        """
        Initializes a LyxLabel.

        :param input_label: The input label to be modified and used.
        """
        input_label = self.label_modifier(input_label)
        tag = 'inset'
        attribute = 'CommandInset Label'
        content = ['LatexCommand Label', 'name "' + input_label + '"']
        super().__init__(tag=tag, attribute=attribute, content=content)

    @staticmethod
    def label_modifier(input_label):
        """
        Modifies the input label by replacing special characters.

        :param input_label: The input label to be modified.
        :return: The modified input label.
        """
        my_labels = {"%": "percent", "_": "underline", "^": "slide", "#": "pound",
                     "{": "bracketStart", "}": "bracketEnd", "\\": "backwardSlash",
                     "=": "equal"}
        regex = re.compile('|'.join(map(re.escape, my_labels.keys())))
        output_str = regex.sub(lambda mo: my_labels.get(mo.string[mo.start():mo.end()]), input_label)
        return output_str

class LyxReference(LyxContainer):
    """
    Represents a LyX reference inset.
    """
    def __init__(self, crossref):
        """
        Initializes a LyxReference.

        :param crossref: The cross-reference to be used.
        """
        tag = 'inset'
        attribute = 'CommandInset ref'
        content = ['reference \"' + crossref + '\"']
        super().__init__(tag=tag, attribute=attribute, content=content)

class LyxLayout(LyxContainer):
    """
    Represents a LyX layout container.
    """
    def __init__(self, layout_type, layout_text, layout_label=""):
        """
        Initializes a LyxLayout.

        :param layout_type: The type of the layout.
        :param layout_text: The text of the layout.
        :param layout_label: The optional label for the layout.
        """
        tag = 'layout'
        attribute = layout_type
        if len(layout_label) > 0:
            content = [LyxLabel(layout_label)]
        else:
            content = []
        content.append(layout_text)
        super().__init__(tag=tag, attribute=attribute, content=content)

class LyxTabular(LyxContainer):
    """
    Represents a LyX tabular container.
    """
    def __init__(self, array, colWidth: List[int] = None, number_format='{:.0f}'):
        """
        Initializes a LyxTabular.

        :param array: The array of data to be included in the tabular.
        :param colWidth: The optional column widths.
        :param number_format: The format for the numbers in the tabular.
        """
        MAXITEM = 180
        tag = 'inset'
        attribute = 'Tabular'
        super().__init__(tag=tag, attribute=attribute)

        num_lines = len(array)
        if num_lines == 0:
            return
        col = 1
        for line in array:
            if isinstance(line, list):
                col = max(col, len(line))
        if colWidth is None:
            colWidth = [round(100.0 * 0.95 / float(col), 0) for _ in range(col)]

        content = []

        # if some content is too big, the data will be split
        for i, line in enumerate(array): # count the num of lines
            if isinstance(line, list):
                col_num = len(line)
                for j in range(col_num):
                    if (isinstance(line[j], string_types) and line[j].count(";") > 0) \
                            and (len(line[j].split(";")) > MAXITEM):
                        num_lines = num_lines + int((len(line[j].split(";")) - 1) / MAXITEM)

        content.append('<lyxtabular version=' + str(3) + ' rows=' + str(num_lines) + ' columns=' + str(int(col)) + '>')
        content.append('<features islongtable="true" longtabularalignment="center">')

        for icol in range(col):
            content.append('<colum alignment="center" valignement="top" width="' + str(colWidth[icol]) + '" text="%s">')

        for iline, line in enumerate(array):
            content.append('<row>')
            local_line = []
            lcol = 1
            if isinstance(line, list):
                lcol = len(line)
                local_line = line
            else:
                local_line.append(line)
            if col > lcol:
                local_line.append(line)
            for j in range(col - lcol):
                local_line.append("")
            topline = "true"
            bottomLine = "false"
            if iline == int(len(array)) - 1:
                bottomline = "true"

            for icol in range(col):
                lefline = "false"
                if icol == int(0):
                    leftline = "true"
                if isinstance(local_line[icol], string_types):
                    local_line[icol] = local_line[icol].replace('_', ' ')
                    local_line[icol] = re.sub(r'([a-z](?=[A-Z])|[A-Z](?=[A-Z][a-z]))', r'\1 ', local_line[icol])

                    # if too long, breaking into different lines
                    if (local_line[icol].count(';') > 0) and (len(local_line[icol].split(';')) > MAXITEM):
                        new_line = local_line[icol].split(';')
                        content.extend(self._cell_content(';'.join(new_line[:MAXITEM]) + ';', topline, bottomline, leftline))
                        for k in range(int((len(new_line) - 1) / MAXITEM)):
                            content.append('</row>')
                            content.append('<row>')
                            content.append('<cell><text>%s</text></cell>')
                            content.append('</row>')
                            text_content = ":".join(new_line[MAXITEM * (k + 1): min(MAXITEM * (k + 2), len(new_line))])
                            if k < int((len(new_line) - 1) / MAXITEM) - 1:
                                text_content += ";"
                            content.extend(self._cell_content(text_content, topline, bottomLine, leftline))
                    else:
                        content.append(str(local_line[icol]))
                elif isinstance(local_line[icol], float):

                    if np.isnan(local_line[icol]):
                        out = 'N/A'
                    else:
                        out = number_format.format(local_line[icol])
                    content.ecxtend(self._cell_content(out, topline, bottomLine, leftline))
                else:
                    content.append(str(local_line[icol]))
            content.append('</row>')
        self.content=content

class LyxGraphics(LyxContainer):
    """
    Represents a LyX graphics container.
    """
    def __init__(self, fig_name, caption_text, width=0, sub_fig=True):
        """
        Initializes a LyxGraphics.

        :param fig_name: The name of the figure.
        :param caption_text: The caption text for the figure.
        :param width: The width of the figure.
        :param sub_fig: Whether the figure is a sub-figure.
        """
        content = [LyxObject('noindent'), LyxObject('align', 'center')]
        if width == 0:
            width_str = " width 45text%"
        else:
            width_str = " width 70text%"
        graphics_content = LyxContainer('inset', 'Graphics', content=[
            '_filename "' + fig_name,
            width_str
        ])
        caption_content = LyxContainer('layout', 'Plain Layout', content=[
            LyxContainer('inset', 'Caption', content=[
                LyxContainer('layout', 'Plain Layout', content=[
                    LyxContainer('inset', 'CommandInset label', content=[
                        'LatexCommand label',
                        'name "' + fig_name + '"'
                    ])
                ])
            ])
        ])
        if not sub_fig:
            content.append(LyxContainer('inset', 'Float figure', content=[
                "wide false",
                "sideways false",
                "status open",
                LyxContainer('layout', 'Plain Layout', content=[
                    LyxObject('noindent'), LyxObject('align', 'center'),
                    graphics_content
                ]),
                caption_content
            ]))
        else:
            content.append(graphics_content)
            content.append(caption_content)
        super().__init__('layout', 'Standard', content)