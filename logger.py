import datetime


def info(message):
    time = str(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"))
    message = str(message)
    print "\033[0m (INFO) {time} {message}".format(time=time, message=message)


def error(message):
    time = str(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"))
    message = str(message)
    print "\033[91m (ERROR) {time} {message}".format(time=time, message=message)


def warning(message):
    time = str(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"))
    message = str(message)
    print "\033[93m (ERROR) {time} {message}".format(time=time, message=message)