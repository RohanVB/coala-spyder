"""
Run coala on specific files only
Authored by: https://github.com/li-boxuan and https://github.com/gaocegege
# todo: add proper references
"""

import sys
import os
import io
from contextlib import redirect_stdout
import json
from coalib import coala
import pickle


class UseCoala(object):

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
        return output

    def output_to_diagnostics():
        """
        Turn output to diagnostics.
        """
        output = UseCoala.specific_file(None, 'run_coala.py')
        if output is None:
            return None
        output_json = json.loads(output)['results']
        res = []
        for key, problems in output_json.items():
            # section = key
            for problem in problems:
                print(problem)
                message = problem['message']
                origin = problem['origin']
                real_message = '[{}: {}]'.format(origin, message)
                for code in problem['affected_code']:
                    filename = code['start']['file']

                    def convert_offset(x):
                        return x - 1 if x else x

                    start_line = convert_offset(code['start']['line'])
                    start_char = convert_offset(code['start']['column'])
                    end_line = convert_offset(code['end']['line'])
                    end_char = convert_offset(code['end']['column'])

                    if start_char is None or end_char is None:
                        start_char = 0
                        end_line = start_line + 1
                        end_char = 0

                    res.append({
                        'file_name': filename,
                        'range': {
                            'start': {
                                'line': start_line,
                                'character': start_char
                            },
                            'end': {
                                'line': end_line,
                                'character': end_char
                            }
                        },
                        'message': real_message  # contains origin and message
                        })
        return res


with open('/Users/rohan/.spyder-py3-dev/coala.results', 'wb') as fp:
    pickle.dump(UseCoala.output_to_diagnostics(), fp)
