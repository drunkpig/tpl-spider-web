#!/usr/bin/env bash
BASEDIR=$(readlink -f $0 | xargs dirname)

cd $BASEDIR/
git pull origin master  # 更新代码
ps -ef | grep 'main.py' | grep -v grep |awk '{print $2}' |xargs kill -9 > /dev/null 2>&1 || true  # 关闭后台python web进程
source venv/bin/activate
pip install -r requirements.txt
nohup python -m spider.main > /dev/null 2>&1 &
echo "`date` tpl-spider started!"
