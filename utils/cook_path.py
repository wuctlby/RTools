


def get_hp_outpath(copypaths):
    '''
    Get the paths from the copy of train output.

    Input:
        -copypaths:
            list of paths

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
                split_paths[i] = split_paths[i] + '/AOD'
            paths += split_paths
        return paths