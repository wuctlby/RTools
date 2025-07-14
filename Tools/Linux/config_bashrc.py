import os
import time
from warnings import Warning
work_dir = os.path.dirname(os.path.abspath(__file__))

# CONFIGURE____________________________________________________________________________________________________________
## O2 development environment configurations
def config_o2_path(bashrc_file):
    if os.environ.get('ALIBUILD_WORK_DIR'):
        print(f"ALIBUILD_WORK_DIR is set: {os.environ['ALIBUILD_WORK_DIR']}")
        if 'ALIBUILD_WORK_DIR' not in bashrc_file:
            Warning("ALIBUILD_WORK_DIR is not set in .bashrc, adding it now.")
            bashrc_file.write(f'export ALIBUILD_WORK_DIR={os.environ["ALIBUILD_WORK_DIR"]}\n')
    else:
        input_path = input("Please enter the path to the O2 work directory (default: $HOME/alice/sw): ")
        bashrc_file.write(f'export ALIBUILD_WORK_DIR={input_path}\n')
    return bashrc_file

def config_ae_alias(bashrc_file):
    if 'alias ae=' in bashrc_file:
        print("Alias 'ae' already exists in .bashrc.")
    else:
        bashrc_file.write('alias ae="alienv enter"\n')
    return bashrc_file

def config_funcO2(bashrc_file):
    if 'funcO2() {' in bashrc_file:
        print("Function 'funcO2' already exists in .bashrc.")
    else:
        bashrc_file.write('''
funcO2() {
    if [ -z "$1" ]; then
        echo "Entering O2 default version"
        alienv enter O2Physics/latest-master-o2
    else
        echo "Entering O2 version $1"
        alienv enter O2Physics/latest-"$1"-o2
    fi
}
export -f funcO2
alias o2=funcO2
''')
        bashrc_file.write('\n')
        print("Function 'funcO2' added to .bashrc.")
    return bashrc_file

def config_funcDPG(bashrc_file):
    if 'funcDPG() {' in bashrc_file:
        print("Function 'funcDPG' already exists in .bashrc.")
    else:
        bashrc_file.write('''
funcDPG() {
    if [ -z "$1" ]; then
        echo "Entering O2DPG default version"
        alienv enter O2/latest O2DPG/latest O2sim/latest
    else
        echo "Entering O2DPG version $1"
        alienv enter O2/latest O2DPG/latest-"$1"-o2 O2sim/latest
    fi
}
export -f funcDPG
alias dpg=funcDPG
''')
        bashrc_file.write('\n')
        print("Function 'funcDPG' added to .bashrc.")
    return bashrc_file

def config_funcO2list(bashrc_file):
    if 'funcO2list() {' in bashrc_file:
        print("Function 'funcO2list' already exists in .bashrc.")
    else:
        bashrc_file.write('''
funcO2list() {
    if [ -z "$1" ]; then
        echo "please provide the name of package to list"
        return 1
    else
        ls "$ALIBUILD_WORK_DIR"/BUILD | grep "$1" | sort -u
    fi
}
export -f funcO2list
alias o2list=funcO2list
''')
        bashrc_file.write('\n')
        print("Function 'funcO2list' added to .bashrc.")
    return bashrc_file

## RTool Configurations
def config_Obj_alias(bashrc_file):
    if 'alias Obj=' in bashrc_file:
        print("Alias 'Obj' already exists in .bashrc.")
    else:
        bashrc_file.write(f'alias Obj="{os.path.join(work_dir, 'OutputFileObj.py')}"\n')
        print("Alias 'Obj' added to .bashrc.")
    return bashrc_file

def config_runtag_func(bashrc_file):
    if 'runtag() {' in bashrc_file:
        print("Function 'runtag' already exists in .bashrc.")
    else:
        bashrc_file.write(f'''
funcRunTag() {{
    if [ $# -eq 0 ]; then
        echo "Usage: runtag <TAG> <COMMAND> [ARGS...]"
        return 1
    else
        {work_dir}/run_with_tag.sh "$@"
    fi
}}
export -f funcRunTag
alias runtag=funcRunTag
''')
        bashrc_file.write('\n')
        print("Function 'runtag' added to .bashrc.")
    return bashrc_file

def config_killtag_func(bashrc_file):
    if 'killtag() {' in bashrc_file:
        print("Function 'killtag' already exists in .bashrc.")
    else:
        bashrc_file.write(f'''
funcKillTag() {{
    if [ $# -eq 0 ]; then
        echo "Usage: killtag <TAG>"
        return 1
    else
        {work_dir}/killtag.sh "$@"
    fi
}}
export -f funcKillTag
alias killtag=funcKillTag
''')
        bashrc_file.write('\n')
        print("Function 'killtag' added to .bashrc.")
    return bashrc_file
        
        

if os.path.exists(os.path.expanduser('~/.bashrc')):
    bashrc_path = os.path.expanduser('~/.bashrc')
else:
    print("No .bashrc file found in the home directory.")
    exit(1)

os.command(f'cp ~/.bashrc ~/.bashrc_{time.strftime("%Y%m%d_%H%M%S")}.bak')

with open(bashrc_path, 'a') as bashrc_file:
    bashrc_file.write('\n# O2 development environment configuration\n')
    
    # Add configurations of O2-related part to .bashrc
    bashrc_file = config_o2_path(bashrc_file)
    bashrc_file = config_ae_alias(bashrc_file)
    bashrc_file = config_funcO2(bashrc_file)
    bashrc_file = config_funcDPG(bashrc_file)
    bashrc_file = config_funcO2list(bashrc_file)
    
    # Add configuration of RTool-related part to .bashrc
    bashrc_file = config_Obj_alias(bashrc_file)
    bashrc_file = config_runtag_func(bashrc_file)
    bashrc_file = config_killtag_func(bashrc_file)

    bashrc_file.write('\n# End of O2 development environment configuration\n')

    print(f"Configuration added to {bashrc_path}. \nPlease restart your terminal or run 'source {bashrc_path}' to apply the changes.")