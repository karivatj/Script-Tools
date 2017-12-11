iPost-PDF conversion tool is able to take .doc or .docx files and convert them to PDF. If the PDF is bundled with an appropriate XML file it bundles them together to form a compliant iPost package.

The script will try to invoke Microsoft Word via comtypes. If this fails it fallbacks to LibreOffice. Thus either Word or LibreOffice should be installed inorder for this script to function properly.

#### Usage

python ipost_converter.py [OPTIONS]

```
Try 'ipost_converter.py --help' for more information.

Options:
  --version                 show program's version number and exit
  -h, --help                show this help message and exit
  --libreoffice=Boolean     try to use LibreOffice as the primary converter
  --workdir=WORKDIR         working directory where the script scans for files to convert
```