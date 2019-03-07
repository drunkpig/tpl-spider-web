#!/usr/bin/env bash
BASEDIR=$(readlink -f $0 | xargs dirname)

cd $BASEDIR/
git pull origin master  # 更新代码
ps -ef | grep 'main.py' | grep -v grep |awk '{print $2}' |xargs kill -9 > /dev/null 2>&1 || true  # 关闭后台python web进程
source venv/bin/activate
pip install -r requirements.txt
nohup python -m spider/main.py > /dev/null 2>&1 &
echo "`date` tpl-spider started!"




BASEDIR=$(readlink -f $0 | xargs dirname)
COLLECTED_STATIC_DIR='collected_static'
NGINX_STATIC_DIR='/var/www/collected_static'

cd $BASEDIR
git pull origin master  # 更新代码
ps -ef | grep gunicorn | grep -v grep |awk '{print $2}' |xargs kill -9 > /dev/null 2>&1 || true  # 关闭后台python web进程
source venv/bin/activate
pip install -r requirements.txt
rm -rf ${NGINX_STATIC_DIR}
mkdir ${COLLECTED_STATIC_DIR}
python manage.py collectstatic
/etc/init.d/nginx stop || true
rm /etc/nginx/sites-available/default
ln -s ${BASEDIR}/default.nginx /etc/nginx/sites-available/default
ln -s ${BASEDIR}/${COLLECTED_STATIC_DIR} ${NGINX_STATIC_DIR}
/etc/init.d/nginx start
nohup gunicorn -w5 -blocalhost:8080 tpl_web.wsgi > /dev/null 2>&1 &
echo "`date` tpl-web web started!"
