import os
import time


# 上传文件保存的工具类
from django.conf import settings


def file_store_path(time_stamp):
    now = int(round(time_stamp * 1000))
    t = time.localtime(now / 1000)
    return os.path.join(settings.MEDIA_ROOT, str(t[0]), str(t[1]), str(t[2]))
