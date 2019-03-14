#!/usr/bin/env bash

TEMPLATE_BASE_DIR="/home/cxu/temp/tpl-spider/"
COLLECTED_STATIC_DIR='collected_static'

NGIXN=/usr/sbin/nginx
NGINX_CONF_FILE=tpl-spider-web.conf
NGINX_INCLUDE_CONF_DIR=/home/cxu/.nginx

BASEDIR=$(readlink -f $0 | xargs dirname)
DEPLOY_PARENT_DIR="${BASEDIR}/../"
PROJ_TPL_SPIDER_WEB=tpl-spider-web
PROJ_TPL_SPIDER_CORE=tpl-spider-core
SPIDER_WEB_PORT=9000
START_UP_PROJ_DIR="${DEPLOY_PARENT_DIR}/${PROJ_TPL_SPIDER_WEB}"
GIT_REPO=("git@github.com:jscrapy/tpl-spider-web.git ${PROJ_TPL_SPIDER_WEB} master"   \
          "git@github.com:jscrapy/tpl-spider-core.git ${PROJ_TPL_SPIDER_CORE} master")

DJANGO_STATIC_DIR="${DEPLOY_PARENT_DIR}/${PROJ_TPL_SPIDER_WEB}/${COLLECTED_STATIC_DIR}"
#=========================================================================
# 制作venv, 安装py依赖
# 杀原来进程
# 启动web: 同步数据库，静态文件同步
# 启动core：软链日志到web
# 配置nginx, 重启nginx
#=========================================================================
__kill_process_by_name(){
	process_name=$1
	ps -ef | grep "${process_name}" | grep -v grep |awk '{print $2}' |xargs kill -9 > /dev/null 2>&1 || true
}

__pip_install_deps(){
	requirements_txt=$1
	pip install -r ${requirements_txt}
}

_set_up_py_venv(){
	venv_dir=${START_UP_PROJ_DIR}/venv
	if [ ! -d ${venv_dir} ];then
		virtualenv -p /usr/bin/python3 ${venv_dir}
	fi
	source ${venv_dir}/bin/activate

	# install deps
	for ((i=0; i<${#GIT_REPO[@]}; i++));
    do
		x=${GIT_REPO[$i]}
		arr=(`cut -d' ' -f1-3 <<< $x`)
		project_dir=${DEPLOY_PARENT_DIR}/${arr[1]}
		requirements_txt=${project_dir}/requirements.txt
		if [ -f ${requirements_txt} ]; then
			__pip_install_deps ${requirements_txt}
		fi
    done
}

__sync_db(){
    pwdir=`pwd`
    proj_dir=$1
    cd ${proj_dir}
    python manage.py makemigrations
    python manage.py migrate
    cd ${pwdir}
}

__collect_static_files(){
    rm -rf ${DJANGO_STATIC_DIR}
    python manage.py collectstatic
}

_start_web(){
    pwdir=`pwd`
    proj_dir=$1
    cd $proj_dir
    __sync_db $proj_dir
    __collect_static_files
    nohup gunicorn -w5 -blocalhost:${SPIDER_WEB_PORT} tpl_web.wsgi > /dev/null 2>&1 &
    # nohup python manage.py runserver localhost:${SPIDER_WEB_PORT}> /dev/null 2>&1 &
    cd ${pwdir}
}

_start_core(){
    pwdir=`pwd`
    proj_dir=$1
    cd ${proj_dir}
    echo "start core ${proj_dir}"
    nohup python tpl-spider-core-main.py  ${TEMPLATE_BASE_DIR}> /dev/null  &
    rm ${DEPLOY_PARENT_DIR}/${PROJ_TPL_SPIDER_WEB}/tpl-spider-core.log || true
    ln -s ${proj_dir}/logs/tpl-spider-core.log  ${DEPLOY_PARENT_DIR}/${PROJ_TPL_SPIDER_WEB}/tpl-spider-core.log
    cd ${pwdir}
}

__clone_or_update_branch(){
    # 进入到父目录，然后更新或者clone
    pwd_dir=`pwd`
    base_abs_dir=${DEPLOY_PARENT_DIR}  # 绝对路径
	git_url=$1
    project_dir=$2  # 工程名字/目录
    branch=$3

    cd ${base_abs_dir}
    if [[ ! -d "${base_abs_dir}/${project_dir}" ]]; then
        git clone -b ${branch} ${git_url}
        git branch ${branch}
        git pull origin ${branch}
    else
        cd ${project_dir}
        git checkout ${branch}
        git pull origin ${branch}
    fi
    cd ${pwd_dir}
}

_setup_repo(){
# 更新/下载全部仓库
	for ((i=0; i<${#GIT_REPO[@]}; i++));
	do
		x=${GIT_REPO[$i]}
		arr=(`cut -d' ' -f1-3 <<< $x`)
		__clone_or_update_branch ${arr[0]} ${arr[1]} ${arr[2]}
	done
}

_config_and_reload_nginx(){
	
    sudo ${NGIXN} -s  stop
    rm ${NGINX_INCLUDE_CONF_DIR}/${NGINX_CONF_FILE} || true
    # ln -s ${DEPLOY_PARENT_DIR}/${PROJ_TPL_SPIDER_WEB}/${NGINX_CONF_FILE}  ${NGINX_INCLUDE_CONF_DIR}/${NGINX_CONF_FILE}
    if [ ! -d "${NGINX_INCLUDE_CONF_DIR}" ];then
        mkdir ${NGINX_INCLUDE_CONF_DIR}
    fi
    /bin/cp -rf ${DEPLOY_PARENT_DIR}/${PROJ_TPL_SPIDER_WEB}/${NGINX_CONF_FILE}  ${NGINX_INCLUDE_CONF_DIR}/${NGINX_CONF_FILE}
    sed -i "s:__STATIC_FILE_DIR__:${DJANGO_STATIC_DIR}:g"  ${NGINX_INCLUDE_CONF_DIR}/${NGINX_CONF_FILE}
    sed -i "s:__PORT__:${SPIDER_WEB_PORT}:g"  ${NGINX_INCLUDE_CONF_DIR}/${NGINX_CONF_FILE}
    sed -i "s:__TEMPLATE_BASE_DIR__:${TEMPLATE_BASE_DIR}:g"  ${NGINX_INCLUDE_CONF_DIR}/${NGINX_CONF_FILE}
    sudo ${NGIXN}
}

##############################################
_setup_repo
_set_up_py_venv
__kill_process_by_name 'tpl_web.wsgi'
__kill_process_by_name 'tpl-spider-core-main.py'

_start_web  ${DEPLOY_PARENT_DIR}/${PROJ_TPL_SPIDER_WEB}
_start_core ${DEPLOY_PARENT_DIR}/${PROJ_TPL_SPIDER_CORE}
_config_and_reload_nginx
##############################################
