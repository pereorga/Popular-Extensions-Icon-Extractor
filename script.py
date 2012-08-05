import os, glob, shutil, time
from PIL import Image
from xml.dom.minidom import parse, parseString

def convert(file, extension, ICON_SIZE = 48):
    shutil.rmtree('png')
    os.mkdir('png')
    shutil.copy('tmp/' + extension + '/' + file, 'ico/' + extension + '.ico')
    code = os.system('convert ico\\' + extension + '.ico png\\' + extension + '.png')
    if code != 0:
        return
    
    best      = ''
    max_size  = 0
    best_size = 0
    for f in glob.glob('png/*.png'):
        img = Image.open(f)
        width, height = img.size
        if width == ICON_SIZE and height == ICON_SIZE:
            if os.path.getsize(f) > best_size:
                best      = f
                best_size = os.path.getsize(f)
        elif best_size == 0 and os.path.getsize(f) > max_size:
            best     = f
            max_size = os.path.getsize(f)
    
    shutil.copy(best, 'output/' + extension.lower() + '.png')
    
    #if care about PNG compression uncomment the line below
    #os.system('pngout.exe output/' + extension + '.png')


os.mkdir('tmp')
os.mkdir('ico')
os.mkdir('png')
try:
    shutil.rmtree('output')
except:
    pass
os.mkdir('output')

code = os.system("filetypesman.exe /sxml list.xml")
if code != 0:
    sys.exit(code)

dom = parse('list.xml')

for item in dom.getElementsByTagName('item'):
    for ext in item.getElementsByTagName('extension'):
        if ext.firstChild is not None and ext.firstChild.data and ext.firstChild.data[0] == '.':
            for icon in item.getElementsByTagName('default_icon'):
                if icon.firstChild is not None and len(icon.firstChild.data) > 5:
                    extension = ext.firstChild.data.replace('.', '')
                    os.mkdir('tmp/' + extension)
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
                    code = os.system('iconsext.exe /save \"' + ic_path + '\" \"tmp\\' + extension + '\" -icons')
                    if code != 0:
                        sys.exit(code)
                    
                    i = 0
                    for file in os.listdir('tmp/' + extension):
                        if ic_int < 0:
                            id = '_' + str(-ic_int) + '.'
                            if id in file:
                                convert(file, extension)
                                break
                        elif i == ic_int:
                            convert(file, extension)
                            break
                        i = i + 1

shutil.rmtree('png')
shutil.rmtree('tmp')
shutil.rmtree('ico')
