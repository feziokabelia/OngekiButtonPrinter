import sys
from core.mainwindows import ArcadeController
from utils import logger


if __name__ == '__main__':
    logger.start()
    app = logger.get_app()
    try:
        window = ArcadeController()
        window.show()
        sys.exit(app.exec())
    except SystemExit:
        pass
    except Exception as e:
        logger.record(e)

