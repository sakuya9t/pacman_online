import datetime


def info(message):
    time = str(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"))
    message = str(message)
    print "(INFO) {time} {message}".format(time=time, message=message)