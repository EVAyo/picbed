# picbed

基于Flask的Web自建图床，支持存储到本地、又拍云、七牛云、阿里云OSS、腾讯云COS、GitHub、Gitee(码云)等。

[![Build Status](https://travis-ci.org/staugur/picbed.svg?branch=master)](https://travis-ci.org/staugur/picbed)
[![codecov](https://codecov.io/gh/staugur/picbed/branch/master/graph/badge.svg)](https://codecov.io/gh/staugur/picbed)
![Last Release](https://img.shields.io/github/release/staugur/picbed.svg?style=flat-square)

## 手动部署

1. 要求： Python2.7、Python3.5+（或PyPy）和Redis

2. 下载： `git clone https://github.com/staugur/picbed && cd picbed`

3. 依赖： `pip install -r requirements/all.txt` # 也可以参考详情文档如何按需安装依赖包

4. 配置：

    src目录下的config.py即配置文件，它会加载中 `.cfg` 文件读取配置信息，
    无法找到时加载环境变量，最后使用默认值，**必需设置picbed_redis_url**

    所以可以把配置项写到 `.bash_profile` 或 `.bashrc` 此类文件中在登录时加载，
    也可以写入到 /path/to/picbed/src/ 下的 **.cfg** 文件里，这是推荐的方式，
    它不会被提交到仓库，格式是k=v，每行一条，注意：v是所见即所得！

    比如：`picbed_redis_url=redis://@localhost`

5. 启动：

    ```bash
    $ cd /path/to/picbed/src/

    // 首先创建一个管理员账号 -h/--help显示帮助
    $ flask sa create -u USER -p PASSWORD --isAdmin

    // 如果更新了版本，注意执行命令迁移数据，详见文档：部署安装-升级部分
    // flask sa upgrade --help

    // 开发环境启动
    $ make dev

    // 正式环境，若需前台启动，将start换成run即可；其他支持stop、reload、restart、status
    $ make start 或 sh online_gunicorn.sh start
    ```

6. Nginx:

    ```nginx
    // 默认配置下，picbed启动监听127.0.0.1:9514，nginx配置示例：
    server {
        listen 80;
        server_name your-picbed.domain.name;
        charset utf-8;
        client_max_body_size 20M;
        location ~ ^\/static\/.*$ {
            root /path/to/picbed/src/;
        }
        location / {
           proxy_pass http://127.0.0.1:9514;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
    ```

## 使用Docker部署

- 手动构建镜像

  源码中已经编写了Dockerfile文件，可以藉此构建picbed镜像。

  ```bash
  $ git clone https://github.com/staugur/picbed && cd picbed
  $ docker build -t staugur/picbed .
  ```

- 使用已上传镜像

  已设置CI实现提交代码自动构建并推送到官方Docker仓库中，直接pull即可：

  ```bash
  $ docker pull staugur/picbed  # 或者加上tag拉取某稳定版本的镜像(1.4.0开始)
  ```

- 启动镜像

  ```bash
  $ docker run -tdi --name picbed --restart=always --net=host \
      -e picbed_redis_url="Your Redis URL" \
      -e 其他配置=值 \
      staugur/picbed
  $ docker exec -i picbed flask sa create -u 管理员账号 -p 密码 --isAdmin
  ```

  使用 *docker run* 启动镜像的命令仅供参考，picbed所用配置可以使用-e设置
  环境变量，必需项picbed_redis_url，其他请参考文档。

  此单一启动镜像方式不包括redis，所以还需要提前准备好redis才行。

------

如果有docker-compose的使用经验，可以使用命令 ``docker-compose up -d``
在后台启动项目，它会直接启动一个redis、并构建启动picbed应用，redis开启AOF，
宿主机映射9514端口以供外部访问，且使用数据卷挂载静态资源、挂载上传目录。

使用前，创建用户：

```bash
$ cd /path/to/picbed
$ docker-compose exec webapp flask sa create -u 管理员账号 -p 密码 --isAdmin
```

- Dockerfile采用分阶段构建，推送到Docker hub，latest标签是master分支，
  dev标签是dev分支，其他标签是已发布的版本。

- docker-compose.yml仅为简单定义，可以自行修改，比如加上nginx、redis挂载数据(/data)。

## 文档

详细文档请访问：[Picbed Docs](https://picbed.rtfd.vip)

## 演示站

http://demo.picbed.pro

测试账号及密码：demo 123456（请勿修改）

对外服务，为防止乱传已关闭匿名上传，随意注册，但不可用于非测试用途，图片保留删除权利！

## 客户端上传

#### - 使用PicGo上传到自定义的picbed图床

[下载PicGo](https://github.com/Molunerfinn/PicGo/releases)并安装，打开主界面，在 **插件设置** 中搜索 **web-uploader** 并安装，然后在 **图床设置-自定义Web图床** 中按照如下方式填写：

```
url: http[s]://你的picbed域名/api/upload

paramName: picbed

jsonPath: src

# 以上是匿名上传，仅在管理员开启匿名时才能上传成功
## 如需登录上传，请使用token(在控制台-个人资料-Token查看)，以下两种任选:
customHeader: {"Authorization": "Token 你的Token值"}
customBody: {"token": "你的Token值", "album: "相册名或留空"}

## 可用LinkToken替换Token(仅用于Header)：
customHeader: {"Authorization": "LinkToken 你的LinkToken值"}
customBody: {"album: "相册名或留空"}
```

设置完之后选择自定义Web图床为默认图床即可。

#### - 使用uPic上传到自定义的picbed图床

[下载uPic](https://github.com/gee1k/uPic)并安装，在 **偏好设置-图床** 中添加 **自定义**，信息如下：

```
API地址：http[s]://你的picbed域名/api/upload

请求方式：POST

文件字段名：picbed

其他字段：增加Header字段 或 增加Body字段，任选一种方式：
  - Headers数据
    key: Authorization
    value: Token 你的Token值
    ## 可用LinkToken替换Token(仅用于Header)：
    key: Authorization
    value: LinkToken 你的LinkToken值

  - Body数据
    key: token
    value: 你的Token值
  # 如需设置相册，请增加Body字段，key为album，value即相册名

URL路径：["src"]
```

#### - 作为自定义命令在使用Typora时上传图片到picbed

[Typora](https://typora.io)是一款跨平台的Markdown编辑器，
在编写内容时可以对图片进行特殊处理，比如上传图片。

有此需求故写了独立脚本（cli/cli.py）用以上传，支持Python2.7、3.x，
可以把[cli.py](cli/cli.py)单独下载到本地，名称随意，无第三方模块依赖。

打开Typora，定位到偏好设置-图像，选择插入图片时-上传图片，上传服务设定：

上传服务：Custom Command

自定义命令：python /{picbed repo}/misc/cli.py -u {picbed url} -t {LinkToken} -s typora

- {picbed repo}: 表示仓库，无需检出，只需cli.py一个文件放到本地即可

- {picbed url}: 指定图床的服务地址，http[s]://你的picbed域名

- {LinkToken}: 设置LinkToken认证、授权，拥有api.upload的post权限

- 其他参数：-s指定输出风格（保持typora），-a指定相册名称，-h查看帮助信息

测试：点击『验证图片上传选项』按钮，验证是否成功。

当然，`cli.py`还支持很多首页不支持的API选项，参考[cli文档](https://picbed.rtfd.vip/cli.html)

> tip: cli.py正在用go改写

## 预览图

![首页上传](./Snapshot/homepage.png)

![管理我的图片](./Snapshot/pic.png)

![控制台管理员功能](./Snapshot/hook.png)

## Contributing

感谢您的贡献！

关于如何提交issue或pr，请参考 [contributing guidelines](./CONTRIBUTING.md)
