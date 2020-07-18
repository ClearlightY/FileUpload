import time


# 根据文件上传的时间戳, 格式化为 2020-6-30 12:00:00
def time_stamp_to_date(time_stamp):
    now = int(round(time_stamp * 1000))
    t = time.localtime(now / 1000)
    return time.strftime('%Y-%m-%d %H:%M:%S', t)


if __name__ == '__main__':
    stamp = time.time()
    print(time_stamp_to_date(stamp))
