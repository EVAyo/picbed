picbed - 简约不小气的自建图床程序
====================================

.. toctree::
    :maxdepth: 1

    install
    docker
    usage
    linktoken
    cli
    admin
    hook
    api
    module
    faq
    changelog

.. _picbed-readme:

======
概述
======

基于Flask的Web自建图床，默认存储在本地，内置支持又拍云、七牛云、阿里云OSS、腾讯云COS等对象存储，支持GitHub、Gitee（码云）。

GitHub：https://github.com/staugur/picbed

Gitee：https://gitee.com/staugur/picbed

语言：Python

框架：Flask

.. _picbed-features:

功能：
------

1. 可作为私有或公共（多用户）的图床程序

2. 可插拔的钩子管理器，允许第三方扩展功能点

  - 扩展了如sm.ms,superbed.cn等公共图床
  - 多个扩展点，针对多个功能增强，开发简单

3. API

  - 基于api的上传接口，支持通过文件域、base64（允许Data URI形式）、Image URL上传
  - 可定制的api响应数据[及字段]及中英错误消息提示
  - 支持Token以及更安全的基于Token的LinkToken调用api
  - 外部网站通过按钮一键上传的插件

4. 我的图片快捷复制支持原生URL、HTML、reStructuredText、Markdown格式，可定制图片处理

5. 管理员控制台可配置全局参数定制站点信息以及用户个性自定义覆盖全局参数

6. 支持PyPy、Python2.7、3.5+（推荐），支持Docker且实时构建最新镜像传到官方仓库

7. 支持油猴脚本（用户脚本） ，使用它，几乎可以采集全网图片！

8. 多种上传方式：用户脚本、JS SDK、命令行工具（支持三端系统，可集成Windows、macOS右键菜单）、支持HTTP API的图床客户端

不足：
-------

- 图床管理暂时不能批量化

- 基于redis的数据存储，虽响应快，但数据存储方面可能有些风险

.. _picbed-deploy:

一句话部署：
------------

1. 要求： Python2.7（3.5+）和Redis
2. 下载： ``git clone https://github.com/staugur/picbed && cd picbed``
3. 依赖： ``pip install -r requirements/all.txt``
4. 配置： ``config.py`` 即配置文件，可从 `.cfg` 文件或环境变量读取配置信息。
5. 启动： make start 或 sh online\_gunicorn.sh start

详细部署请看下一篇！
--------------------

文档中录制了一些操作过程，所用系统CentOS7.8最小化安装的纯净系统， Python2.7.5
