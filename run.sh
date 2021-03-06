#!/usr/bin/env bash
# 程序可以部署在任何地方，但是可读的内容必须在 deploy_home下,这是权限的问题
# 需要在deploy_home的1) nginx.conf, 2)static file, 3)lua
PYTHON="/usr/bin/python3.7"
if [[ $UID -eq 0 ]]; then
    deploy_home="/var/template-spider.com/"
else
    deploy_home=$HOME/template-spider.com/
fi

mkdir -p ${deploy_home}

TEMPLATE_BASE_DIR="${deploy_home}/web-templates/"
mkdir -p ${TEMPLATE_BASE_DIR}

NGINX_INCLUDE_CONF_DIR=${deploy_home}/nginx

COLLECTED_STATIC_DIR='collected_static'
OPENRESTRY_DIR=/opt/openresty


NGIXN=${OPENRESTRY_DIR}/nginx/sbin/nginx
NGINX_CONF_SRC_DIR=nginx/
NGINX_CONF_FILE=tpl-spider-web.conf
NGINX_LUA_DIR=nginx/lua/

LUA_ROCKS=/opt/luarocks/bin/luarocks

NGINX_LUA_JIT_DIR=${OPENRESTRY_DIR}/luajit

BASEDIR=$(readlink -f $0 | xargs dirname)
DEPLOY_PARENT_DIR="${BASEDIR}/../"
PROJ_TPL_SPIDER_WEB=tpl-spider-web
PROJ_TPL_SPIDER_CORE=tpl-spider-core
SPIDER_WEB_PORT=9000
START_UP_PROJ_DIR="${DEPLOY_PARENT_DIR}/${PROJ_TPL_SPIDER_WEB}"
GIT_REPO=("git@github.com:jscrapy/tpl-spider-web.git ${PROJ_TPL_SPIDER_WEB} master"   \
          "git@github.com:jscrapy/tpl-spider-core.git ${PROJ_TPL_SPIDER_CORE} master")

DJANGO_STATIC_DIR="${DEPLOY_PARENT_DIR}/${PROJ_TPL_SPIDER_WEB}/${COLLECTED_STATIC_DIR}"
DJANGO_DEPLOY_STATIC_DIR="${deploy_home}/"
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
    ${PYTHON} -m pip install virtualenv
	venv_dir=${deploy_home}/venv
	if [ ! -d ${venv_dir} ];then
		${PYTHON} -m virtualenv -p ${PYTHON} ${venv_dir}
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
    rm -rf ${DJANGO_DEPLOY_STATIC_DIR}/${COLLECTED_STATIC_DIR}
    mkdir -p ${DJANGO_DEPLOY_STATIC_DIR}
    cp -rf ${DJANGO_STATIC_DIR}  ${DJANGO_DEPLOY_STATIC_DIR}
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
    src_nginx_conf_file=${DEPLOY_PARENT_DIR}/${PROJ_TPL_SPIDER_WEB}/${NGINX_CONF_SRC_DIR}/${NGINX_CONF_FILE}
    dst_nginx_conf_file="${NGINX_INCLUDE_CONF_DIR}/${NGINX_CONF_FILE}"
    if [ -f "${dst_nginx_conf_file}" ]; then
        rm ${dst_nginx_conf_file}
    fi

    if [ ! -d "${NGINX_INCLUDE_CONF_DIR}" ];then
        mkdir ${NGINX_INCLUDE_CONF_DIR}
    fi

    /bin/cp -rf ${src_nginx_conf_file}  ${dst_nginx_conf_file}
    sed -i "s:__STATIC_FILE_DIR__:${DJANGO_DEPLOY_STATIC_DIR}/${COLLECTED_STATIC_DIR}:g" ${dst_nginx_conf_file}
    sed -i "s:__PORT__:${SPIDER_WEB_PORT}:g"  ${dst_nginx_conf_file}
    sed -i "s:__TEMPLATE_BASE_DIR__:${TEMPLATE_BASE_DIR}:g"  ${dst_nginx_conf_file}

    cp ${DEPLOY_PARENT_DIR}/${PROJ_TPL_SPIDER_WEB}/${NGINX_LUA_DIR}/*.lua  ${NGINX_INCLUDE_CONF_DIR}/
    sed -i "s:__LUA_DIR__:${NGINX_INCLUDE_CONF_DIR}:g"  ${dst_nginx_conf_file}

    # /bin/cp -rf  ${DEPLOY_PARENT_DIR}/${PROJ_TPL_SPIDER_WEB}/web/templates/   ${DEPLOY_PARENT_DIR}/${PROJ_TPL_SPIDER_WEB}/collected_static
    sudo ${NGIXN}
}

_install_pgmoon(){
    sudo ${LUA_ROCKS} install --tree=${NGINX_LUA_JIT_DIR}   pgmoon
}

##############################################
_setup_repo
_set_up_py_venv
__kill_process_by_name 'tpl_web.wsgi'
__kill_process_by_name 'tpl-spider-core-main.py'
_install_pgmoon
_start_web  ${DEPLOY_PARENT_DIR}/${PROJ_TPL_SPIDER_WEB}
_start_core ${DEPLOY_PARENT_DIR}/${PROJ_TPL_SPIDER_CORE}
_config_and_reload_nginx
##############################################
