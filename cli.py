import subprocess

# Script uses ip utility. Commands using for interacting with ip goes next
_get_custom_tables = '''ip route show table all | grep "table" | sed 's/.*\(table.*\)/\1/g' | awk '{print $2}' | sort | uniq | grep -e "[0-9]"'''
_get_rules = 'ip rule'

def execute(cmd, raw=False):
    shell = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = shell.communicate()[0]
    # make str from bytes
    string = output.decode()[:-2]
    if len(string) == 0:
        return None
    if raw == False:
        output = string.split('\n')
        return(output)
    elif raw == True:
        return(string)

print(execute(_get_custom_tables))