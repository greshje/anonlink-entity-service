
import util.file.file_util as fu
import definitions as defs


def log(msg):
    fu.mkdirs(defs.LRP_LOG_DIR)
    fu.write_string_to_file(msg + "\n", defs.LRP_LOG_FILE)
