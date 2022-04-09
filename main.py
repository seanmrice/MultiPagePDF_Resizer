import PyPDF2
from PyPDF2 import PdfFileMerger
import glob
import os

# The working directory where the PDF to process exists
working_dir = "/Windows/Main/PDF Resizer/"

# The temporary directory (that exists) for intermediate files to use during the correction of each page
temp_dir = "/Windows/Main/PDF Resizer/temp/"

# The PDF file to be processed
pdf_file = "Input_PDF_File.pdf"

# We have to open the file prior to entering the loop to avoid a bug with PyPDF2
pdf_in_file = open(pdf_file,'rb')

# SizeCheck makes sure we don't process a file that already has the correct dimensions
# Returns false when a PDF does not need resizing, returns true when it needs to be resized
def SizeCheck(currentPdfWidth, currentPdfHeight, newHeight, newWidth):
    if currentPdfWidth == newWidth and currentPdfHeight == newHeight:
        print("PDF does not need resizing")
        return "false"
    else:
        return "true"

# OrientationCheck returns the orientation of the PDF page (portrait or landscape) as a string
def OrientationCheck(currentPdfWidth, currentPdfHeight):
    if currentPdfWidth > currentPdfHeight:
        return "landscape"
    else:
        return "portrait"
    
needsResize = "true"

#LTR
LTR_h = 612
LTR_w = 792

#TAB
TAB_h = 792
TAB_w = 1224

inputpdf = PyPDF2.PdfFileReader(pdf_in_file, strict=False)
pages_no = inputpdf.numPages

# Check if temp dir is actually there, if not, then create it under the working directory
temp_dir_check = os.path.exists(temp_dir)
if temp_dir_check == False:
    os.mkdir(working_dir + "temp/")

for i in range(pages_no):
    inputpdf = PyPDF2.PdfFileReader(pdf_in_file)
    currentPage = inputpdf.getPage(i)
    
    pdfMediaBox = currentPage.mediaBox
    currentPdfWidth = pdfMediaBox[2]
    currentPdfHeight = pdfMediaBox[3]
    orientation = OrientationCheck(currentPdfWidth, currentPdfHeight)
    if orientation == "landscape":
        if pdf_file.upper().find("TAB") != -1:
            newWidth = TAB_w
            newHeight = TAB_h
        elif pdf_file.upper().find("LTR") != -1:
            newWidth = LTR_w
            newHeight = LTR_h
    elif orientation == "portrait":
        if pdf_file.upper().find("TAB") != -1:
            newWidth = TAB_h
            newHeight = TAB_w
        elif pdf_file.upper().find("LTR") != -1:
            newWidth = LTR_h
            newHeight = LTR_w
    needsResize = SizeCheck(currentPdfWidth, currentPdfHeight, newHeight, newWidth)            
    if needsResize == "true": currentPage.scaleTo(newWidth, newHeight)
    else: break
    
    output = PyPDF2.PdfFileWriter()
    currentPage.scaleTo(newWidth, newHeight)
    output.addPage(currentPage)
    
    # Each page will temporarily be seperately written to a PDF file in the temp directory
    with open(temp_dir + "document-page%s.pdf" % i, "wb") as outputStream:
        output.write(outputStream)
pdf_in_file.close()

if needsResize == "true":
    file_list = glob.glob(temp_dir + "*document-page*.pdf")
    file_list.sort()
    
    # Append each merged page to the output document (original filename of the input PDF)
    merger = PdfFileMerger()
    for pdf in file_list:
        merger.append(pdf)

    merger.write(working_dir + pdf_file)
    merger.close()

    for pdf in file_list:
        if os.path.exists(pdf):
            os.remove(pdf)
print("Processing of file:", pdf_file, "complete.")

