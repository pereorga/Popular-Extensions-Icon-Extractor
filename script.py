import sys, os, glob, shutil, time
from PIL import Image
from xml.dom.minidom import parse, parseString

def convert(file, extension, ICON_SIZE = 48):
    try:
        shutil.rmtree('tmp/png')
    except:
        pass
    try:
        os.mkdir('tmp/png')
    except:
        pass
    shutil.copy('tmp/ex/' + extension + '/' + file, 'tmp/ico/' + extension + '.ico')
    code = os.system('convert tmp\\ico\\' + extension + '.ico tmp\\png\\' + extension + '.png')
    if code != 0:
        return
    
    best      = ''
    max_size  = 0
    best_size = 0
    for f in glob.glob('tmp/png/*.png'):
        img = Image.open(f)
        width, height = img.size
        if width == ICON_SIZE and height == ICON_SIZE:
            if os.path.getsize(f) > best_size:
                best      = f
                best_size = os.path.getsize(f)
        elif best_size == 0 and os.path.getsize(f) > max_size:
            best     = f
            max_size = os.path.getsize(f)
    
    shutil.copy(best, 'icons/' + extension.lower() + '.png')
    
    # Compress it with pngout.exe.
    #os.system('pngout.exe icons/' + extension + '.png')




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
os.mkdir('tmp/ico')
os.mkdir('tmp/png')
os.mkdir('icons')


code = os.system("filetypesman.exe /sxml tmp/list.xml")
if code != 0:
    sys.exit(code)

dom = parse('tmp/list.xml')

for item in dom.getElementsByTagName('item'):
    for ext in item.getElementsByTagName('extension'):
        if ext.firstChild is not None and ext.firstChild.data and ext.firstChild.data[0] == '.':
            for icon in item.getElementsByTagName('default_icon'):
                if icon.firstChild is not None and len(icon.firstChild.data) > 5:
                    extension = ext.firstChild.data.replace('.', '')
                    os.mkdir('tmp/ex/' + extension)
                    if ',' in icon.firstChild.data:
                        ic_path, sep, ic_number = icon.firstChild.data.rpartition(',')
                        if len(ic_path) < 5:
                            ic_path   = icon.firstChild.data
                            ic_number = 0
                    else:
                        ic_path   = icon.firstChild.data
                        ic_number = 0
                    
                    ic_int = int(ic_number)
                    ic_path = ic_path.replace('\"', '')
                    code = os.system('iconsext.exe /save \"' + ic_path + '\" \"tmp\\ex\\' + extension + '\" -icons')
                    if code != 0:
                        continue
                    
                    i = 0
                    for file in os.listdir('tmp/ex/' + extension):
                        if ic_int < 0:
                            id = '_' + str(-ic_int) + '.'
                            if id in file:
                                convert(file, extension)
                                break
                        elif i == ic_int:
                            convert(file, extension)
                            break
                        i = i + 1
