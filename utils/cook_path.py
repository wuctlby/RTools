import os


def get_hp_outpath(copypaths, subpath = '/AOD'):
    '''
    Get the paths from the copy of train output.

    Input:
        -copypaths:
            list of paths
        -subpath:  
            subpath of the path

    Output:
        -list of paths
    '''
    paths = []
    if len(copypaths) == 0:
        print('the copypaths is empty')
        return []
    else:
        for copypath in copypaths:
            split_paths = copypath.split(',')
            for i in range(len(split_paths)):
                split_paths[i] = os.path.join(split_paths[i], subpath)
            paths += split_paths
        return paths