import os.path
import sys
from magicalimport.compat import _create_module
from magicalimport.compat import import_module as import_module_original


def expose_all_members(module, globals_=None, _depth=2):
    members = {k: v for k, v in module.__dict__.items() if not k.startswith("_")}
    return expose_members(module, members, globals_=globals_, _depth=_depth)


def expose_members(module, members, globals_=None, _depth=1):
    if globals_ is None:
        frame = sys._getframe(_depth)
        globals_ = frame.f_globals
    globals_.update({k: module.__dict__[k] for k in members})
    return globals_


def import_from_physical_path(path, as_=None, here=None):
    if here is not None:
        here = here if os.path.isdir(here) else os.path.dirname(here)
        here = os.path.normpath(os.path.abspath(here))
        path = os.path.join(here, path)
    module_id = as_ or path.replace("/", "_").rsplit(".py", 1)[0]
    if module_id in sys.modules:
        return sys.modules[module_id]
    return _create_module(module_id, path)


def import_module(module_path, here=None, sep=":"):
    _, ext = os.path.splitext(module_path)
    if ext == ".py":
        return import_from_physical_path(module_path, here=here)
    else:
        return import_module_original(module_path)


def import_symbol(sym, here=None, sep=":", ns=None):
    if ns is not None and sep not in sym:
        sym = "{}{}{}".format(ns, sep, sym)
    module_path, fn_name = sym.rsplit(sep, 2)
    try:
        module = import_module(module_path, here=here, sep=sep)
        return getattr(module, fn_name)
    except (ImportError, AttributeError) as e:
        sys.stderr.write("could not import {!r}\n{}\n".format(sym, e))
        raise
