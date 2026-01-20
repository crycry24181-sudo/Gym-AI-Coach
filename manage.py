#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# 👇 THÊM ĐOẠN NÀY ĐỂ SỬA LỖI PYTHON 3.13 + MONGODB 👇
# Python 3.13 đã xóa distutils, nhưng Djongo lại cần nó.
# Dòng này giúp "hồi sinh" distutils để nút Run chạy được.
try:
    import setuptools
except ImportError:
    pass
# 👆 KẾT THÚC PHẦN SỬA 👆


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()