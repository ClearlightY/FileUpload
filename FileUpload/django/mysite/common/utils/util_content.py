import os
import re

import chardet
import docx
import win32com.client as wc
import pythoncom
import pdfplumber


def get_content_by_filetype(path, name, origin_path):
    print('----------------文档处理工具类--------------')
    print(path)
    print(name)
    txt_filename = '.'.join(name.split('.')[:-1]) + '.txt'
    print(txt_filename)
    file_type = name.split('.')[-1]
    print('文档类型: %s' % file_type)
    content = []
    if file_type == 'docx':
        file = docx.Document(path)
        for para in file.paragraphs:
            print(para.text)
            print(type(para.text))
            content.append(para.text)
    elif file_type == 'doc':
        output = os.subprocess.check_output(['antiword', path])
        content.extend(output.decode().split('\n'))
    elif file_type == 'pdf':
        pdf = pdfplumber.open(path)
        for page in pdf.pages:
            content.extend(page.extract_text().split('\n'))
        pdf.close()
    elif file_type == 'txt':
        with open(path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                content.append(line)
    else:
        content = ['文件格式不支持: {}'.format(file_type)]
        # with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        #     for line in f.readlines():
        #         print(line)
        #         content.append(line)
    return content
