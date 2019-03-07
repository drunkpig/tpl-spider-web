#!/usr/bin/env bash

__kill_process_by_name(){
	process_name=$1
	ps -ef | grep "${process_name}" | grep -v grep |awk '{print $2}' |xargs kill -9 > /dev/null 2>&1 || true
}

__kill_process_by_name 'tpl_web.wsgi'
__kill_process_by_name 'tpl-spider-core-main.py'
