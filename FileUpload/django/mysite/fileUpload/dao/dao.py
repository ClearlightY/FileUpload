from common.utils.dao.base_dao import execute_sql


# 添加文件上传信息: 存入md5实现秒传
def insert_upload_info(name, upload_date, path, md5, size):
    sql = """
        INSERT INTO fileupload_upload_info 
            (name, upload_date, path, md5, size) 
        values 
            (%s, %s, %s, %s, %s) 
    """
    return execute_sql(sql, [name, upload_date, path, md5, size])


# 添加文件校验的信息
def insert_check_info(uuid, name, check_date, path):
    sql = """
        INSERT INTO fileupload_check_info
            (uuid, name, check_date, path)
        VALUES
            (%s, %s, %s, %s)
    """
    return execute_sql(sql, [uuid, name, check_date, path])


# 根据上传文件的md5查询是否已经上传
def query_is_upload_by_md5(md5, size):
    sql = """
        SELECT 
            size 
        FROM 
            fileupload_upload_info 
        where 
            md5 = %s and size = %s 
    """
    return execute_sql(sql, [md5, size])
