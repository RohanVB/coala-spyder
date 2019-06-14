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
        output = UseCoala.specific_file(None, '*.py')
        if output is None:
            return None
        output_json = json.loads(output)['results']
        res = []
        for key, problems in output_json.items():
            # section = key
            for problem in problems:
                message = problem['message']
                origin = problem['origin']
                real_message = '{}: {}'.format(origin, message)
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
                        'data': {
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
                        }
                    })
                    result_list = [res[result_val]['file_name'] for result_val, val in enumerate(res)]
                    message_list = [res[result_val]['data'] for result_val, val in enumerate(res)]
                    final_list = list(zip(result_list, message_list))
        return final_list, filename

    def give_output():
        x, y = UseCoala.output_to_diagnostics()
        file_list = []
        line_list = []
        character_list = []
        message_list = []
        for i in x:
            file_value = i[0]
            line_value = str(i[1]['range']['start']['line']) + '~'
            message_value = i[1]['message']
            character_value = str(i[1]['range']['start']['character']) + ';'
            line_list.append(line_value)
            message_list.append(message_value)
            character_list.append(character_value)
            file_list.append(file_value)
        zipped_list = list(zip(line_list, character_list, message_list))
        my_dict = {'C': zipped_list}

        final_tuple = (y, my_dict)
        return [final_tuple]


# with open('/Users/rohan/.spyder-py3-dev/coala.results', 'wb') as fp:
#     pickle.dump(UseCoala.give_output(), fp)

if __name__ == '__main__':
    x = UseCoala.give_output()
    messages = ([two for one, two in x])
    for i in messages:
        dict_val = i
    print(dict_val)
