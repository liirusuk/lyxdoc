import os
from typing import List
from collections.abc import Iterable
import logging
import lyxclass

def read_project_file(file_ref):
    """
    Reads the content of a project file.

    :param file_ref: The reference to the file to be read.
    :return: The content of the file as a string.
    """
    module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
    filepath = os.path.abspath(os.path.join(module_path, file_ref))
    with open(filepath, "r") as f:
        input_str = f.read()
    return input_str


class LyxPart:
    """
    Represents a part of a LyX document.
    """
    header: lyxclass.LyxContainer
    content: List

    def __init__(self, header: lyxclass.LyxContainer, content=None):
        """
        Initializes a LyxPart.

        :param header: The header for the LyX part.
        :param content: The content for the LyX part.
        """
        self.header = header
        if content is None:
            self.content = []
        else:
            self.content = content

    @property
    def tag(self):
        """
        Gets the tag of the header.

        :return: The tag of the header.
        """
        return self.header.tag

    @property
    def attribute(self):
        """
        Gets the attribute of the header.

        :return: The attribute of the header.
        """
        return self.header.attribute

    @property
    def name(self):
        """
        Gets the text of the header.

        :return: The text of the header.
        """
        return self.header.text().strip()

    def tostring(self):
        """
        Converts the LyX part to a string representation.

        :return: The string representation of the LyX part.
        """
        string_content = [str(self.header)]
        for item in self.content:
            string_content.append(str(item))
        return '\n'.join(string_content)

    def append(self, item):
        """
        Appends an item to the content of the LyX part.

        :param item: The item to be appended.
        """
        self.content.append(item)

    def __str__(self):
        """
        Converts the LyX part to a string.

        :return: The string representation of the LyX part.
        """
        return self.tostring()

    def __repr__(self):
        """
        Provides a detailed string representation of the LyX part.

        :return: The detailed string representation of the LyX part.
        """
        return str(self.__class__.__name__) + ' (' + self.header.attribute + \
               ')' if self.header.attribute is not None else '' + ' ' + self.name

    def __getitem__(self, key):
        """
        Gets an item from the content by index.

        :param key: The index of the item.
        :return: The item at the specified index.
        """
        return self.content[key]

class LyxDocument:
    """
    Represents a LyX document.
    """
    content: List

    def __init__(self, input_string: str):
        """
        Initializes a LyxDocument.

        :param input_string: The input string representing the document content.
        """
        lines = input_string.split('\n')
        lyx_content = []
        parents_ref = [[lyx_content]]
        for i, line in enumerate(lines):
            parsed_line = self._parse_line(line)
            if isinstance(parsed_line, lyxclass.CloseTag):
                if len(parents_ref[-1]) == 1:
                    logging.warning('found the closing tag without the opening ' + str(i) + ': ' +
                                    parents_ref[-1][-1].tag + ': ' + parsed_line.tag)
                parents_ref[-1].append(parsed_line.tostring())
                parents_ref.pop()
            elif isinstance(parsed_line, lyxclass.LyxContainer):
                parents_ref[-1].append(parsed_line)
                parents_ref.append([parsed_line])
            else:
                parents_ref[-1].append(parsed_line)
        if len(parents_ref) > 1:
            logging.warning('found ' + str(len(parents_ref) - 1) + ' open closed tags: \n' + str(parents_ref[-1]))
        self.content = lyx_content

    @staticmethod
    def _parse_line(line: str):
        """
        Parses a single line of the document.

        :param line: The line to be parsed.
        :return: The parsed line as a LyX object or container.
        """
        if len(line) == 0:
            return line
        if line[0] != '\\':
            return line
        elif (not line.strip().startswith('\\begin')) and (not line.strip().startswith('\\end')):
            objs = line.strip().split(' ', 1)
            if len(objs) > 1:
                return lyxclass.LyxObject(objs[0][1:], objs[1])
            else:
                return lyxclass.LyxObject(objs[0][1:])
        elif line.strip().startswith('\\begin'):
            objs = line.strip().split(' ', 1)
            if len(objs) > 1:
                return lyxclass.LyxContainer(objs[0].replace('\\begin_', ''), objs[1])
            else:
                return lyxclass.LyxContainer(objs[0].replace('\\begin_', ''))

    def find_tag(self, tag: str):
        """
        Finds and returns the content with a specific tag.

        :param tag: The tag to find.
        :return: The content with the specified tag.
        """
        notvisited = [(x, [i]) for x, i in enumerate(self.content)]
        found = []
        while len(notvisited) > 0:
            obj, path = notvisited.pop(0)
            if hasattr(obj, 'tag'):
                if obj.tag == tag:
                    found.append((obj, path))
                for i, subobj in enumerate(obj.content):
                    notvisited.append((subobj, path + [i]))
            elif hasattr(obj, 'content'):
                if obj.tag == tag:
                    found.append((obj, path))
                for i, subobj in enumerate(obj.content):
                    notvisited.append((subobj, path + [i]))
        return found

    def parse_lyx_parts(self, attributes=('Section', 'Subsection', 'Subsubsection')):
        """
        Parses the LyX parts based on specified attributes.

        :param attributes: The attributes to use for parsing.
        :return: The parsed LyX parts.
        """
        lyxbody = self._get_body()
        if lyxbody is not None:
            lyx_parts = lyxclass.LyxContainer('body', attribute='', content=[])
            parents_ref = [lyx_parts]
            for i, item in enumerate(lyxbody.content):
                if isinstance(item, lyxclass.LyxContainer) and (item.attribute.strip() in attributes):
                    while parents_ref[-1].attribute.strip() in attributes and \
                            attributes.index(item.attribute.strip()) <= \
                            attributes.index(parents_ref[-1].attribute.strip()):
                        parents_ref.pop()
                    new_item = LyxPart(item)
                    parents_ref[-1].append(new_item)
                    parents_ref.append(new_item)
                else:
                    parents_ref[-1].append(item)
            return lyx_parts.content
        return []

    def _get_body(self):
        """
        Retrieves the body content of the LyX document.

        :return: The body content of the LyX document.
        """
        if hasattr(self, '_body_id'):
            self._body_id = self._get_item_by_ref(self._body_id)
        lyxbody_id = self._find_tag('body')
        if len(lyxbody_id) > 0:
            self._body_id = lyxbody_id[0]
            return self._get_item_by_ref(lyxbody_id[0])
        return None

    def _get_item_by_ref(self, ref: Iterable) -> lyxclass.LyxContainer:
        """
        Gets an item by its reference.

        :param ref: The reference to the item.
        :return: The item referenced.
        """
        next_it = self.content
        for i in ref:
            next_it = next_it[int(i)]
        return next_it

    def tostring(self):
        """
        Converts the entire LyX document to a string representation.

        :return: The string representation of the LyX document.
        """
        return '\n'.join([str(x) for x in self.content])

    def tofile(self, filename):
        """
        Writes the LyX document to a file.

        :param filename: The name of the file.
        """
        with open(filename, 'w') as file:
            file.write(self.tostring())


