import sys
sys.path.append('..')

from ML.Prepare.MergedTableForML import merge_DF_singeFile

def path_filter(file_paths):
    '''
    Filter the paths, if there is a merged file in the farther path,

    Input:
        the list of paths
        
    Output:
        the list of paths that pass the filter
        which means the farther path have the AnalysisResults.root
        that is the merged file of the sub paths in the farther path
    '''
    do_filter = True
    while do_filter:
        do_filter = False
        for path in file_paths:
            if 'stage' in path.lower():
                farther_path = path.lower().split('/stage')[0]
                for this_path in file_paths[:]:
                    if farther_path in this_path and farther_path + 'AnalysisResults.root' != this_path:
                        file_paths.remove(this_path)
                        do_filter = True
            if 'AnalysisResults.root' in path:
                farther_path = path.replace('AnalysisResults.root', '')
                for this_path in file_paths[:]:
                    if farther_path in this_path and farther_path + 'AnalysisResults.root' != this_path:
                        file_paths.remove(this_path)
                        do_filter = True

    unique_paths = []
    for path in file_paths:
        if 'AnalysisResults.root' in path:
            farther_path = path.replace('AnalysisResults.root', '')
            if not any(farther_path in p for p in unique_paths):
                unique_paths.append(path)
            else:
                print('Warning: The farther path has been added')
        else:
            print('Warning: the path does not have AnalysisResults.root')

    # file_paths = unique_paths
    
    file_paths.sort(key=len)
    print(file_paths)
    print(len(file_paths))
    unique_paths.sort(key=len)
    print(unique_paths)
    print(len(unique_paths))
    
if __name__ == '__main__':
    
    inputdir = '/home/wuct/ALICE/Results/324130'
    inputName = 'AnalysisResults.root'
    
    pre_file_paths = merge_DF_singeFile(inputdir, inputName, False)
    
    file_paths = [path.replace(inputdir + '/', '') for path in pre_file_paths]
    
    file_paths.sort(key=len)
        
    path_filter(file_paths)

    pass