import sys
import os
import concurrent.futures
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
    
def is_valid_root_file(file_path):
    command = f"rootls {file_path}"
    return os.system(command) == 0

def merge_files(file_list, output_file):
    valid_files = [f for f in file_list if is_valid_root_file(f)]
    if len(valid_files) < 2:
        print(f"Warning: Not enough valid files to merge: {valid_files}")
        return
    command = f"hadd -f {output_file} " + " ".join(valid_files)
    os.system(command)
    
def pre_merge(file_paths, merge_per_nfiles, max_workers):
    stage = 0
    while len(file_paths) > merge_per_nfiles - 1:
        merged_files = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for i in range(0, len(file_paths), merge_per_nfiles):
                to_be_merged = file_paths[i:i + merge_per_nfiles]
                if len(to_be_merged) > merge_per_nfiles - 1:
                    output_file = f"{inputdir}/temp_merged_s{stage}_{i//merge_per_nfiles}.root"
                    futures.append(executor.submit(merge_files, to_be_merged, output_file))
                    merged_files.append(output_file)
                else:
                    merged_files.extend(to_be_merged)
            concurrent.futures.wait(futures)
        file_paths = merged_files
        stage += 1
    return file_paths

if __name__ == '__main__':
    
    # please make sure the inputdir is the directory that doesn't contain the AnalysisResults.root
    inputdir = '/media/wuct/wulby/ALICE/AnRes/D0_flow/pass4/ML/Results/324130'
    inputName = 'AnalysisResults.root'
    
    # be carefult to set a max_workers that is too large
    
    # it is also avaliable to set merge_per_nfiles to a larger number with a smaller max_workers
    # this will be auto parallelize the execution by -j with defautly using the system maximum
    
    # it would be safer to set merge_per_nfiles to a smaller number, like 2 or 3,
    # in case can't merge the files at high stage
    merge_per_nfiles = 2
    max_workers = 12
    
    file_paths = merge_DF_singeFile(inputdir, inputName, False)
    
    file_paths = pre_merge(file_paths, merge_per_nfiles, max_workers)

    if len(file_paths) == 1:
        final_output = f"{inputdir}/{inputName}"
        os.rename(file_paths[0], final_output)
    else:
        merge_files(file_paths, f"{inputdir}/{inputName}")
    
    # file_paths = [path.replace(inputdir + '/', '') for path in pre_file_paths]
    
    # file_paths.sort(key=len)
        
    # path_filter(file_paths)

    pass