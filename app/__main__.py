import functions as fn
from version import getVersion
from pathlib import Path
from typing import Union

from pypdf import PdfReader, PdfWriter, Transformation, PageObject, PaperSize
from pypdf.generic import RectangleObject


w_new = PaperSize.A4.width
h_new = PaperSize.A4.height
ratio_new = float(h_new/w_new)


def doFile (thisFile : Union[str,Path,list]):

    def _doFile (_thisFile : Union[str,Path]):
        if not _thisFile:
            raise FileNotFoundError ('No file passed')
        elif not isinstance(_thisFile,Path):
            _thisFile = Path(_thisFile)
        _thisFile = _thisFile.expanduser()
        if not _thisFile.is_file():
            raise FileNotFoundError (str(_thisFile))

        try:
            _thisFile = _thisFile.relative_to('.')
        except ValueError:
            ...

        converted = _thisFile.with_stem(f"{_thisFile.stem}.A4")

        reader = PdfReader(_thisFile)
        writer = PdfWriter()

        pagesResized = 0

        for page in reader.pages:

            # resize page to fit *inside* A4
            h = float(page.mediabox.height)
            w = float(page.mediabox.width)

            scale_factor = min(h_new/h, w_new/w)

            # prepare A4 blank page
            parmsDict = dict(height = max(w_new,h_new), width = min(w_new,h_new))
            page_new = PageObject.create_blank_page(**parmsDict)

            if w == w_new and h == h_new:
                page_new.merge_page(page2 = page)
            else:
                pagesResized += 1
                def getMove (v1, v2):
                    return max(round(((v1-(v2*scale_factor))/2),0),0)

                transform = (Transformation()
                                    .scale(scale_factor,scale_factor)
                                    .translate(getMove(page_new.mediabox.width,page.mediabox.width)
                                              ,getMove(page_new.mediabox.height,page.mediabox.height)
                                              )
                            )
                page_new.merge_transformed_page(page2 = page, ctm = transform)

            writer.add_page(page_new)

            # if len(writer.pages) == 5:
            #     break

        msg = f"'{str(_thisFile)}' : "
        if pagesResized == 0:
            msg+="All pages already A4. Not creating document"
        else:
            writer.write(converted)
            msg+=f"Resized {pagesResized} of {len(reader.pages)} pages, created document"

        msg+=f"\n{' '*(len(str(_thisFile))+6)} '{str(converted.relative_to(_thisFile.parent))}'"
        if DEBUG:
            print (msg)

    if not thisFile:
        raise FileNotFoundError ('No file passed')
    elif not isinstance(thisFile,list):
        thisFile = [thisFile,]
    _ = [_doFile(_thisFile = f) for f in thisFile]

if __name__ == '__main__':
    global CONFIG, DEBUG, VERSION
    CONFIG  = fn.getConfig(Path(__file__).parent.parent.joinpath('config.ini'))
    DEBUG   = CONFIG.getboolean('APP','DEBUG')
    VERSION = getVersion()
    files   = CONFIG.getPathListCSV(section = 'FILES', option = 'NAMES')
    doFile (files)