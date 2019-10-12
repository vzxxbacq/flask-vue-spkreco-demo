import logging
import sys


def init_logger(name):
    logging.basicConfig(stream=sys.stdout, format='%(asctime)s [%(filename)s %(lineno)d] %(levelname)s: %(message)s',
                        datefmt='%m-%d %H:%M:%S', level=logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(filename)s: %(lineno)d] %(levelname)s: %(message)s',
                                  '%m-%d %H:%M:%S')
    return _single_logger(name, formatter)


def _single_logger(name, formatter):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('log/%s.txt' % name)
    ch = logging.StreamHandler()
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


import functools
import logging
import sys
import traceback


class _LogTracer(object):
    def __init__(self):
        self._last_frame = None

    def tracer(self, frame, event, *extras):
        if event == 'return':
            self._last_frame = frame

    @property
    def last_frame(self):
        return self._last_frame


def log_locals_on_exit(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        log_tracer = _LogTracer()
        sys.setprofile(log_tracer.tracer)
        try:
            result = fn(*args, **kwargs)
        except Exception:
            logging.exception("Get Exception in function %s" % fn.__name__)
            frame = sys.exc_info()[2]
            formattedTb = traceback.format_tb(frame)
            frame = frame.tb_next
            logging.debug("Locals as follows:")
            while frame:
                logging.debug(formattedTb.pop(0).replace("\t", "").replace("\n", '\t'))
                vars = frame.tb_frame.f_locals
                for k, v in vars.items():
                    logging.debug("Name: " + k + "\t Type:" + str(type(v)) + "\tValue: " + str(v))
                frame = frame.tb_next
            return
        finally:
            sys.setprofile(None)
        frame = log_tracer.last_frame
        _locals = {}
        logging.debug("Call function " + fn.__name__)
        logging.debug("Locals as follows:")
        for k, v in frame.f_locals.items():
            _locals[k] = repr(v)
            logging.debug("Name: " + k + "\t Type:" + str(type(v)) + "\tValue: " + str(v))
        return result
    return inner