# 从parameter中获取数据的工具
import datetime
import json
import traceback

# 获取前端传来的数据
import urllib

import requests


# 发送json数据
def get_interface_result(url, paramname, lines, exception_flag):
    t0 = datetime.datetime.now()
    try:
        if paramname is None or paramname == '':
            req = requests.post(url=url, json=lines, timeout=30)
        else:
            req = requests.post(url=url, data={paramname: json.dumps(lines)}, timeout=30)
        res = req.json()
        try:
            new_res = []
            for temp in res:
                row_res = []
                for entry in temp:
                    if len(entry) < 4:
                        entry.append('')
                    else:
                        entry = entry[:4]
                    row_res.append(entry)
                new_res.append(row_res)
            res = new_res
        except Exception as ex:
            print(ex)
        t1 = datetime.datetime.now()
        print('接口查询:类别：{},\turl为：{},\t耗时：{}'.format(exception_flag, url, str(t1 - t0)))
    except Exception as ex:
        print('接口查询:当前url为：{},\t参数名：{},\t标注：{},错误:{}'.format(url, paramname, exception_flag, traceback.format_exc()))
        res = [[] for _ in range(len(lines))]
    return res


if __name__ == '__main__':
    # 搭配纠错
    lines = ['我再程度的街头']
    url = 'http://202.85.216.20:20027/punc/'
    res = get_interface_result(url, 'lines', lines, 'token')
    print(res)
