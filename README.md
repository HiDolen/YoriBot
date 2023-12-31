## 本项目还正在开发中

功能未完成。

### 现有问题

- [ ] 签到插件
  - [ ] 使图片不从本地发送
- [ ] 群词条插件
  - [ ] 不使用 cq 码，使用消息链

### bot 功能

直接功能，

- [ ] 概率复读
- [ ] 随机数生成 / 随机选择
- [ ] 图库
- [ ] 简单的 ai 回复
  - [ ] gpt2？
  - [ ] 青云客？
  - [ ] bingAI？
- [ ] 撤回监控

复杂功能，

- [ ] 群聊图片与整理
- [ ] 群聊历史记录
- [ ] web ui
  - [ ] 界面基础实现
  - [ ] 提供简明的接入接口
- [ ] 每日报告
- [ ] 数据备份

提上日程，

- [ ] bot 消息发送阻塞。避免同时发出，并避免短时间发出相同消息
- [ ] 群被动开关实现。最好先看其他定时器插件怎么写的

### 整体修改

- [ ] 从 cq 码转到消息链（`MessageSegment`）
- [ ] 图片不从本地发送，而是先转换为 bytes 或 base64

> ```python
> async with aiofiles.open('') as f:
>     pic = await f.read()
>     MessageSegment.image(pic)
> ```

- [ ] 同时兼容 v11、v12 等多协议
- [ ] 整理指令触发优先级，汇总为表格

## 一些数值的意义

群权限，

| 值          | 意义                                                              |
| ----------- | ----------------------------------------------------------------- |
| -1（默认）  | 若 bot 程序在线，加入群后 bot 会立即自动退群。除此之外与 0 无区别 |
| 0           | bot 会主动关闭所有功能                                            |
| 1           | bot 开启超级管理员设定的功能。群管理不能修改插件的开关情况        |
| 2（群认证） | 允许群管理员自由开关超级管理员设定的特权插件                      |
| 3           | 允许群管理员开关任意插件                                          |
| 4           | 允许任何人开关任意插件                                            |

## 插件信息设置

基本格式，

```python
__plugin_meta__ = PluginMetadata(
    name="进群欢迎",
    description=r"新人入群时的欢迎语",
    usage="""
    群欢迎消息
    """,
    type="application",
    supported_adapters={"~onebot.v11"},
    extra={
        "default_status": True,
    }
)
```

基础，

| 键               | 值意义                                                        |
| ---------------- | ------------------------------------------------------------- |
| `name`           | 将作为 `plugin_name` 存储在数据库。决定了插件向用户的显示名称 |
| `description`    | 插件的说明文字                                                |
| `usage`          | 插件的使用方法                                                |
| `type`(TODO)     | 插件的分类                                                    |
| `default_status` | 新入群时，初始化的插件状态。bool 类型。默认为 True            |

其他，

| 变量名                 | 意义                           |
| ---------------------- | ------------------------------ |
| `__force_to_operate__` | 无视群权限的限制，强制执行插件 |

## 杂项

### 插件信息

- `plugin_name` 是插件设定的显示名称，在 `__plugin_meta__` 中的 `name` 设置
- `plugin` 由插件文件命名决定，是独一无二的插件标识

### 插件管理

插件可以在信息设置中配置默认状态。新入群时，会根据设置的默认状态开启或关闭插件。

群管理开关群插件的权限，与群权限、插件的默认开关状态、特权插件的设置有关：

- 群权限小于等于 1，不允许群管理开关群插件。仅超级管理员可以开关群插件
- 群权限为 2，群管理仅可自由开关群的特权插件。特权插件需要超级管理员针对各个群设置
  - 也就是说，群管理也没有关闭特权插件之外的插件的权限
- 群权限为 3，允许群管理开关任意插件
- 群权限为 4，允许任何人开关任意插件

### 插件帮助

TODO 插件帮助插件。

TODO 超级用户插件是单独的帮助页面。通过插件信息中的分类进行分辨。

### 文件结构

- `basic_plugins` 存放 yoribot 运行所需的必要插件，`plugins` 存放预置插件
- `data` 存放插件运行产生的数据
- temp 资源位于 `resources/temp`
- 用户自定义插件推荐放在 `plugins_extensive`

## TODO

- 使用 `bot.send_group_msg` 实现定时发送，使用 `@Bot.on_calling_api` 实现定时发送的阻断

## 部署（Windows）

若不知道怎么部署 poetry 虚拟环境，以下步骤可供参考。

首先需要安装 Python，在此不赘述。Python 版本需要大于等于 3.10。

打开终端，执行 `pip install pipx`，执行 `pipx install poetry`，执行 `pipx ensurepath`。

将项目 clone 到本地，在项目路径下打开终端，执行 `poetry install`，等待虚拟环境部署完成。

最后执行 `poetry run bot.py`，即可启动 bot。

若出现 `the greenlet library is required to use this function. DLL load failed while importing _greenlet: The specified module could not be found.` 的错误，请安装 [Microsoft Visual C++ Redistributable](https://learn.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist?view=msvc-170)，以保证数据库功能的正常运作。

### 运行 bot 之前……

在 bot 根目录下添加 `.env` 文件，以确定指令开头、超级管理员账号：

```yml
HOST=127.0.0.1
PORT=8080

COMMAND_START=[".", "。"]
COMMAND_SEP=["."]

SUPERUSERS=["145xxxxxxxx"]
```
