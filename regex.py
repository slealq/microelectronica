

from os import walk
from os.path import join
from re import findall

TARGET_TOP_DIR = './tarea_regexp'
TARGET_DIRS = ['flat', 'hier']
RESPONSE_ROW = {'module': '',
                'syn mode': '',
                'clk': '',
                'slack': '',
                'TNS': '',
                'Comb cell count': '',
                'Seq cell count': '',
                'Comb area': '',
                'Seq area': '',
                'Design Area': '',
                '% area impr': ''}


def find_modules_name(file_content, row_dict):
    modules_name_regex = r'Design\s:\s(module_\S)'

    matches = findall(modules_name_regex, file_content)
    assert len(matches) == 1
    row_dict['module'] = next(iter(matches))


def find_syn_mode(syn_mode, row_dict):
    row_dict['syn mode'] = syn_mode

def get_target_files_of_dirs(top_directory: str,
                             target_directories: list) -> dict:

    """Return a dictionary with all files of the given directories.

    The keys of the dictionary are the names of the files, and the values
    a list with complete paths to each file inside the directory.
    """

    return {target_dir: [join(TARGET_TOP_DIR, target_dir, each_file) for
            each_file in files] for target_dir in TARGET_DIRS for subdirs,
            dirs, files in walk(join(TARGET_TOP_DIR, target_dir))}


if __name__ == '__main__':
    files_in_directory = get_target_files_of_dirs(TARGET_TOP_DIR, TARGET_DIRS)

    for directory, files in files_in_directory.items():
        for each_file in files:
            print(each_file)
            with open(each_file, 'r') as processing_file:
                new_row = dict(RESPONSE_ROW)
                file_content = processing_file.read()
                find_modules_name(processing_file, new_row)
                print(new_row)
