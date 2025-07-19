# 日志用
import sys
import traceback
import logging

from PyQt6.QtCore import QtMsgType, qInstallMessageHandler
from PyQt6.QtWidgets import QApplication


class SafeApplication(QApplication):
    def notify(self, obj, event):
        try:
            return super().notify(obj, event)
        except Exception as e:
            print(f"事件处理异常: {e}")
            traceback.print_exc()
            return False


def qt_message_handler(mode, context, message):
    if mode in (QtMsgType.QtCriticalMsg, QtMsgType.QtFatalMsg):
        logging.critical(f"Qt内部错误: {message}")
        traceback.print_stack(context)
        sys.exit(1)


# 配置日志系统
def setup_logging():
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app_error.log', mode='w'),  # 输出到文件
            logging.StreamHandler()  # 同时打印到控制台
        ]
    )


def record(e):
    print(f"主函数捕获: {e}")
    logging.critical(f"主程序崩溃: {e}", exc_info=True)  # 记录完整堆栈


def start():
    setup_logging()
    qInstallMessageHandler(qt_message_handler)


def get_app():
    app = SafeApplication(sys.argv)
    return app
