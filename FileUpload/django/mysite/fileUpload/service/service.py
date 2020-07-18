import os
import time
import uuid

from django.core.cache import cache

from common.utils.threading.ResultThread import ResultThread
from common.utils.urls_net import get_interface_result
from common.utils.util_date import time_stamp_to_date
from fileUpload.dao import dao


def get_file_info(req):
    # 将上传的文件逐行读取保存到list中
    info = {'date': '', 'name': '', 'uuid': uuid.uuid1(), 'path': ''}

    # 生成当前文件生成UUID
    # 文本校验的时间
    time_stamp = time.time()
    info['date'] = time_stamp_to_date(time_stamp)
    # 文件名称
    info['name'] = req['fname']
    # 存储路径
    info['path'] = req['fpath']
    # 将文本信息保存到数据库
    dao.insert_check_info(info['uuid'], info['name'], info['date'], info['path'])
    # 将uuid和文件状态保存到redis
    cache.set(info['uuid'], 0)
    return info


def check_interface_by_file(info):
    target_path = '%s\\%s' % (info['path'], info['name'])
    # 将文本发送到指定接口进行校验, 这里使用多线程
    # tmp_url = 'http://127.0.0.1:8000/fileUpload/check'
    tmp_url = 'http://202.85.216.20:20027/punc/'
    thread_list = []
    file_path = os.path.join(info['path'], str(info['uuid']) + ".res.txt")
    thread = ResultThread(target=get_interface_result, name=info['uuid'],
                          args=(tmp_url, target_path, info['uuid'], file_path, info['name'], info['path']))
    thread_list.append(thread)
    for thread in thread_list:
        thread.start()
    return file_path


def query_file_check_status(request):
    file_uuid = request.POST.get('file_uuid')
    status = cache.get(file_uuid)
    return status
