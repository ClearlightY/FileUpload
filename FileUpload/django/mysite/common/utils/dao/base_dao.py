import os
import django
from django.db import connection


def execute_sql(sql: str, param: list):
    """
    执行查询sql, 返回列表
    :param param: 执行参数
    :param sql: 执行的sql语句
    :return: 结果列表
    """
    cursor = connection.cursor()
    res = cursor.execute(sql, param)
    return res
