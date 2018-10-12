import asyncio, os, mimetypes


cookie = {'lastdir' : '/'}


def det_mime(path):
	typ = mimetypes.guess_type(path)[0]
	if typ:
		return typ
	else:
		return 'application/octet-stream'


async def dispatch(reader, writer):
    try:
        html_front = ('\n'
                      '    <html>\n'
                      '	<head>\n'
                      '		<title>Index of .//</title>\n'
                      '	</head>\n'
                      '	\n'
                      '	<body bgcolor="white">\n'
                      '		<h1>Index of .//</h1><hr>\n'
                      '			<div>\n'
                      )

        html_rear = ("			</div>\n"
                     "		<hr>\n"
                     "	</body>\n"
                     "</html>\n"
                     "    ")
        data = await reader.read(2048)
        # heads = reader.read()
        print(data.decode('ascii'))
        message = data.decode().split('\r\n')
        data = data.decode()
        header = message[0]
        method = header.split()[0]
        path = header.split()[1]
        file_path = '.' + path.rstrip()
        if os.path.isfile(file_path) or os.path.isdir(file_path):
            if method == 'GET':
                if file_path[len(file_path) - 1] != '/':
                    size = os.path.getsize(file_path)
                    index1 = data.find('Range: bytes=')
                    index2 = 0
                    ranges = ''
                    flag = False
                    if index1 > -1:
                        index2 = data.find('\r\n', index1)
                        ranges = data[index1 + 13: index2] + '/' + str(size)
                        if ranges[0:2] != '0-':
                            flag = True
                            formats = 'Content-Range: bytes {}\r\n'.format(ranges)
                    if flag:
	                    writer.writelines([
	                        b'HTTP/1.0 206 Partial Content\r\n',
	                        b'Content-Type:',
	                        det_mime(file_path).encode(),
	                        b'\r\n',
	                        # b'Content-Length:',
	                        # str(os.path.getsize(file_path)).encode(),
	                        formats.encode(),
	                        b'Connection: close\r\n',
	                        b'\r\n'
	                    ])
	                    writer.write(open(file_path, 'rb').read()) 
                    else:
	                    writer.writelines([
	                        b'HTTP/1.0 200 OK\r\n',
	                        b'Content-Type:',
	                        det_mime(file_path).encode(),
	                        b'\r\n',
	                        # b'Content-Length:',
	                        # str(os.path.getsize(file_path)).encode(),
	                        b'Connection: close\r\n',
	                        b'\r\n'
	                    ])
	                    writer.write(open(file_path, 'rb').read())
                else:
                    status = 'HTTP/1.0 200 OK\r\n' 
                    if path == '/' and cookie["lastdir"] != '/':
                        path = cookie["lastdir"]
                        status = 'HTTP/1.0 302 Found\r\nLocation: {} \r\n'.format(path)
                    html_files = ''
                    cookie["lastdir"] = path
                    file_path = '.' + path.rstrip()
                    for file in os.listdir(file_path):
                        if os.path.isdir(file_path + file):
                            file = file + '/'
                        html_files += str('<a href = "{}">'.format(str(file)) + str(file) + '</a><br>')
                    html = html_front + html_files + html_rear
                    writer.writelines([
                        status.encode(),
                        b'Content-Type:text/html; charset=utf-8\r\n',
                        b'Set-Cookie: lastdir = ',
                        path.encode(),
                        b'\r\nConnection: close\r\n',
                        b'\r\n',
                        html.encode(),
                        b'\r\n'
                    ])

            elif method == 'HEAD':
                if file_path[len(file_path) - 1] != '/':
                	size = os.path.getsize(file_path)
                	index1 = data.find('Range: bytes=')
                	index2 = 0
                	ranges = ''
                	flag = False
                	if index1 > -1:
                		index2 = data.find('\r\n', index1)
                		ranges = data[index1 + 13: index2] + '/' + str(size)
                		flag = True
                		formats = '\r\nContent-Range: bytes {}\r\n'.format(ranges)
                	if flag:
	                	writer.writelines([
	                        b'HTTP/1.0 206 Partial Content\r\n',
	                        b'Content-Type:',
	                        det_mime(file_path).encode(),
	                        b'; charset=utf-8\r\n',
	                        b'Content-Length:',
	                        str(size).encode(),
	                        formats.encode(),
	                        b'Connection: close\r\n',
	                        b'\r\n'
	                    ])
	                else:
	                    writer.writelines([
	                        b'HTTP/1.0 200 OK\r\n',
	                        b'Content-Type:',
	                        det_mime(file_path).encode(),
	                        b'; charset=utf-8\r\n',
	                        b'Content-Length:',
	                        str(size).encode(),
	                        b'\r\nConnection: close\r\n',
	                        b'\r\n'
	                    ])
                else:
                    html_files = ''
                    for file in os.listdir(file_path):
                        html_files += str('<a>' + str(file) + '</a><br>')
                    html = html_front + html_files + html_rear
                    writer.writelines([
                        b'HTTP/1.0 200 OK\r\n',
                        b'Content-Type:text/html; charset=utf-8\r\n',
                        b'\r\nConnection: close\r\n',
                        b'\r\n'
                    ])
            else:
                writer.writelines([
                    b'HTTP/1.0 405 Method Not Allowed\r\n',
                    b'Content-Type:text/html; charset=utf-8\r\n',
                    b'Connection: close\r\n',
                    b'\r\n'
                    b'405 Method Not Allowed',
                    b'\r\n'
                ])
        else:
            writer.writelines([
                b'HTTP/1.0 404 NOT FOUND\r\n',
                b'Content-Type:text/html; charset=utf-8\r\n',
                b'Connection: close\r\n',
                b'\r\n'
                b'404 NOT FOUND',
                b'\r\n'
            ])
        await writer.drain()
        writer.close()
    except:
        pass


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(dispatch, '127.0.0.1', 80, loop=loop)
    server = loop.run_until_complete(coro)
    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
