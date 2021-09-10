from urllib.parse import urlparse


def parse(command, url):
    if not command:
        return ""
    if not url:
        return command

    o = urlparse(url)

    command = command.replace("$host$", o.netloc)
    command = command.replace("$url$", url)

    return command
