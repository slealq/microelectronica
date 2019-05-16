

from os import walk
from os.path import join
from re import findall, match
from json import dumps
from csv import writer

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
                '% area diff': ''}
SEARCH_STATES = {'look_for_tns': False,
                 'look_for_slack':False,
                 'seq_area_in_two_lines':False}

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
        file_information['syn mode'] = [syn_mode]

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

def find_comb_cell(line, file_information):
    comb_cell_regex = r'Combinational\sCell\sCount:\s+(\d+)'
    append_only_if_match(findall(comb_cell_regex, line), file_information,
                         'Comb cell count')

def find_seq_cell(line, file_information):
    seq_cell_regex = r'Sequential\sCell\sCount:\s+(\d+)'
    append_only_if_match(findall(seq_cell_regex, line), file_information,
                         'Seq cell count')

def find_comb_area(line, file_information):
    comb_area_regex = r'Combinational\sArea:\s+(\d+.\d+)'
    append_only_if_match(findall(comb_area_regex, line), file_information,
                         'Comb area')

def find_seq_area(line, file_information):
    seq_area_title_regex = r'\s+Noncombinational\sArea:'
    seq_area_value_regex = r'\s+(\d+.\d+)'
    seq_area_complete_regex = r'Noncombinational\sArea:\s+(\d+.\d+)'

    if append_only_if_match(findall(seq_area_complete_regex, line),
                            file_information, 'Seq area'):
        return
    else:
        if not SEARCH_STATES['seq_area_in_two_lines'] and \
           match(seq_area_title_regex, line):
            SEARCH_STATES['seq_area_in_two_lines'] = True
        elif SEARCH_STATES['seq_area_in_two_lines']:
            found_it = append_only_if_match(
                findall(seq_area_value_regex, line),
                file_information, 'Seq area')
            SEARCH_STATES['seq_area_in_two_lines'] =\
                False if found_it else True
        else:
            return

def find_design_area(line, file_information):
    design_area_regex = r'Design\sArea:\s+(\d+.\d+)'
    append_only_if_match(findall(design_area_regex, line), file_information,
                         'Design Area')

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

        find_comb_cell(line, file_information)
        find_seq_cell(line, file_information)
        find_comb_area(line, file_information)
        find_seq_area(line, file_information)
        find_design_area(line, file_information)

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

def calculate_area_improvement(all_files_information):
    flat_files_paths = [keys for keys in all_files_information
                        if 'flat' in keys]

    for flat_file_path in flat_files_paths:
        flat_file_information = all_files_information[flat_file_path]
        hier_file_information = all_files_information[
            flat_file_path.replace('flat', 'hier')]

        flat_file_area =\
            float(next(iter(flat_file_information['Design Area'])))
        hier_file_area =\
            float(next(iter(hier_file_information['Design Area'])))

        flat_file_information['% area diff'] =\
            [(flat_file_area - hier_file_area)*100/hier_file_area]
        hier_file_information['% area diff'] = \
            [(hier_file_area - flat_file_area)*100/flat_file_area]

def convert_file_information_to_list_of_rows(file_information, column_list):
    amount_of_lines = len(file_information['clk'])

    list_of_rows = []

    for line in range(amount_of_lines):
        row = []
        for column in column_list:
            data = file_information[column]
            if (len(data) < amount_of_lines and line is 0) or \
               (len(data) is amount_of_lines):
                row.append(data[line])
            else:
                row.append('')
        list_of_rows.append(row)

    return list_of_rows

def dump_files_information_to_csv(all_files_information,
                                  report_name='report.csv'):

    # Write hier first then flat
    hier_files_paths = sorted([keys for keys in all_files_information
                        if 'hier' in keys])

    all_lines = []
    column_list = list(RESPONSE_ROW.keys())
    all_lines.append(column_list)

    for path in hier_files_paths:
        all_lines.extend(
            convert_file_information_to_list_of_rows(
                all_files_information[path], column_list))

        all_lines.extend(
            convert_file_information_to_list_of_rows(
                all_files_information[path.replace('hier', 'flat')],
                column_list))

    with open(report_name, 'w') as writeFile:
        csv_writer = writer(writeFile)
        csv_writer.writerows(all_lines)

if __name__ == '__main__':
    files_in_directory = get_target_files_of_dirs(TARGET_TOP_DIR, TARGET_DIRS)

    all_files_information = {}
    for directory, files in files_in_directory.items():
        for each_file in files:
            with open(each_file, 'r') as processing_file:
                all_files_information[each_file] =\
                    process_file(processing_file)

    calculate_area_improvement(all_files_information)
    dump_files_information_to_csv(all_files_information)

    print(dumps(all_files_information, indent=4))
