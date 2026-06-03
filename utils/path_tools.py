import os

def get_project_root()->str:
    '''获取当前项目路径'''
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    project_root = os.path.dirname(current_dir)
    return project_root

def get_abs_path(relativepath:str)->str:
    '''根据相对路径获取绝对路径'''
    project_root = get_project_root()
    abs_path = os.path.join(project_root,relativepath)
    return abs_path

if __name__ == '__main__':
    print(get_abs_path("config.txt"))