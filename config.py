import configparser
import getopt
import sys


class Config:
    cfg_path = 'D:/110/app/config.cfg'
    type = 'product'
    opts, args = getopt.getopt(sys.argv[1:], "d:s:c:i:t:", ["rootdir=", "serial=", "code=", "ip=", "type="]);
    for opt, arg in opts:
        for opt, arg in opts:
            if opt in ("-d", "--rootdir"):
                cfg_path = arg
            elif opt in ("-t", "--type"):
                type = arg
    config_parser = configparser.ConfigParser()  # 初始化对象
    config_parser.read(cfg_path)  # 读取config.cfg配置文件
    config = config_parser['%s' % type]

    db_config = {
        "host": str(config['db_host']),
        "port": int(config['db_port']),
        "user": str(config['db_user']),
        "password": str(config['db_password']),
        "db": str(config['db_name']),
        "charset": str(config['db_charset'])
    }

    root_dir = config['root_dir']
    clue_dir = config['clue_dir']
    scenario_dir = config['scenario_dir']
    task_url = config['task_url']
    rtmp_url = config['rtmp_url']
    m3u8_url = config['m3u8_url']
    minio_endpoint = config['minio_endpoint']
    minio_access_key = config['minio_access_key']
    minio_secret_key = config['minio_secret_key']
    minio_secure = config['minio_secure']
    minio_bucket = config['minio_bucket']
    default_collect_time = config['default_collect_time']