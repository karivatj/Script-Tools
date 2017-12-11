# !/usr/bin/python
#  -*- coding: utf-8 -*-
# code utilized in this script include modified examples from https://stackoverflow.com/a/377028 and https://stackoverflow.com/a/6018039

import time
import sys
import os
import zipfile
import comtypes.client
import logging
import shutil
from subprocess import call
from optparse import OptionParser

# setup logging
# create logger with 'ipost_converter'
logger = logging.getLogger('ipost_converter')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('debug.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

class ConversionError(Exception):
    pass

# function that tests if an executable is present in the system
def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)

    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def listfiles(path):
    arr = []
    for files in next(os.walk(path))[2]:
        arr.append(path + "\\" + files)
    return arr

def getWord():
    word = comtypes.client.CreateObject('Word.Application')
    word.Visible = False
    return word    

if __name__== "__main__":
    logger.info("Doc to iPost-PDF conversion tool 0.1")
    parser = OptionParser(usage="Usage: %prog [OPTIONS]\nTry '%prog --help' for more information.", version="%prog 1.0")
    parser.add_option("--libreoffice",
                  action="store",
                  dest="try_libre",
                  default=False,
                  help="try to use LibreOffice as the primary converter",)
    parser.add_option("--workdir",
                  action="store",
                  dest="workdir",
                  default=os.getcwd(),
                  help="working directory where the script scans for files to convert")
    parser.add_option("--archivedir",
                  action="store",
                  dest="archivedir",
                  default=os.getcwd() + "\\archive",
                  help="archive directory where the script puts the processed files after conversion")   
    parser.add_option("--zipdir",
                  action="store",
                  dest="zipdir",
                  default=os.getcwd() + "\\zip",
                  help="directory where the script puts the finalized iPost packages")                         
    (options, args) = parser.parse_args()

    wdFormatPDF = 17

    word = None
    word_enabled = False
    libreoffice_enabled = False

    work_directory = options.workdir

    logger.info("Using: " + work_directory + " as working directory")

    # check if archive directory exists. If not, create one
    archive_directory = options.archive_directory
    if not os.path.exists(archive_directory):
        os.makedirs(archive_directory)

    logger.info("Using: " + archive_directory + " as archive directory")

    # check if zip directory exists. If not, create one
    zip_directory = options.zipdir
    if not os.path.exists(zip_directory):
        os.makedirs(zip_directory)

    logger.info("Using: " + zip_directory + " as zip directory")

    try:
        if options.try_libre == False:
            logger.info("Trying to set-up external file converter using Word...")
            word = getWord()
            word_enabled = True
            logger.info("Done!")
    except Exception as e:
        word_enabled = False
        word = None
        logger.info("Eror ({0})".format(e))
        logger.info("Creating Word instance failed. Check if you have Office installed.")

    if word_enabled == False:
        logger.info("Trying to set-up external file converter using LibreOffice...")

        if(which("soffice.exe") == None):
            logger.info("LibreOffice not present in target system. No other converters available. Exiting...")
            sys.exit()
        else:
            logger.info("Done!")
            libreoffice_enabled = True

    if word_enabled:
        logger.info("Using Word as the primary file converter")
    elif libreoffice_enabled:
        logger.info("Using LibreOffice as the primary file converter")
    else:
        logger.info("No suitable file converter available Exiting...")
        sys.exit(0)

    while True:
        try:
            waittime = 10       

            # Step 1: Convert .doc/x files to .pdf
            # get list of files
            arr = listfiles(work_directory)

            # filter based on file extension
            arr_doc = [x for x in arr if x.endswith(".doc") or x.endswith(".docx")]

            if len(arr_doc) == 0:
                logger.info("No files to convert. Waiting for {0} seconds".format(waittime + 10))
                while waittime + 10 > 0:
                    waittime -= 1
                    time.sleep(1)
                continue

            # conversion
            for file in arr_doc:
                logger.info("Converting file {0}...".format(file))
                if word_enabled:
                    file_stripped = ""
                    if file.endswith(".doc"):
                        file_stripped = file.strip(".doc")
                    elif file.endswith(".docx"):
                        file_stripped = file.strip(".docx")
                    try:
                        filename = file_stripped + ".pdf"
                        doc = word.Documents.Open(file)
                        doc.SaveAs(filename, FileFormat=wdFormatPDF)
                        doc.Close()
                        # check if the file exists. If something went wrong attempt it again with LibreOffice
                        if not os.path.isfile(filename):
                            raise ConversionError
                    except ConversionError as e:
                        logging.error("Conversion failed. Trying again with LibreOffice..")
                        if(which("soffice.exe") == None):
                            logger.info("LibreOffice not present in target system. No other converters available. Exiting...")
                            sys.exit()
                        else:
                            logger.info("Fallback to LibreOffice succesfull!")
                            return_code = call("soffice --headless --convert-to pdf " + file, shell=True)
                    except Exception as e:
                        logger.info("Conversion failed with Word! Retrying...")                        
                        try:
                            word = getWord()
                            word.Visible = False
                            doc = word.Documents.Open(file)
                            doc.SaveAs(filename, FileFormat=wdFormatPDF)
                            doc.Close()
                            # check if the file exists. If something went wrong attempt it again with LibreOffice
                            if not os.path.isfile(filename):
                                raise ConversionError
                        except ConversionError as e:
                            logging.error("Conversion failed. Trying again with LibreOffice..")
                            if(which("soffice.exe") == None):
                                logger.info("LibreOffice not present in target system. No other converters available. Exiting...")
                                sys.exit()
                            else:
                                logger.info("Fallback to LibreOffice succesfull!")
                                return_code = call("soffice --headless --convert-to pdf " + file, shell=True)
                        except Exception as e:
                            logger.info("Conversion with Word fails repeatedly. Falling back to LibreOffice!")
                            word.Quit()
                            word_enabled = False
                            if(which("soffice.exe") == None):
                                logger.info("LibreOffice not present in target system. No other converters available. Exiting...")
                                sys.exit()
                            else:
                                logger.info("Fallback to LibreOffice succesfull!")
                                libreoffice_enabled = True
                                return_code = call("soffice --headless --convert-to pdf " + file, shell=True)

                elif libreoffice_enabled:
                    return_code = call("soffice --headless --convert-to pdf " + file, shell=True)

            logger.info("Conversion completed...")

            # Step 2: bundle xml and the converted pdf to zip file
            # get list of files            
            arr = listfiles(work_directory)

            # filter all pdf files            
            arr_pdf = [x for x in arr if x.endswith(".pdf")]

            logger.info("Creating zip files...")
            for file in arr_pdf:
                # xml file named similarly to the pdf should co-exist with the file
                if os.path.isfile(file.replace("pdf", "xml")):
                    file = file.split("\\")[-1] # strip the path and select the last element
                    logger.info("Creating zip file for {0}".format(file.strip(".pdf")))
                    try:
                        zf = zipfile.ZipFile(file.replace("pdf", "zip"), "w")
                        zf.write(file)
                        zf.write(file.replace("pdf", "xml"))
                        zf.close()
                    except PermissionError as e:
                        logger.info("Failed to create the zip file ({0})".format(e))
                        continue
                    # delete the pdf file we dont need it anymore and move the zip file to its final resting place
                    os.remove(file)
                    zip_file = file.replace("pdf", "zip")
                    try:
                        os.rename(zip_file, zip_directory + "\\" + zip_file)
                    except FileExistsError as e:
                        logger.info("Zip file in archive exists. Attempting to replace it...")
                        os.remove(zip_directory + "\\" + zip_file)
                        os.rename(zip_file, zip_directory + "\\" + zip_file)                        
                        pass
                else:
                    logger.info("XML does not exist for {0}. Skipping zipping step.".format(file.strip(".pdf")))

            # Step 3: We're done, move the converted files to archive
            logger.info("Moving files to archive...")
            for file in arr_doc:
                filename = file.split("\\")[-1]
                archive_file = archive_directory + "\\" + filename

                # try to move the doc file to archive
                try:
                    shutil.copy(file, archive_file)
                    os.remove(file)
                except FileExistsError as e:
                    logger.info("Doc file in archive exists. Attempting to replace it...")
                    os.remove(archive_file)
                    os.rename(file, archive_file)
                    pass
                except PermissionError as e:
                    logger.info("Doc file in use. Check for permissions. Skipping...")
                    pass
                except FileNotFoundError as e:
                    logger.info("Doc file not found or does not exist. Skipping...")
                    pass

                if file.endswith("doc"):
                    xml_filename = file.split("\\")[-1].replace("doc", "xml")
                else:
                    xml_filename = file.split("\\")[-1].replace("docx", "xml")

                xml_archive_file = archive_directory + "\\" + xml_filename

                try:
                    shutil.copy(xml_filename, xml_archive_file)
                    os.remove(xml_filename)
                except FileExistsError as e:
                    logger.info("XML file in archive exists. Attempting to replace it...")                        
                    os.remove(xml_archive_file)
                    os.rename(xml_filename, xml_archive_file)
                    pass
                except PermissionError as e:
                    logger.info("XML file in use. Check for permissions. Skipping...")
                    pass                    
                except FileNotFoundError as e:
                    logger.info("XML file not found or does not exist. Skipping...")
                    pass

            logger.info("Done. Waiting for {0} seconds".format(waittime))

            while waittime > 0:
                waittime -= 1
                time.sleep(1)                

        except KeyboardInterrupt:
            break

    if word_enabled:
        word_enabled = False
        try:
            word.Quit()
        except Exception as e:
            pass

    logger.info("Exiting...")