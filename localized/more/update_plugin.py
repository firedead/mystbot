#$ mystbot_plugin 01

import httplib

UPDATE_HOST = 'www.jabber.ru'
UPDATE_PATH = '/projects/mystbot/files/'

VERSIONS_FILE = 'dynamic/versions.txt'

def update_download(file):
	httpcon = httplib.HTTPConnection(UPDATE_HOST)
	httpcon.request('GET', UPDATE_PATH + file)
	response = httpcon.getresponse()
	if response.status == 200:
		reply = response.read()
	else:
		reply = None
	httpcon.close()
	return reply

def handler_update_update(type, source, parameters):
	try:
		server_versions = eval(update_download('dynamic/versions.txt'))
	except:
		smsg(type, source, 'Server Error')
		return
	my_versions = eval(read_file(VERSIONS_FILE))
	to_update = []
	to_remove = []
	for filename in my_versions:
		if server_versions.has_key(filename):
			if my_versions[filename] < server_versions[filename]:
				to_update.append(filename)
		else:
			to_remove.append(filename)
	for filename in server_versions:
		if not my_versions.has_key(filename):
			to_update.append(filename)
	if not (to_update or to_remove):
		smsg(type, source, 'Mystbot is already completely up to date. Finished')
		return
	for filename in to_remove:
		smsg(type, source, 'Removing: ' + filename)
		os.remove(filename)
		del my_versions[filename]
	for filename in to_update:
		smsg(type, source, 'Updating: ' + filename)
		new_file_data = update_download(filename)
		if new_file_data == 'None':
			smsg(type, source, 'Error Updating: ' + filename)
			continue
		update_fp = file(filename, 'wb')
		update_fp.write(new_file_data)
		update_fp.close()
		my_versions[filename] = server_versions[filename]
	write_file(VERSIONS_FILE, str(my_versions))
	smsg(type, source, 'Mystbot is now completely up to date. Finished')

register_command_handler(handler_update_update, '!update', 100, 'Updates Mystbot from Internet.', '!update', ['!update'])
