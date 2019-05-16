

from os import walk
from os.path import join
from re import findall
from json import dumps

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
SEARCH_STATES = {'look_for_tns': False,
                 'look_for_slack':False}

def append_only_if_match(match, file_information, key):
    if match:
        if file_information[key]:
            file_information[key].append(next(iter(match)))
        else:
            file_information[key] = match
        return True
    return False

def find_clks_titles(line, file_information):
    clks_regex = r'Timing\sPath\sGroup\s\'(clk_\S+|\S+_clk|\S+_clk\S+)\''
    return append_only_if_match(findall(clks_regex, line),
                                file_information, 'clk')

def find_modules_name(line, file_information):
    modules_name_regex = r'Design\s:\s(module_\S)'
    append_only_if_match(findall(modules_name_regex, line),
                         file_information, 'module')

def find_synth_mode(syn_mode, file_information):
    # Only save the name once
    if not file_information['syn mode']:
        file_information['syn mode'] = syn_mode

def find_clk_tns(line, file_information, search=False):
    if search:
        tns_regex = r'Total\sNegative\sSlack:\s+([-\d]+\.\d+)'
        return append_only_if_match(
            findall(tns_regex, line), file_information, 'TNS')

def find_clk_slack(line, file_information, search=False):
    if search:
        slack_regex = r'Critical\sPath\sSlack:\s+([-\d]+\.\d+)'
        return append_only_if_match(
            findall(slack_regex, line), file_information, 'slack')

def process_file(processing_file):
    file_information = dict(RESPONSE_ROW)

    for line in processing_file:
        find_modules_name(line, file_information)

        find_synth_mode(directory, file_information)

        if find_clks_titles(line, file_information):
            SEARCH_STATES['look_for_tns'] = True
            SEARCH_STATES['look_for_slack'] = True

        if find_clk_tns(line, file_information,
                        SEARCH_STATES['look_for_tns']):
            SEARCH_STATES['look_for_tns'] = False

        if find_clk_slack(line, file_information,
                          SEARCH_STATES['look_for_slack']):
            SEARCH_STATES['look_for_slack'] = False

    print(dumps(file_information, indent=4))
    return file_information

def get_target_files_of_dirs(top_directory: str,
                             target_directories: list) -> dict:
    """Return a dictionary with all files of the given directories.

    The keys of the dictionary are the names of the containning directories,
    and the values a list with complete paths to each file inside the
    directory.
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
                process_file(processing_file)
