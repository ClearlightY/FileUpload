import json
import os

import requests
from django.core.cache import cache
from django.http import HttpResponse


# 发送json数据
from common.utils import util_content


def get_interface_result(url, target_path, uuid, path, name, origin_path):
    global handle_Response
    response = {}
    try:
        # 请求远程接口, 并将文本内容发送过去
        content = util_content.get_content_by_filetype(target_path, name, origin_path)
        # with open(target_path, 'r', encoding='utf-8') as f:
        #     for line in f.readlines():
        #         content.append(line)
        print('---------------------------')
        print(content)
        req = requests.post(url=url, data={"lines": json.dumps(content)}, timeout=30)
        #req = requests.post(url=url, json=json.dumps(contents), timeout=30)
        # handle_content = req.text
        handle_content = req.json()
        print('---------校验接口返回的数据-------')
        print(handle_content)
        print(req)
        # 将返回的文本保存到文件中
        new_res = []
        for temp in handle_content:
            row_res = []
            for entry in temp:
                row_res.append(entry)
            new_res.append(row_res)
        res = new_res
        print('-----------处理后的返回数据-----------')
        print(res)
        destination = open(
            path, 'w', encoding="utf-8")
        destination.write(str(res))
        destination.close()
        print("----------校验已经完成-----------")
        cache.set(uuid, 1)
        response['msg'] = '文件校验成功'
        response['code'] = 200
        response['checkStatus'] = '校验完成'
    except Exception as e:
        print("发送请求错误:" + str(e))
    return HttpResponse(json.dumps(response), content_type="application/json")
