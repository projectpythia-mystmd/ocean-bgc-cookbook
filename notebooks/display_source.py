from IPython.display import display, HTML
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
import inspect

def display_source(obj, color=True):
    obj_src = inspect.getsource(obj)
    if color:
        display(HTML(highlight(obj_src, PythonLexer(), HtmlFormatter())))
    else:
        print(obj_src)