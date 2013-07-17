#$ mystbot_plugin 01

import re

LOG_CACHE_FILE = 'dynamic/logcache.txt'

initialize_file(LOG_CACHE_FILE, '{}')
LOG_FILENAME_CACHE = eval(read_file(LOG_CACHE_FILE))

def log_write_header(fp, source, (year, month, day, hour, minute, second, weekday, yearday, daylightsavings)):
    body="""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<style type="text/css">
<!--
.timestamp {color: #AAAAAA;}
.system {color: #009900; font-weight: bold;}
.emote {color: #AA0099;}
.self {color: #CC0000;}
.normal {color: #0000AA;}
h1 { color: #336699; font-family: sans-serif; border-bottom: #224466 solid 3pt; letter-spacing: 3px; margin-left: 20pt; }
h2 { color: #663399; font-family: sans-serif; letter-spacing: 2px; text-align: center }
//-->
</style>
<title>""" + source + """</title>
</head>
<body>
<div style="color: #AAAAAA; text-align: right; font-family: monospace; letter-spacing: 3px">mystbot log</div>
<h1>""" + source + """</h1>
<h2>""" + time.strftime('%A, %B %d, %Y', (year, month, day, hour, minute, second, weekday, yearday, daylightsavings)) + """</h2>
<br />
<code>
"""
    body=body.encode('utf-8')
    fp.write(body)

def log_write_footer(fp):
    fp.write('\n</code>\n</body>\n</html>')

def log_get_fp(type, source, (year, month, day, hour, minute, second, weekday, yearday, daylightsavings)):
    if type == 'public':
        logdir = PUBLIC_LOG_DIR
    else:
        logdir = PRIVATE_LOG_DIR
    if logdir[-1] == '/':
        logdir = logdir[:-1]
    str_year = str(year)
    str_month = str(month)
    str_day = str(day)
    filename = logdir + '/' + source + '/' + str_year + '/' + str_month + '/' + str_day + '.html'
    alt_filename = logdir + '/' + source + '/' + str_year + '/' + str_month + '/' + str_day + '_alt.html'
    if not os.path.exists(logdir):
        os.mkdir(logdir)
    if not os.path.exists(logdir + '/' + source):
         try:
	    os.mkdir(logdir + '/' + source)
	 except:
	    pass
    if not os.path.exists(logdir + '/' + source + '/' + str_year):
	try:
    	    os.mkdir(logdir + '/' + source + '/' + str_year)
	except:
	    pass
    if not os.path.exists(logdir + '/' + source + '/' + str_year + '/' + str_month):
	try:
    	    os.mkdir(logdir + '/' + source + '/' + str_year + '/' + str_month)
	except:
	    pass    
    if LOG_FILENAME_CACHE.has_key((source, type)):
        if LOG_FILENAME_CACHE[(source, type)] != filename:
            try:
		fp_old = file(LOG_FILENAME_CACHE[(source, type)], 'a')
        	log_write_footer(fp_old)
        	fp_old.close()
	    except:
		pass
        if os.path.exists(filename):
            fp = file(filename, 'a')
            return fp
        else:
            LOG_FILENAME_CACHE[(source, type)] = filename
            write_file(LOG_CACHE_FILE, str(LOG_FILENAME_CACHE))
            fp = file(filename, 'w')
            log_write_header(fp, source, (year, month, day, hour, minute, second, weekday, yearday, daylightsavings))
            return fp
    else:
        if os.path.exists(filename):
            LOG_FILENAME_CACHE[(source, type)] = filename
            write_file(LOG_CACHE_FILE, str(LOG_FILENAME_CACHE))
            fp = file(alt_filename, 'a')
            # log_write_header(fp, source, (year, month, day, hour, minute, second, weekday, yearday, daylightsavings))
            return fp
        else:
            LOG_FILENAME_CACHE[(source, type)] = filename
            write_file(LOG_CACHE_FILE, str(LOG_FILENAME_CACHE))
            fp = file(filename, 'w')
            log_write_header(fp, source, (year, month, day, hour, minute, second, weekday, yearday, daylightsavings))
            return fp