class SpecialDocument(LyxDocument):
    """
    Represents a special document type.
    """
    def __init__(self, default_doc='doc_default.lyx'):
        """
        Initializes a SpecialDocument.

        :param default_doc: The default document to be used.
        """
        input_str = read_project_file(default_doc)
        super().__init__(input_str)

    @staticmethod
    def executive_summary(intended_use: List[str] = None, description: List[str] = None):
        """
        Generates an executive summary.

        :param intended_use: The intended use descriptions.
        :param description: The descriptions.
        :return: The executive summary content.
        """
        purpose = LyxPart(lyxclass.LyxLayout('Subsection', 'Purpose',
                                                    layout_label='summary-purpose'))
        if intended_use is None:
            purpose.append(lyxclass.LyxLayout('Standard', 'is used for'))
        else:
            for use in intended_use:
                purpose.append(lyxclass.LyxLayout('Standard', use))

        summary_description = LyxPart(lyxclass.LyxLayout('Subsection', 'Summary of Description',
                                                          layout_label='summary-description'))
        if description is None:
            summary_description.append(
                lyxclass.LyxLayout('Standard', 'Description here'))
            summary_description.append(lyxclass.LyxLayout('Standard', 'Description here too'))
        else:
            for desc in description:
                summary_description.append(lyxclass.LyxLayout('Standard', desc))

        content = LyxPart(lyxclass.LyxLayout('Section', 'Executive Summary', layout_label='summary'),
                          content=[purpose, summary_description])
        return content

    @staticmethod
    def outputs(template_outputs: List[str] = None):
        """
        Generates the outputs section.

        :param template_outputs: The template outputs descriptions.
        :return: The outputs content.
        """
        content = LyxPart(lyxclass.LyxLayout('Subsection', 'Outputs', layout_label='outputs'))
        if template_outputs is None or len(template_outputs) == 0:
            content.append(lyxclass.LyxLayout('Standard', 'Description'))
        else:
            content.append(lyxclass.LyxLayout('Standard', 'Description'))
            content.append(lyxclass.LyxLayout('Standard', ' '.join(template_outputs)))
        return content

    @staticmethod
    def limitations(limitation_table: List[List[str]] = None):
        """
        Generates the limitations section.

        :param limitation_table: The table of limitations.
        :return: The limitations content.
        """
        content = LyxPart(lyxclass.LyxLayout('Section', 'Limitations',
                                              layout_label='limitations'))
        if limitation_table is None or len(limitation_table) == 0:
            content.append(lyxclass.LyxLayout('Standard', 'Description'))
        else:
            content.append(lyxclass.LyxLayout('Standard', lyxclass.LyxTabular(limitation_table, colWidth=[10, 28, 30, 30])))
        return content