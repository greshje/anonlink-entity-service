
import util.file.file_util as fu
import definitions as defs
from datetime import datetime


def log(msg):
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    fu.mkdirs(defs.LRP_LOG_DIR)
    fu.append_string_to_file(dt_string + ": " + msg + "\n", defs.LRP_LOG_FILE)
