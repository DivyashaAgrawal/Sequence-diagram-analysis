from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTPage, LTChar, LTAnno, LAParams, LTTextBox, LTTextLine

##Inherited function
class PDFPageDetailed(PDFPageAggregator):
    def __init__(self, rsrcmgr, pageno=1, laparams=None):
        PDFPageAggregator.__init__(self, rsrcmgr, pageno=pageno, laparams=laparams)
        self.rows = []
        self.comments = []
        self.page_number = 0
    def receive_layout(self, ltpage):        
        def render(item, page_number):
            if isinstance(item, LTPage) or isinstance(item, LTTextBox):
                for child in item:
                    render(child, page_number)
            elif isinstance(item, LTTextLine):
                child_str = ''a
                for child in item:
                    if isinstance(child, (LTChar, LTAnno)):
                        child_str += child.get_text()
                    if isinstance(child,LTChar):
                        font = child.fontname
                        fnt=(font.split("+"))[1].split("U")[0]
                child_str = ' '.join(child_str.split()).strip()
                if child_str:
<<<<<<< HEAD
                    row = (page_number, item.bbox[0], item.bbox[1], item.bbox[2], item.bbox[3], child_str) # bbox == (x1, y1, x2, y2)
=======
                    row = ( item.bbox[0], item.bbox[1], item.bbox[2], item.bbox[3], child_str , fnt ) # bbox == (x1, y1, x2, y2)
>>>>>>> a982b1f7c1a96570cbe6950b755cabf9fe419379
                    self.rows.append(row)
                for child in item:
                    render(child, page_number)
            return
        render(ltpage, self.page_number)
        self.page_number += 1
<<<<<<< HEAD
        self.rows = sorted(self.rows, key = lambda x: (x[0], -x[2]))
        self.result = ltpage
=======
        self.rows = sorted(self.rows, key = lambda x: ( -x[1], x[0] , x[5]))
        self.result = ltpage
>>>>>>> a982b1f7c1a96570cbe6950b755cabf9fe419379
