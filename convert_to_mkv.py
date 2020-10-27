import os


def search_files(directory='.', extensions=''):
    extensions = [x.lower().strip() for x in extensions.split(',')]
    for dirpath, dirnames, files in os.walk(directory):
        for name in files:
            for ext in extensions:
                if ext and name.lower().endswith(ext):
                    print(os.path.join(dirpath, name))
                elif not ext:
                    print(os.path.join(dirpath, name))

cmd = 'ffmpeg -i \'{FILENAME}\' -vcodec copy -acodec copy {OUTPUTFILE}'
search_files('/mnt/MEDIA/Media/Video/Movies', 'mp4,avi,m4v')