import time
from datetime import datetime
from urllib.parse import quote_plus

import xbmc
import xbmcgui

DATE_FORMAT = "%Y-%m-%d %H:%M:00"


def log(x):
    xbmc.log(repr(x), xbmc.LOGERROR)


def escape(value):
    # value = value.decode("utf8")
    # value = value.encode("utf8")
    return quote_plus(value)


def get_format():
    dateFormat = xbmc.getRegion('datelong')
    timeFormat = xbmc.getRegion('time').replace('%H%H', '%H').replace('%I%I', '%I')
    timeFormat = timeFormat.replace(":%S", "")
    return "{}, {}".format(dateFormat, timeFormat)


def extract_date(dateLabel, timeLabel):
    date = xbmc.getInfoLabel(dateLabel)
    language = xbmc.getLanguage(xbmc.ENGLISH_NAME)
    xbmc.log("(contextEPG.extract_date) Language: " + language, xbmc.LOGWARNING)
    localname = xbmc.getLanguage(format=xbmc.ISO_639_1, region=True)
    xbmc.log("(contextEPG.extract_date) localname: " + localname, xbmc.LOGWARNING)
    if language == 'German':
        # locale de_DE is not known in LibreElec 9.2.6
        date = date.replace('Sonntag', 'Sunday').replace('Montag', 'Monday').replace('Dienstag', 'Tuesday').replace('Mittwoch', 'Wednesday').replace('Donnerstag', 'Thursday').replace('Freitag', 'Friday').replace('Samstag', 'Saturday')
        date = date.replace('Januar', 'January').replace('Februar', 'February').replace('M\xe4rz', 'March').replace('April', 'April').replace('Mai', 'May').replace('Juni', 'June').replace('Juli', 'July').replace('Oktober', 'October')
    if language == 'Hungarian':
        date = date.replace('Vas\xE1rnap', 'Sunday').replace('H\xE9tf\x97', 'Monday').replace('Kedd', 'Tuesday').replace('Szerda', 'Wednesday').replace('Cs\xFCt\xF6rt\xF6k', 'Thursday').replace('P\xE9ntek', 'Friday').replace('Szombat', 'Saturday')
        date = date.replace('Janu\xE1r', 'January').replace('Febru\xE1r', 'February').replace('M\xE1rcius', 'March').replace('\xC1prilis', 'April').replace('M\xE1jus', 'May').replace('J\xFAnius', 'June').replace('J\xFAlius', 'July').replace('Augusztus', 'August').replace('Szeptember', 'September').replace('Okt\xF3ber', 'October')

    timeString = xbmc.getInfoLabel(timeLabel)
    fullDate = "{}, {}".format(date, timeString)

    # https://bugs.python.org/issue27400
    try:
        parsedDate = datetime.strptime(fullDate, fullFormat)
    except TypeError:
        parsedDate = datetime(*(time.strptime(fullDate, fullFormat)[0:6]))
    return datetime.strftime(parsedDate, DATE_FORMAT)


fullFormat = get_format()

channel = escape(xbmc.getInfoLabel("ListItem.ChannelName"))
title = escape(xbmc.getInfoLabel("ListItem.Label"))

try:
    start = extract_date("ListItem.StartDate", "ListItem.StartTime")
    stop = extract_date("ListItem.EndDate", "ListItem.EndTime")
    xbmc.log("Record info: {} {} {} - {}".format(channel, title, start, stop), xbmc.LOGWARNING)

    try:
        cmd = "PlayMedia(plugin://plugin.video.iptv.recorder/record_epg/%s/%s/%s/%s)" % (channel,
                                                                                        title,
                                                                                        start,
                                                                                        stop)
        xbmc.executebuiltin(cmd)

        message = "{}: {} ({} to {})'".format(xbmc.getInfoLabel("ListItem.ChannelName"), xbmc.getInfoLabel("ListItem.Label"), start, stop)
        xbmcgui.Dialog().notification("IPTV Recorder - Scheduled record", message, xbmcgui.NOTIFICATION_INFO, 10000, sound=False)
    except:
        xbmcgui.Dialog().notification("IPTV Recorder", "Could not schedule recording", xbmcgui.NOTIFICATION_WARNING)
except Exception as e:
    xbmcgui.Dialog().notification("IPTV Recorder", "Error parsing dates", xbmcgui.NOTIFICATION_ERROR)
    log("IPTV Recorder: Error parsing dates ({})".format(e))
