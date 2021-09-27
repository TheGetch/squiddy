from urllib.parse import urlparse
import socket


def parse(command, url):
    if not command:
        return ""
    if not url:
        return command

    o = urlparse(url)

    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)

    command = command.replace("$host$", o.netloc)
    command = command.replace("$url$", url)

    try:
        command = command.replace("$ip$", socket.gethostbyname(o.netloc))
    except socket.gaierror as e:
        print(e)

    command = command.replace("$localhost$", host_name)
    command = command.replace("$localip$", host_ip)

    return command
