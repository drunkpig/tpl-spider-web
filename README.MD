
## 架构
![](docs/image/arch.jpg)

## 部署
1. django静态文件
执行 `python manage.py collectstatic`之后静态文件被放在 `tpl-spider-web`工程目录下的
 `collected_static/`。
这个目录在`run.sh `里使用sed对nginx的配置 `tpl-spider-web.conf`进行了配置。
2. 下载的模版位置
位置会存储下载过程中的临时目录和压缩后的zip文件。这个路径被配置在`run.sh`里。在启动的时候
传送给 `tpl-spider-core`。

3. nginx配置
    - 首先需要root配置下nginx的自带配置文件`nginx.conf`， include 进去`$HOME/.nginx/*.conf`
    如果没有这个目录需要自己去建好
    - 第二步，把`tpl-spider-web`工程下的`tpl-spider-web.conf`文件软链接到`$HOME/.nginx/tpl-spider-web.conf`
    

## TODO
- 精品模版
- 截图
- [logo](https://image.baidu.com/search/index?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq=1543832155706_R&pv=&ic=0&nc=1&z=0&hd=0&latest=0&copyright=0&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&word=%E6%B0%B4%E9%BB%BE+%E9%AB%98%E6%B8%85
)

## 模版网站地址

https://www.wix.com/website/templates

http://wang.market/template.jsp

