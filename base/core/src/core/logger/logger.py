import logging
from logging import Logger
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
from pathlib import Path
from typing import cast

import colorlog
import yaml
import sys

CONFIG_FILE = Path(__file__).parent / "logger.yaml"

_log_queue = Queue(-1)
_listener = None


def _load_yaml():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"{CONFIG_FILE} not found")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _make_formatter(formatters_cfg, name):
    default_fmt = "%(log_color)s%(asctime)s\t[%(levelname)s]\t[%(module)s:%(lineno)d]\t%(message)s"
    if not formatters_cfg or not name:
        return logging.Formatter(default_fmt)
    fmt_entry = formatters_cfg.get(name, {})
    fmt = fmt_entry.get("format", default_fmt)
    return colorlog.ColoredFormatter(fmt, reset=True)


def _setup_logging():
    """
    最简设计：
    - 从 yaml 读取格式与 root 级别
    - 在代码中只创建一个 StreamHandler(sys.stdout)，用于所有级别
    - 清空 root 的已有 handler，替换为 QueueHandler（唯一入口）
    - 启动 QueueListener，用上面单一 stdout handler 异步输出
    """
    global _listener

    cfg = _load_yaml()
    formatters_cfg = cfg.get("formatters", {}) if cfg else {}
    root_cfg = cfg.get("root", {}) if cfg else {}
    root_level = root_cfg.get("level", "INFO").upper()

    # 创建单一 stdout handler（接收所有级别）
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)  # 接收所有级别，交由 root level 控制输出
    # 使用 yaml 中第一个 formatter（若有），否则默认格式
    # 尝试找到一个 formatter 名称（取 handlers 中第一个的 formatter）
    first_formatter_name = None
    handlers_cfg = cfg.get("handlers", {}) if cfg else {}
    if handlers_cfg:
        # 取第一个 handler 配置的 formatter 名称（若存在）
        for _, hcfg in handlers_cfg.items():
            first_formatter_name = hcfg.get("formatter")
            if first_formatter_name:
                break

    stdout_handler.setFormatter(_make_formatter(formatters_cfg, first_formatter_name))

    # 清理 root logger 的所有 handler（避免重复）
    root_logger = logging.getLogger()
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)

    # root 只挂一个 QueueHandler（把日志放到队列里）
    qhandler = QueueHandler(_log_queue)
    root_logger.addHandler(qhandler)
    root_logger.setLevel(getattr(logging, root_level, logging.INFO))

    # QueueListener 负责把队列中的记录异步写到 stdout_handler
    _listener = QueueListener(_log_queue, stdout_handler, respect_handler_level=True)
    _listener.start()


# 模块导入时初始化（只会执行一次）
_setup_logging()


class _LoggerProxy:
    """import logger 后直接用 logger.info(...)，自动绑定调用模块名"""

    def __getattr__(self, name):
        frame = sys._getframe(1)
        module_name = frame.f_globals.get("__name__", "unknown")
        return getattr(logging.getLogger(module_name), name)

    def __dir__(self):
        # 返回 logging.Logger 的属性列表，方便交互式查看
        return sorted(set(dir(logging.getLogger()) + list(self.__dict__.keys())))


logger = cast(Logger, cast(object, _LoggerProxy()))
logger.info("logger config loaded")
