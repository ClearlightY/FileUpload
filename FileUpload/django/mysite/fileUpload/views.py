import json
import os
import re
import time
import uuid

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from common.utils.util_date import time_stamp_to_date
from common.utils.util_store_path import file_store_path
from fileUpload.dao.dao import insert_upload_info, query_is_upload_by_md5
from fileUpload.service import service
from mysite import settings


@require_http_methods(["GET", "POST"])
@csrf_exempt
def textCheck(request):
    try:
        if request.method == 'POST':
            response = {}
            req = request.POST
            info = service.get_file_info(req)
            file_path = service.check_interface_by_file(info)
            response['msg'] = '文件正在校验中'
            response['code'] = 200
            response['uuid'] = str(info['uuid'])
            response['file_path'] = str(file_path)
    except Exception as e:
        print(e)
        response['msg'] = '服务器内部错误'
        response['code'] = 1
    return HttpResponse(json.dumps(response), content_type="application/json")


# 模拟的远程校验接口
@csrf_exempt
def check(request):
    # 模拟校验完成的文本
    response = {'uuid': 'cc5ff954-b453-11ea-b978-f875a46e2034'}
    time.sleep(2)  # 模拟文本校验消耗的时间
    return HttpResponse(json.dumps(response), content_type="application/json")


# 查询文件的校验状态
@csrf_exempt
def check_result(request):
    status = service.query_file_check_status(request)
    result = {}
    if status == 0:
        result['code'] = '500'
    else:
        result['code'] = '200'
    return HttpResponse(json.dumps(result), content_type="application/json")


# 合并文件
@csrf_exempt
def fileMerge(request):
    req = request.POST
    md5 = req.get('identifier')  # 获取上传文件的文件名
    date = req.get('timeStamp')  # 获取文件上传的时间
    origin_filename = req.get('filename')  # 原始文件名
    file_path = os.path.join(settings.MEDIA_ROOT) + '\\chunk'  # 文件分片的保存的位置
    upload_date = time_stamp_to_date(float(date))  # 格式化日期保存数据库中
    t_path = file_store_path(float(date))  # 合成文件的保存路径
    target_path = os.path.join(t_path, '%s.%s' % (md5, origin_filename))  # 合成文件的命名
    chunk = 1  # 文件分片从1开始
    if not os.path.exists(t_path):
        os.makedirs(t_path)
    with open(target_path, 'ab+') as target_file:
        while True:
            try:
                filename = os.path.join(file_path, '%d_%s' % (chunk, md5))
                source_file = open(filename, 'rb')  # 按照分片顺序打开每个分片
                target_file.write(source_file.read())
                source_file.close()
            except IOError:
                break
            chunk += 1
            os.remove(filename)  # 移除已合成文件的分片
    # 将上传的文件信息保存到数据库中, 为秒传 是否已经上传 做准备
    insert_upload_info(origin_filename, upload_date, t_path, md5, req.get('totalSize'))

    response = {'filePath': t_path, 'fileName': '%s.%s' % (md5, origin_filename), 'fileDate': req.get('timeStamp')}
    return HttpResponse(json.dumps(response), content_type="application/json")


@require_http_methods(["GET", "POST"])
@csrf_exempt
def globalUpload(request):
    response = {}
    info = {}
    time_stamp = time.time()
    info['uuid'] = uuid.uuid1()  # 上传文件生成UUID
    info['date'] = time_stamp_to_date(time_stamp)  # 时间戳转换为日期
    info['path'] = file_store_path(time_stamp) + '\\chunk'  # 存储路径
    info['chunk_path'] = os.path.join(settings.MEDIA_ROOT) + '\\chunk'
    try:
        if request.method == 'GET':
            print(request.GET)
            req_get = request.GET
            
             # 上传文件类型检测
            file_type = re.match(r'.*\.(txt|doc|docx|pdf)', req_get.filename)
            if not file_type:
                response['msg'] = '文件类型不匹配, 请重新上传'
                return HttpResponse(json.dumps(response))

            md5 = req_get['identifier']
            totalSize = req_get['totalSize']
            # 根据文件MD5和文件大小查询数据库文件是否已经上传, 若存在则返回标志完成秒传
            file_exist_result = query_is_upload_by_md5(md5, totalSize)
            if file_exist_result != 0:
                response['skipUpload'] = 'true'
                return HttpResponse(json.dumps(response), content_type="application/json")
            # 断点续传: 查询已经上传的分片, 将已经上传的分片以数组的形式返回给前台
            uploaded = []  # 指定文件夹中的文件名以列表形式存储
            for root, dirs, files in os.walk(info['chunk_path']):
                uploaded = files
            response['uploaded'] = []
            for file in uploaded:
                match = re.findall(r'(\d+)' + '_' + md5, file)
                if match:
                    response['uploaded'].append(match[0])
            # filename = os.path.join(info['path'], '%d_%s' % (int(req_get['chunkNumber']), req_get['identifier']))
            return HttpResponse(json.dumps(response), content_type="application/json")
        if request.method == 'POST':
            req = request.POST
            f = request.FILES.get('file')

            # 上传文件类型检测
            file_type = re.match(r'.*\.(txt|doc|docx|pdf)', f.name)
            if not file_type:
                response['msg'] = '文件类型不匹配, 请重新上传'
                return HttpResponse(json.dumps(response))
            
            # 存储目录不存在则创建
            if not os.path.exists(info['chunk_path']):
                os.makedirs(info['chunk_path'])
            # 打开特定的文件进行二进制的写操作
            file_name = str(req['chunkNumber']) + '_' + req['identifier']
            destination = open(
                os.path.join(info['chunk_path'], file_name), 'wb+')
            for chunk in f.chunks():  # 分块写入文件
                destination.write(chunk)
            destination.close()
            response['needMerge'] = 'true'
            response['timeStamp'] = time_stamp
    except Exception as e:
        print(e)
    return HttpResponse(json.dumps(response), content_type="application/json")


@csrf_exempt
def file_download(request):
    req = request.POST
    file_path = req.get("file_path")
    print(file_path)
    file = open(file_path, 'rb')
    print(file)
    response = HttpResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="hello.txt"'
    return response
