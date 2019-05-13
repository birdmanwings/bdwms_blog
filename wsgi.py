import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')  # .env文件所在的地方
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from bdwms_blog import create_app

app = create_app('production')  # 使用production生产环境，gunicorn wsgi容器将发现这个create_app函数
