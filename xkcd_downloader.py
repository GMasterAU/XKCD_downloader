# 2022 Dr T. Gabriel Enge, Canberra, Australia

import requests, wget, re, os, sys, time

# glob_vars
option = 2
log_file = 1
large_file = 2

def main():
    # SETUP
    datetime = time.strftime("%Y%m%d-%H%M%S")
    #########################################################
    # Get user input
    global option, large_file, log_file, folders
    option = int(user_input("Record original file names [1], or rename files sequentially based on comic number [2]? Provide number option: "))
    log_file = user_input("Record error log on [1] or off [2] (default = on): ")

    large_file = user_input("Record large [2] version of files in addition to regular size [1]: ")
    if large_file == 2:
        folders = {"base_folder": "./XKCD_files", "folder_s": "./XKCD_files/regular", "folder_l": "./XKCD_files/large"}
    else:
        folders = {"base_folder": "./XKCD_files", "folder_s": "./XKCD_files/regular"}
    #########################################################
    # Folder operations
    for i in folders.values():
        make_folder(i)
    #########################################################
    # Operations on front page
    web_url = 'https://xkcd.com/'

    # Get website text
    base_info = requests.get(web_url).text

    # Separate out important information (relevant urls and count)
    all_urls = str(re.findall("content=\"h.+>", base_info))
    global count_total
    count_total = int(str(' '.join(all_urls.split('/')[3:4])))
    #########################################################
    # Progressbar
    # for i in progressbar(range(15), "Computing: ", 40):
    # Image page operations
    # for i in range(count_total):
    for i in progressbar(range(count_total), "waiting to complete: ", 60):
        # Clear log for iteration
        global errors
        errors = []

        # Build image URL
        image_page_url = "https://xkcd.com/" + (str(count_total - i))

        # Get website text
        image_page_info = requests.get(image_page_url).text

        # Extract relevant URL
        image_url_base = str(re.findall("Image.+URL.+", image_page_info))
        # Regular size
        image_url = ' '.join(image_url_base.split('">')[1:])[:-6]
        download_procedure(image_url, i, 'regular', None)

        # Large size
        if large_file == 2:
            sizes = {1:'_large', 2:'_huge', 3:'_2x'}
            for j in sizes.values():
                image_url_large = image_url[:-4] + j + image_url[-4:]
                download_procedure(image_url_large, i, 'large', j)

        if log_file == 1:
            with open('./log' + '_' + datetime + '.txt', 'a') as log:
                log.write('\n'.join(str(i) for i in errors))
                log.write('\n')
    #########################################################

def make_folder(f):
    if not os.path.exists(f):
        os.makedirs(f)


def user_input(s):
    while True:
        try:
            option = int(input(s))
        except ValueError:
            print("Please input a numeric value")
            print("")
        else:
            if option == 1 or option ==2:
                return option
            else:
                print("Please input a valid numeric value [1] or [2]")
                print("")


def download_procedure(url, i, size ,j):
    try:
        check = requests.get(url)
    except requests.exceptions.RequestException as exc_1:
        if not size == 'regular':
            exc = 'requests.get.error: ' + str(exc_1)
            error_catch(count_total, i, exc, None)
        return

    if check.status_code == requests.codes.ok:
        if url:
            # Extract image name
            image_name = ' '.join(url.split('/')[4:])
            image_extension = ' '.join(image_name.split('.')[1:])

            if option == 2:
                # OPTION 2: download with modified file names
                # Build new file name, then check if image exists, else write image
                if not size == 'regular':
                    new_image_name = folders['folder_l'] + '/' + 'XKCD_' + str(count_total - i) + '.' + image_extension
                else:
                    new_image_name = folders['folder_s'] + '/' + 'XKCD_' + str(count_total - i) + '.' + image_extension
                if not os.path.exists(new_image_name):
                    download(url, i, new_image_name)

            else:
                # OPTION 1: download with original file name
                # Check if image exists, else write image
                if not size == 'regular':
                    if not os.path.exists(folders['folder_l'] + '/' + image_name):
                        download(url, i, folders['folder_l'])
                else:
                    if not os.path.exists(folders['folder_s'] + '/' + image_name):
                        download(url, i, folders['folder_s'])
    else:
        error_catch(count_total, i, check.status_code, j)


def error_catch(x, i, s, j):
    if j == None:
        errors.append('file number: ' + (str(x - i)) + '_' + '; error, status_code: ' + str(s))
    else:
        errors.append('file number: ' + (str(x - i)) + '_' + j + '; error, status_code: ' + str(s))
    # print(errors)


def download(url, i, x):
    try:
        # Suppress wget output to not interfere with the progress bar
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.devnull, "w")
        wget.download(url, out = x)
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    except Exception as exc:
        exc = 'wget.error: ' + str(exc)
        error_catch(count_total, i, exc, None)


# Modified from https://stackoverflow.com/questions/3160699/python-progress-bar
# First version taking total count and counting up from that
# def progressbar(length, text = "", size = 10, out=sys.stderr):
#     count = len(length)

#     def show(j):
#         x = int(size * j / count)
#         print("{}[{}{}] {}/{}".format(text, "#" * x, "." * (size-x), j, count),
#                 end='\r', file=out, flush=True)

#     show(0)
#     for i, item in enumerate(length):
#         yield item
#         show(i + 1)
#     print("\n", flush=True, file=out)

# Second version calculates the fraction out of 100%
def progressbar(length, text = "", size = 10, out=sys.stderr):
    count = len(length)

    def show(j):
        x = int(size * j / count)
        print("{}[{}{}] {}/{}".format(text, "#" * x, "." * (size - x), j, '100%'),
                end='\r', file=out, flush=True)

    show(0)
    for i, item in enumerate(length):
        yield item
        show(round((i + 1) * size / count, 2))
    print("\n", flush=True, file=out)

if __name__ == "__main__":
    main()