def log_get_timestamp(hour, minute):
    timestamp = '['
    if hour < 10:
        timestamp += '0'
    timestamp += str(hour)
    timestamp += ':'
    if minute < 10:
        timestamp += '0'
    timestamp += str(minute)
    timestamp += ']'
    return timestamp

def log_regex_url(matchobj):
    # 06.03.05(Sun) slipstream@yandex.ru urls parser
    return '<a href="' + matchobj.group(0) + '">' + matchobj.group(0) + '</a>'

def log_handler_message(type, source, body):
    if not body:
        return
    (year, month, day, hour, minute, second, weekday, yearday, daylightsavings) = time.gmtime()
    if type == 'public' and PUBLIC_LOG_DIR:
        groupchat = source[1]
        nick = source[2]
        # 06.03.05(Sun) slipstream@yandex.ru urls parser & line ends
        body = body.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        body = re.sub('(http|ftp)(\:\/\/[^\s<]+)', log_regex_url, body)
        body = body.replace('\n', '<br />')
        body = body.encode('utf-8');
        nick = nick.encode('utf-8');
        timestamp = log_get_timestamp(hour, minute)
        fp = log_get_fp('public', groupchat, (year, month, day, hour, minute, second, weekday, yearday, daylightsavings))
        fp.write('<span class="timestamp">' + timestamp + '</span> ')
        if not nick:
            fp.write('<span class="system">' + body + '</span><br />\n')
        elif body[:3].lower() == '/me':
            fp.write('<span class="emote">* ' + nick + body[3:] + '</span><br />\n')
        else:
            # 08.03.05(Tue) slipstream@yandex.ru encoding
            if nick == get_nick(groupchat).encode('utf-8'):
                fp.write('<span class="self">&lt;' + nick + '&gt;</span> ')
            else:
                fp.write('<span class="normal">&lt;' + nick + '&gt;</span> ')
            fp.write(body + '<br />\n')
        fp.close()
    elif type == 'private' and PRIVATE_LOG_DIR:
        jid = get_true_jid(source)
        nick = string.split(jid, '@')[0]
        # 06.03.05(Sun) slipstream@yandex.ru urls parser, line ends & encoding
        body = body.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        body = re.sub('(http|ftp)(\:\/\/[^\s<]+)', log_regex_url, body)
        body = body.replace('\n', '<br />')
        body = body.encode('utf-8');
        nick = nick.encode('utf-8');
        timestamp = log_get_timestamp(hour, minute)
        fp = log_get_fp('private', jid, (year, month, day, hour, minute, second, weekday, yearday, daylightsavings))
        fp.write('<span class="timestamp">' + timestamp + '</span> ')
        if body[:3].lower() == '/me':
            fp.write('<span class="emote">* ' + nick + body[3:] + '</span><br />\n')
        else:
            fp.write('<span class="normal">&lt;' + nick + '&gt;</span> ' + body + '<br />\n')
        fp.close()

def log_handler_outgoing_message(target, body):
    if GROUPCHATS.has_key(target) or not body:
        return
    (year, month, day, hour, minute, second, weekday, yearday, daylightsavings) = time.gmtime()
    jid = get_true_jid(target)
    nick = 'mystbot'
    # 06.03.05(Sun) slipstream@yandex.ru urls parser, line ends & encoding
    body = body.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    body = re.sub('(http|ftp)(\:\/\/[^\s<]+)', log_regex_url, body)
    body = body.replace('\n', '<br />')
    body = body.encode('utf-8');
    nick = nick.encode('utf-8');
    timestamp = log_get_timestamp(hour, minute)
    fp = log_get_fp('private', jid, (year, month, day, hour, minute, second, weekday, yearday, daylightsavings))
    fp.write('<span class="timestamp">' + timestamp + '</span> ')
    if body[:3].lower() == '/me':
        fp.write('<span class="emote">* ' + nick + body[3:] + '</span><br />\n')
    else:
        fp.write('<span class="self">&lt;' + nick + '&gt;</span> ' + body + '<br />\n')
    fp.close()

if PUBLIC_LOG_DIR or PRIVATE_LOG_DIR:
    register_message_handler(log_handler_message)
if PRIVATE_LOG_DIR:
    register_outgoing_message_handler(log_handler_outgoing_message)
