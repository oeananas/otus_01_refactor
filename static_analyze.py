import ast
import os
import collections

from nltk import pos_tag


def flat(_list):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
    return sum([list(item) for item in _list], [])


def is_verb(word):
    """ return True if word is verbose"""
    if not word:
        return False
    pos_info = pos_tag([word])
    return pos_info[0][1] == 'VB'


def get_content_from_file(filename):
    """ read file and return content """
    with open(filename, 'r', encoding='utf-8') as attempt_handler:
        main_file_content = attempt_handler.read()
    return main_file_content


def get_py_filenames(dir_path):
    """ return filenames endswith .py """
    filenames = []
    for dirname, dirs, files in os.walk(dir_path, topdown=True):
        files = [file for file in files if file.endswith('.py')]
        for file in files:
            filenames.append(os.path.join(dirname, file))
        if len(filenames) == 100:
            break
    return filenames


def get_trees(path, with_filenames=False, with_file_content=False):
    """ return list of trees from path """
    trees = []
    filenames = get_py_filenames(path)
    for filename in filenames:
        main_file_content = get_content_from_file(filename)
        try:
            tree = ast.parse(main_file_content)
        except SyntaxError:
            tree = None
        if with_filenames:
            if with_file_content:
                trees.append((filename, main_file_content, tree))
            else:
                trees.append((filename, tree))
        else:
            trees.append(tree)
    return trees


def get_all_names(tree):
    """ return names """
    return [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]


def get_verbs_from_name(name):
    """ return verbs from name of function """
    return [word for word in split_snake_case_name_to_words(name) if is_verb(word)]


def split_snake_case_name_to_words(name):
    """ return list of verbs from snake case name """
    return name.split('_')


def exclude_magic_function_names(func_names_list):
    """ return func names without __name__ """
    return [f for f in func_names_list if not (f.startswith('__') and f.endswith('__'))]


def get_all_words_in_path(path):
    """ return list of split verbs from path """
    trees = get_trees(path)
    all_words = [f for f in flat([get_all_names(t) for t in trees])]
    words = exclude_magic_function_names(all_words)
    return flat([split_snake_case_name_to_words(word) for word in words])


def get_function_names(path):
    """ return define functions """
    trees = get_trees(path)
    all_f_names = flat([[node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)] for t in trees])
    return exclude_magic_function_names(all_f_names)


def get_top_verbs_in_path(path, top_size=10):
    all_words = get_all_words_in_path(path)
    verbs = flat([get_verbs_from_name(word) for word in all_words])
    return collections.Counter(verbs).most_common(top_size)


def get_top_function_verbs_in_path(path, top_size=10):
    """ return most common words, top 10 by default """
    functions = get_function_names(path)
    verbs = flat([get_verbs_from_name(function_name) for function_name in functions])
    return collections.Counter(verbs).most_common(top_size)


def get_top_functions_names_in_path(path, top_size=10):
    """ return most common names of functions, top 10 by default """
    functions = get_function_names(path)
    return collections.Counter(functions).most_common(top_size)


if __name__ == '__main__':
    wds = []
    projects = [
        'django',
        'flask',
        'pyramid',
        'reddit',
        'requests',
        'sqlalchemy',
    ]
    for project in projects:
        path = os.path.join('.', project)
        wds += get_top_verbs_in_path(path)
    top_size = 200
    print('total %s words, %s unique' % (len(wds), len(set(wds))))
    for word, occurence in collections.Counter(wds).most_common(top_size):
        print(word, occurence)
