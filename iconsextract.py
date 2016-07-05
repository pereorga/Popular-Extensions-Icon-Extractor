import sys
import os
import platform
import shutil
import tempfile
import zipfile
from xml.dom.minidom import parse

try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve

# TODO:
#   Add output directory option
#   better error and exception handling


def choose_icon(extension, icon_number):
    """Choose an icon using its resource number."""
    extension_dir = os.path.join(get_temp_directory(), extension)
    if os.listdir(extension_dir):
        if icon_number >= 0:
            icon_number += 1
        elif icon_number < 0:
            icon_number = -icon_number

        aux = None
        found = False
        i = 0
        for f in os.listdir(extension_dir):
            file_name = os.path.join(extension_dir, f)
            if '_' + str(icon_number) + '.' in f:
                found = True
                break
            elif i == icon_number - 1:
                aux = file_name
            i += 1

        if not found and aux:
            file_name = aux

        shutil.copy(file_name, os.path.join('icons', extension.lower() + '.ico'))


def icon_extract(resource, extension):
    """Extract icons from resource"""
    path = os.path.dirname(os.path.abspath(__file__))
    extension_dir = os.path.join(get_temp_directory(), extension)
    return os.system(os.path.join(path, 'iconsext.exe') + ' /save \"' + resource + '\" \"' + extension_dir + '\" -icons')


def get_temp_directory():
    """Get temporary directory name"""
    return os.path.join(tempfile.gettempdir(), 'iconsextractor')


def create_temp_directory():
    """Create a temporary directory and return its path. Delete any existing directories"""
    tmp_dir = get_temp_directory()
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)
    return tmp_dir


def download_filetypesman():
    path = os.path.dirname(os.path.abspath(__file__))
    urlretrieve('http://www.nirsoft.net/utils/filetypesman.zip', os.path.join(path, 'filetypesman.zip'))
    with zipfile.ZipFile(os.path.join(path, 'filetypesman.zip')) as zip_file:
        for name in zip_file.namelist():
            if name.lower() == 'filetypesman.exe':
                zip_file.extract(name, path)
                break
    os.remove(os.path.join(path, 'filetypesman.zip'))


def download_iconsext():
    path = os.path.dirname(os.path.abspath(__file__))
    urlretrieve('http://www.nirsoft.net/utils/iconsext.zip', os.path.join(path, 'iconsext.zip'))
    with zipfile.ZipFile(os.path.join(path, 'iconsext.zip')) as zip_file:
        for name in zip_file.namelist():
            if name.lower() == 'iconsext.exe':
                zip_file.extract(name, path)
                break
    os.remove(os.path.join(path, 'iconsext.zip'))


def main():
    if platform.system().lower() != 'windows':
        sys.stderr.write('Windows is required.')
        exit(1)

    if os.path.exists('icons') and os.listdir('icons'):
        sys.stderr.write("'icons' directory exists and is not empty. Please remove it first.\n")
        exit(1)

    # Create icons directory
    if not os.path.exists('icons'):
        os.mkdir('icons')

    script_path = os.path.dirname(os.path.abspath(__file__))

    if not os.path.exists(os.path.join(script_path, 'FileTypesMan.exe')):
        print('FileTypesMan.exe not found. Trying to download it.')
        download_filetypesman()
    if not os.path.exists(os.path.join(script_path, 'iconsext.exe')):
        print('iconsext.exe not found. Trying to download it.')
        download_iconsext()

    tmp_dir = create_temp_directory()
    xml_file = os.path.join(tmp_dir, 'list.xml')
    code = os.system(os.path.join(script_path, 'filetypesman.exe') + " /sxml " + xml_file)
    if code != 0:
        sys.exit(code)

    dom = parse(xml_file)
    lookup_paths = os.environ.get('PATH').split(";")

    for item in dom.getElementsByTagName('item'):
        for ext in item.getElementsByTagName('extension'):
            if ext.firstChild is not None and ext.firstChild.data and ext.firstChild.data[0] == '.':
                extension = ext.firstChild.data.replace('.', '')
                for icon_element in item.getElementsByTagName('default_icon'):
                    # Example cases:
                    # 1)
                    # 2) %1
                    # 3) "C:\windows\System32\zipfldr.dll"
                    # 4) C:\Python27\DLLs\py.ico
                    # 5) C:\windows\Installer\{AC76BA86-7AD7-FFFF-7B44-AB0000000001}\PDFFile_8.ico,0
                    # 6) C:\Windows\System32\icardres.dll,-4112
                    # 7) C:\PROGRA~1\COMMON~1\MICROS~1\OFFICE14\MSORES.DLL,-560
                    # 8) imageres.dll,-67
                    # 9) cryptui.dll,-3425
                    # 10) %SystemRoot%\System32\shell32.dll,2
                    # 11) %SystemRoot%\System32\GfxUIEx.exe, 2
                    # 12) %SystemRoot%\system32\wmploc.dll,-730
                    # 13) "C:\Program Files (x86)\qBittorrent\qbittorrent.exe",1
                    # 14) &quot;%ProgramFiles%\Windows Journal\Journal.exe&quot;,2

                    # Skip cases 1 and 2
                    if icon_element.firstChild is not None and len(icon_element.firstChild.data) > 2:

                        # Remove quotes
                        icon_path = icon_element.firstChild.data.replace('\"', '')
                        icon_path2 = ''
                        resource_number = 0

                        # Handle cases with an icon number
                        if ',' in icon_path:
                            icon_path, sep, resource_number = icon_path.rpartition(',')
                            resource_number = int(resource_number)

                        # Evaluate environment variables and workaround specific case for %ProgramFiles%
                        if '%ProgramFiles%' in icon_path:
                            icon_path2 = os.path.expandvars(icon_path.replace('%ProgramFiles%', '%ProgramW6432%'))
                        icon_path = os.path.expandvars(icon_path)

                        # Handle cases 4 and 5
                        if icon_path.lower().endswith('.ico'):
                            shutil.copy(icon_path, os.path.join('icons', extension.lower() + '.ico'))
                            break

                        # Try to extract the icon
                        extension_dir = os.path.join(tmp_dir, extension)
                        os.mkdir(extension_dir)
                        icon_extract(icon_path, extension)
                        if icon_path2:
                            icon_extract(icon_path2, extension)

                        # If the directory is still empty and the path of the resource was relative
                        if not os.listdir(extension_dir) and not os.path.isabs(icon_path):
                            # Try again with absolute paths
                            for path_prefix in lookup_paths:
                                icon_extract(os.path.join(path_prefix, icon_path), extension)
                                if os.listdir(extension_dir):
                                    break

                        choose_icon(extension, resource_number)

    # Delete temporary directory
    shutil.rmtree(get_temp_directory())

if __name__ == '__main__':
    main()
