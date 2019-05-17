"""
Run coala on specific files only
Authored by: https://github.com/li-boxuan and https://github.com/gaocegege
# todo: add proper references
"""

import sys
import os
import io
from contextlib import redirect_stdout

from coalib import coala

class use_coala(object):

    def log(*args, **kwargs):
        return print(*args, file=sys.stderr, **kwargs), sys.stderr.flush()

    def specific_file(working_dir, file):
        sys.argv = ['', '--json', '--find-config', '--limit-files', file]
        if working_dir is None:
            working_dir = '.'
        os.chdir(working_dir)
        f = io.StringIO()
        with redirect_stdout(f):
            retval = coala.main()
        output = None
        if retval == 1:
            output = f.getvalue()
            if output:
                use_coala.log('Output =', output)
            else:
                use_coala.log('No results for the file')
        elif retval == 0:
            use_coala.log('No issues found')
        else:
            use_coala.log('Exited with:', retval)
        return output
