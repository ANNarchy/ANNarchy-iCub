
def spread_version(base_file, py_file, dox_file):
    # Set interface version
    with open(base_file, 'r') as file_object:
        version = file_object.readlines()[0].rstrip().lstrip()
    with open(py_file, 'w') as file_object:
        file_object.write("# automatically generated in setup.py\n")
        file_object.write(f"__version__ = \"{version}\"\n")
    with open(dox_file, 'w') as file_object:
        file_object.write("# automatically generated in setup.py\n")
        file_object.write(f"PROJECT_NUMBER = \"{version}\"\n")
    return version

fileversion = './ANN_iCub_Interface/version.txt'
fileversion_py = './ANN_iCub_Interface/_version.py'
fileversion_doxy = './doc/_version.dox'


if __name__ == "__main__":
    spread_version(fileversion, fileversion_py, fileversion_doxy)