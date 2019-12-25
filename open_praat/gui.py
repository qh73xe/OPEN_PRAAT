import eel
from pathlib import Path
from logger import createLogger

PROC = None
LOGGER = createLogger(__name__)


@eel.expose
def get_projects():
    from project import CONFDIR
    return [{"text": str(d.name), "val": str(d)} for d in CONFDIR.iterdir()]


@eel.expose
def get_filepath(val):
    import json
    jpath = Path(val).joinpath("filelist.json")
    if jpath.exists():
        LOGGER.info("GET:FILEPATH:{}".format(jpath))
        with open(str(jpath)) as f:
            result = json.load(f)
        return {"result": result}
    else:
        return {"error": "FILE NOT FOUND"}


@eel.expose
def get_gui(val):
    import json
    jpath = Path(val).joinpath("gui.json")
    if jpath.exists():
        LOGGER.info("GET:GUI:{}".format(jpath))
        with open(str(jpath)) as f:
            result = json.load(f)
        return {"result": result}
    else:
        return {"error": "FILE NOT FOUND"}


@eel.expose
def get_tires(val):
    from praat import get_tire_names
    return get_tire_names(val)


@eel.expose
def open_praat(wpath, tgpath):
    from praat import Praat
    global PROC
    if PROC:
        PROC.close()
    PROC = Praat(wpath, tgpath)
    PROC.view()
    return {"wav": wpath, "tg": tgpath}


@eel.expose
def add_boundaly(tier):
    global PROC
    if PROC:
        PROC.addBoundaly(tier, "")
        return True
    return False


@eel.expose
def remove_boundaly(tier):
    global PROC
    if PROC:
        PROC.removeBoundaly(tier)
        return True
    return False


@eel.expose
def add_word(tier, word):
    global PROC
    if PROC:
        PROC.addWord(tier, word)
        return True
    return False


@eel.expose
def save_textgrid():
    global PROC
    if PROC:
        PROC.saveTextGrid()
        return PROC.tgpath
    return False


@eel.expose
def finish_praat(project, fileobj):
    import json
    global PROC
    if PROC:
        PROC.saveTextGrid()
        PROC.close()
        PROC = None
        jpath = Path(project).joinpath("filelist.json")
        LOGGER.info(str(jpath))
        if jpath.exists():
            with open(str(jpath), 'w') as f:
                json.dump({"files": fileobj}, f, indent=4)
        return True
    return False


def start_gui():
    LOGGER.info("START:GUI")
    template_dir = Path(__file__).parent.joinpath("template").resolve()
    eel.init(str(template_dir))
    eel.start('index.html')


if __name__ == "__main__":
    try:
        start_gui()
    except (SystemExit, KeyboardInterrupt) as e:
        LOGGER.info(e)
        if PROC:
            LOGGER.error(e)
            PROC.close()
    except MemoryError as e:
        LOGGER.error(e)
        if PROC:
            LOGGER.error(e)
            PROC.close()
    LOGGER.info("CLOSED:GUI")
