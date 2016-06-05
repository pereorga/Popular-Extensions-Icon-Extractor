import sys
import os
import shutil
from xml.dom.minidom import parse

# TODO:
#   Use paths separators
#   use temporary directory
#   windows only
#   use main function
#   comment code
#   download tools if not available
#   better exceptions


def choose_icon(extension, icon_number):
    if os.listdir('tmp/ex/' + extension):
        if icon_number >= 0:
            icon_number += 1
        elif icon_number < 0:
            icon_number = -icon_number

        aux = None
        found = False
        i = 0
        for f in os.listdir('tmp/ex/' + extension):
            file_name = 'tmp/ex/' + extension + '/' + f
            if '_' + str(icon_number) + '.' in f:
                found = True
                break
            elif i == icon_number - 1:
                aux = file_name
            i += 1

        if not found and aux:
            file_name = aux

        shutil.copy(file_name, 'icons/' + extension.lower() + '.ico')


def icon_extract(icon, extension):
    return os.system('iconsext.exe /save \"' + icon + '\" \"tmp\\ex\\' + extension + '\" -icons')

try:
    shutil.rmtree('tmp')
except:
    pass
try:
    shutil.rmtree('icons')
except:
    pass
os.mkdir('tmp')
os.mkdir('tmp/ex')
os.mkdir('icons')


code = os.system("filetypesman.exe /sxml tmp/list.xml")
if code != 0:
    sys.exit(code)

dom = parse('tmp/list.xml')
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
                        shutil.copy(icon_path, 'icons/' + extension.lower() + '.ico')
                        break

                    # Try to extract the icon
                    os.mkdir('tmp/ex/' + extension)
                    icon_extract(icon_path, extension)
                    if icon_path2:
                        icon_extract(icon_path2, extension)

                    # If the directory is still empty and the path of the resource was relative
                    if not os.listdir('tmp/ex/' + extension) and not os.path.isabs(icon_path):
                        # Try again with absolute paths
                        for path_prefix in lookup_paths:
                            icon_extract(path_prefix + '\\' + icon_path, extension)
                            if os.listdir('tmp/ex/' + extension):
                                break

                    choose_icon(extension, resource_number)
