# LyX Document Utilities

This project provides a set of Python classes and utilities to facilitate the creation and manipulation of LyX documents programmatically. The main components include handling various LyX objects, containers, and layouts, as well as providing mechanisms to read, parse, and generate LyX documents.

## Project Structure

### Modules

1. **lyxclass.py**
   - Contains the definitions for `LyxObject`, `LyxContainer`, `LyxLabel`, `LyxReference`, `LyxLayout`, `LyxTabular`, and `LyxGraphics`.
   - These classes represent various components and structures within a LyX document.

2. **lyxdoc.py**
   - Contains the definitions for `LyxPart`, `LyxDocument`, and `SpecialDocument`.
   - Provides utilities for reading project files, parsing document content, and generating sections and summaries within a LyX document.

### Classes and Functions

#### lyxclass.py

- **LyxObject**: Represents a basic LyX object with a tag and an optional attribute.
- **LyxContainer**: Represents a container for multiple LyX objects.
- **LyxLabel**: Represents a LyX label inset.
- **LyxReference**: Represents a LyX reference inset.
- **LyxLayout**: Represents a LyX layout container.
- **LyxTabular**: Represents a LyX tabular container.
- **LyxGraphics**: Represents a LyX graphics container.

#### lyxdoc.py

- **read_project_file**: Reads the content of a project file.
- **LyxPart**: Represents a part of a LyX document.
- **LyxDocument**: Represents a LyX document and provides methods to parse and manipulate its content.
- **SpecialDocument**: A specialized LyxDocument for any special purposes, including methods to generate executive summaries, outputs, and limitations.

## Installation

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Usage

### Creating and Manipulating LyX Documents

You can create a new LyX document by initializing `LyxDocument` with a string containing the document content. The document can then be manipulated using various methods provided by the classes.

```python
from lyxdoc import SpecialDocument, read_project_file

# Read and parse a project file
input_string = read_project_file('path/to/file.lyx')
document = SpecialDocument(input_string)

# Find and print sections
sections = document.find_tag('Section')
for section in sections:
    print(section)

# Generate and append an executive summary
summary = document.executive_summary(['Use case 1', 'Use case 2'], ['Description 1', 'Description 2'])
document.content.append(summary)

# Save the document to a file
document.tofile('path/to/output.lyx')
```
### Generating Outputs and Limitations

`SpecialDocument` provides static methods to generate sections related to outputs and limitations.

#### Generating Outputs

You can generate the outputs section by using the `outputs` method. This method accepts a list of template outputs and returns a `LyxPart` object containing the outputs section.

```python
# Generate outputs
outputs = SpecialDocument.outputs(['Output 1', 'Output 2'])

# Generate limitations
limitations = SpecialDocument.limitations([['Limitation 1', 'Description'], ['Limitation 2', 'Description']])

# Append to the document
document.content.append(outputs)
document.content.append(limitations)
```