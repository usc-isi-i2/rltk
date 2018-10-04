import sys
import os
import tempfile
import logging

from distributed.cli import dask_scheduler, dask_worker


def help_info():
    print('Available commands:')
    print('remote.worker, remote.scheduler')


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('No command\n')
        help_info()

    cmd = sys.argv[1]
    sub_cmd = sys.argv[2:] if len(sys.argv) >= 3 else []
    sys.argv.pop(1)

    if cmd in ('help', '--help', 'h', '-h'):
        help_info()

    temp_path = os.path.join(tempfile.gettempdir(), 'rltk', 'remote')
    # working_dir = os.path.join(temp_path, 'working_dir')
    # os.chdir(working_dir)
    if cmd == 'remote.worker':
        logger = logging.getLogger('distributed.dask_worker')
        logger.setLevel(logging.ERROR)
        sys.argv.append('--local-directory')
        sys.argv.append(temp_path)
        sys.argv.append('--change-directory')
        sys.exit(dask_worker.go())
    elif cmd == 'remote.scheduler':
        logger = logging.getLogger('distributed.scheduler')
        logger.setLevel(logging.ERROR)
        sys.argv.append('--local-directory')
        sys.argv.append(temp_path)
        sys.exit(dask_scheduler.go())
    else:
        print('Unknown command\n')
        help_info()

    sys.exit()
