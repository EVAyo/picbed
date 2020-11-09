#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
    cli.py
    ~~~~~~

    The command-line client for picbed.

    :copyright: (c) 2020 by staugur.
    :license: BSD 3-Clause, see LICENSE for more details.
"""

__version__ = "0.3.1"
__author__ = "staugur <me@tcw.im>"

import argparse
from json import loads, dumps
from base64 import b64encode
from sys import version_info, platform
from os import getenv, system, remove
from os.path import abspath, basename, isfile
from tempfile import NamedTemporaryFile


PY2 = version_info[0] == 2

if PY2:
    #: pylint: disable=import-error
    import urllib2
    #: pylint: disable=no-name-in-module
    from urllib import urlencode
else:
    import urllib.request as urllib2
    from urllib.parse import urlencode

allowed_style = ("default", "typora", "line")


def style_type(value):
    if value not in allowed_style:
        try:
            if not value or "." not in value:
                raise ValueError
            mod, func = value.split(".")
            module = __import__(mod)
        except ValueError:
            raise argparse.ArgumentTypeError("invalid style type")
        except ImportError:
            raise argparse.ArgumentTypeError("not found module: " + mod)
        else:
            if not hasattr(module, func):
                raise argparse.ArgumentTypeError("not found func: " + func)
    return value


def get_os_type():
    pf = platform.lower()
    if pf.startswith("linux"):
        return "linux"
    elif pf.startswith("win"):
        return "windows"
    elif pf.startswith("darwin"):
        return "macos"
    else:
        return "unknown"


def gen_tmp_ps():
    tpl = '''
param(
    [String] $Title = 'Upload successfully',
    [String] $SubTitle = 'Copied to clipboard'
)

[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

$APP_ID = '110366bd-56e2-47ed-9bdf-3ce1fa408b6c'

$template = @"
<toast>
    <visual>
        <binding template="ToastText02">
            <text id="1">$($Title)</text>
            <text id="2">$($SubTitle)</text>
        </binding>
    </visual>
</toast>
"@

$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = New-Object Windows.UI.Notifications.ToastNotification $xml
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($APP_ID).Show($toast)
'''
    with NamedTemporaryFile(mode='w', suffix='.ps1', delete=False) as fp:
        fp.write(tpl)
        return fp.name


def auto_copy(content):
    ost = get_os_type()
    if PY2 and not isinstance(content, str):
        content = content.encode("utf-8")
    if ost == "windows":
        code = system("echo %s | clip" % content)
        if code == 0:
            sf = gen_tmp_ps()
            if isfile(sf):
                cmd = "powershell -ExecutionPolicy Unrestricted {}".format(sf)
                if not PY2:
                    cmd = "%s %s %s" % (cmd, "上传成功", "已复制到剪贴板")
                system(cmd)
                remove(sf)

    elif ost == "macos":
        code = system('echo "%s" | pbcopy' % content)
        if code == 0:
            system(
                'osascript -e \'display notification "已复制到剪贴板"'
                ' with title "上传成功"  sound name "default"\''
            )
        return code

    elif ost == "linux":
        #: install xclip with `apt/yum install xclip`
        return system('echo "%s" | xclip -selection clipboard' % content)


def copy_parse_result(copy_type, result):
    uns = [
        dict(url=res["src"], name=res["filename"], tpl=res.get("tpl") or {})
        for res in result
        if isinstance(res, dict) and res.get("code") == 0
    ]
    if copy_type == "md":
        contents = [
            u["tpl"].get(
                "Markdown",
                "![](%s)" % (u["url"])
            )
            for u in uns
        ]
    elif copy_type == "rst":
        contents = [
            u["tpl"].get(
                "rST",
                ".. image:: %s" % (u["url"])
            )
            for u in uns
        ]
    else:
        contents = [u["tpl"].get("URL", u["url"]) for u in uns]
    return contents


def main(parser):
    args = parser.parse_args()
    api = args.picbed_url
    token = args.picbed_token
    album = args.album or ""
    title = args.desc or ""
    expire = args.expire or 0
    if not api:
        api = getenv("picbed_cli_apiurl")
        if not api:
            print("Please enter picbed api url")
            return
    if not api.endswith("/api/upload"):
        api = "{}/api/upload".format(api.rstrip("/"))
    if not token:
        token = getenv("picbed_cli_apitoken")
    style = args.style
    copy = args.copy
    files = args.file
    result = []
    for f in files:
        filepath = abspath(f)
        filename = basename(filepath)
        if isfile(filepath):
            with open(filepath, "rb") as fp:
                stream = fp.read()
            req = urllib2.Request(
                api,
                data=urlencode(dict(
                    picbed=b64encode(stream),
                    filename=filename,
                    album=album,
                    title=title,
                    expire=expire,
                    origin="cli/{}".format(__version__),
                )).encode("utf-8"),
                headers={
                    "Authorization": "LinkToken {}".format(token),
                    "User-Agent": "picbed-cli/{}".format(__version__),
                },
            )
            res = urllib2.urlopen(req)
            res = loads(res.read())
            result.append(res)
    if result:
        if style == "typora":
            print("Upload Success:")
            for res in result:
                if isinstance(res, dict) and res.get("code") == 0:
                    print(res["src"])

        elif style == "line":
            for res in result:
                if isinstance(res, dict) and res.get("code") == 0:
                    print(res["src"])

        elif "." in style:
            mod, func = style.split(".")
            getattr(__import__(mod), func)(result)

        else:
            print(dumps(result))

        #: auto copy
        if copy:
            contents = copy_parse_result(copy, result)
            if contents:
                return auto_copy("\\n".join(contents))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="picbed cli",
        description='More docs to https://picbed.rtfd.vip/cli.html',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-u", "--picbed-url",
        help=(
            "The picbed upload api url.\n"
            "Or use environment variable: picbed_cli_apiurl"
        ))
    parser.add_argument(
        "-t", "--picbed-token",
        help=(
            "The picbed LinkToken.\n"
            "Or use environment variable: picbed_cli_apitoken"
        ))
    parser.add_argument("-a", "--album", help="Set image album")
    parser.add_argument("-d", "--desc", help="Set image title(description)")
    parser.add_argument(
        "-e", "--expire", type=int,
        help="Set image expire(seconds)"
    )
    parser.add_argument(
        "-s", "--style", default="default", type=style_type,
        help=(
            "The upload result output style from: { %s }.\n"
            "Or, allows the use of \"module.function\" to "
            "customize the output style."
        ) % ", ".join(allowed_style))
    parser.add_argument(
        "-c", "--copy", choices=["url", "md", "rst"],
        help=(
            "Copy the uploaded image url type to the clipboard "
            "for win/mac/linux.\n"
            "By the way, md=makrdown, rst=reStructuredText"
        )
    )
    parser.add_argument("file", nargs="+", help="Local file")
    main(parser)
