import asyncio
import aiohttp
import requests
from asyncio_pool import AioPool
from multiprocessing.dummy import Pool as ThreadPool
import time
import os
import io
from PIL import Image
import zipfile


downloaded = 0
threads_count = 50


class DownloadingImage:
    def __init__(self, filename, url, img_id=0, size=None, session=None):
        self.filename = filename
        self.url = url
        self.session = session
        self.id = img_id
        self.size = size


async def async_get_url(image):
    if not os.path.exists(image.filename):
        try:
            async with image.session.get(image.url) as response:
                if response.status == 200:
                    with io.BytesIO() as img_buffer:
                        async for data in response.content.iter_any():
                            img_buffer.write(data)
                        i = Image.open(img_buffer)
                        if image.size:
                            i = i.resize(image.size, Image.LANCZOS)
                        i.save(image.filename, optimize=True)
                # else:
                #     print(f'download: {response.status}')
        except Exception as e:
            print(f'\nerror: {e}, {image.filename}')


async def async_download(images):
    pool = AioPool(size=threads_count)
    async with aiohttp.ClientSession() as session:
        for img in images:
            img.session = session
        await pool.map(async_get_url, images)


def thread_get_url(image):
    if not os.path.exists(image.filename):
        try:
            response = image.session.get(image.url)
            if response.ok:
                with io.BytesIO() as img_buffer:
                    img_buffer.write(response.content)
                    i = Image.open(img_buffer)
                    if image.size:
                        i = i.resize(image.size, Image.LANCZOS)
                    i.save(image.filename, optimize=True)
            else:
                print(f'download: {response.status}')
        except Exception as e:
            print(f'\nerror: {e}, {image.filename}')


def thread_download(images):
    session = requests.Session()
    for img in images:
        img.session = session
    pool = ThreadPool(threads_count)
    pool.map(thread_get_url, images)
    pool.close()
    pool.join()


def main(urls, folder='', size=(224, 224)):
    if not os.path.exists(folder):
        os.mkdir(folder)
    start_time = time.time()
    images = list()
    for img_id, img_url in enumerate(urls):
        file_name = img_url.split('?')[0].rsplit('/', 1)[1]
        images.append(DownloadingImage(url=img_url, filename=os.path.join(folder, file_name), img_id=img_id, size=size))

    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.run_until_complete(async_download(images))
    # loop.close()
    thread_download(images)
    print(f'download in {round(time.time() - start_time, 2)} seconds')


def zipdir(path):
    zip_file = os.path.join(os.path.dirname(path),
                            os.path.basename(path) + '.zip')
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(path, topdown=False):
            for file in files:
                full_name = os.path.join(root, file)
                zip_name = os.path.relpath(full_name, path)
                zipf.write(full_name, zip_name)
                os.remove(full_name)
            for dir_name in dirs:
                os.rmdir(os.path.join(root, dir_name))
    os.rmdir(path)
    return zip_file


if __name__ == '__main__':
    test_urls = ['https://sun9-27.userapi.com/c849128/v849128769/c260d/U4_NJTepM0Q.jpg',
                 'https://sun9-24.userapi.com/c849520/v849520073/134147/cvmgJOdpSCY.jpg',
                 'https://sun1-98.userapi.com/c845324/v845324360/1ad7e6/XRAoJdLYKXA.jpg',
                 'https://sun9-64.userapi.com/c626121/v626121740/5b489/HqWk1mJq6Sc.jpg']
    main(urls=test_urls, folder='G:\\tmp\\imgs')
    # zipdir('G:\\tmp\\imgs')

