import socket
import time
from lame import frame_length


def listen(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send("GET /stream.mp3 HTTP/1.0\r\n\r\n")

    at = None
    times = []

    start = None
    off = 0
    while True:
        start = s.recv(16)
        if "\xFF\xFB" in start:
            i = start.index("\xFF\xFB")
            off = len(start) - i - 4
            start = start[i:i + 4]
            break

    while True:
        if start:
            header = start
            start = None
        else:
            header = s.recv(4)
            off = 0
        if not len(header):
            break
        flen = frame_length(header)
        data = s.recv(flen - 4 - off)
        got = time.time()
        if not len(data):
            break
        if at:
            times.append(got - at)
            avg = ((1152 / 44100.0) / (sum(times) / len(times)))
            print "Frame (%d bytes, %2.5fs) received after %2.5fs\t(%2.2fx)\tAvg: %fx" % \
                    (len(data), 1152 / 44100.0, got - at,  (1152 / 44100.0) / (got - at), avg)
        at = got

if __name__ == "__main__":
    listen("localhost", 8192)
