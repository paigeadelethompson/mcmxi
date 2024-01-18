import sopel
import requests
from sopel.tools import Identifier
from sopel.tools import SopelMemory
import re

#zfg - below can be removed after graduation
import streamlink
import cv2
import pytesseract
import datetime
#endzfg

ssthisregex = re.compile('.*\W(?:ss|screenshot) this.*')
def setup(bot):
    if not bot.memory.contains('url_callbacks'):
        bot.memory['url_callbacks'] = SopelMemory()
    bot.memory['url_callbacks'][ssthisregex] = ssthisirc

#@sopel.module.commands('testusers')
def testusers(bot, trigger):
        line = trigger.group(2)
        nicklist = []
        nicks = bot.channels[trigger.sender.lower()].users
        for nick in nicks:
                nicklist.append(nick)
        if any(word in line.split() for word in nicklist):
                bot.say("it matched :(")
        else:
                bot.say(line)

@sopel.module.commands('userquery')
def userquery(bot,trigger):
    person = trigger.group(2)
    nicklist = []
    nicks = bot.channels[trigger.sender.lower()].users
    for nick in nicks:
        nicklist.append(nick)
    if trigger.group(2) in nicklist:
        bot.say('ya')
    else:
        bot.say('nope')

@sopel.module.commands('wittest')
def wittest(bot,trigger):
    line = trigger.group(2)
    res = requests.get("https://api.wit.ai/message?v=20171003&q={}".format(requests.utils.quote(line)), headers = {'Authorization':''}).json() #requires wit.ai api key, and some training.
    try:
        x = res['entities']['datetime'][0]['value']
    except:
        x = res['entities']['datetime'][0]['to']['value']
    bot.say(x)

@sopel.module.rule('.*\W(?:ss|screenshot) this.*')
def ssthisirc(bot,trigger,match=None):
    match = match or trigger
    bot.say('you said ss this!!  content: {}'.format(trigger.group(0)))

@sopel.module.commands('lewd')
def lewd(bot,trigger):
    url = 'https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/analyze'
    headers = {'Ocp-Apim-Subscription-Key': ''} #requires microsoft computer vision api key
    params = {'visualFeatures':'Adult'}
    if trigger.group(2):
        data = {'url': trigger.group(2)}
        req = requests.post(url, headers=headers, params=params, json=data)
        js = req.json()
        if js['adult']['isAdultContent']:
            bot.say("[NSFW] wow lewd... lewd score: %.3f/1.00"%js['adult']['adultScore'])
        else:
            bot.say("phew safe... lewd score: %.3f/1.00"%js['adult']['adultScore'])

@sopel.module.commands('hostm')
def hostm(bot,trigger):
    bot.say(trigger.host)

@sopel.module.commands('zfg')
def zfg(bot, trigger):
    session = streamlink.Streamlink()
    session.set_plugin_option("twitch", "disable_hosting", True)
    session.set_plugin_option("twitch", "disable_ads", True)
    st = session.streams("https://twitch.tv/zfg1")
    if not st:
      return bot.say("zfg isn't streaming :(")
    s = st['best']
    fd = s.open()
    data = fd.read(int(5e6))
    fd.close()
    fname = '/home/desu/test/s.bin'
    open(fname, 'wb').write(data)
    capture = cv2.VideoCapture(fname)
    imgdata = capture.read()[1]
    i = imgdata[...,::-1]
    fc = cv2.cvtColor(i, cv2.COLOR_RGB2BGR)
    cv2.imwrite('/home/desu/htdocs/desu/zfg/captured_frame.png', fc)
    psplit_crop = fc[310:330, 270:330]
    cv2.imwrite('/home/desu/htdocs/desu/zfg/psplit_crop.png', psplit_crop)
    psplit_prep = cv2.cvtColor(psplit_crop, cv2.COLOR_BGR2GRAY)
    psplit_prep = cv2.threshold(psplit_prep, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    rows, cols = psplit_prep.shape
    psplit_r = cv2.resize(psplit_prep, (int(cols*4), int(rows*4)))
    psplit_string = pytesseract.image_to_string(psplit_r, config='-psm 7 -c tessedit_char_whitelist=.+-:0123456789').replace(" ","")
    if (psplit_string[0] != '-') and (psplit_string[0] != '+'):
        psplit_string = "\x0F-\x0F"
    timer_crop = fc[427:465, 179:331]
    cv2.imwrite('/home/desu/htdocs/desu/zfg/timer_crop.png', timer_crop)
    rows, cols,_ = timer_crop.shape
    tc_r = cv2.resize(timer_crop, (int(cols*4), int(rows*4)))
    timer_string = pytesseract.image_to_string(tc_r, config='-psm 7 -c tessedit_char_whitelist=.+-:0123456789').replace(" ","")
    if psplit_string != "\x0F-\x0F":
        try:
            psplit_td, psplitsign = parse_timer(psplit_string)
            timer_td, timersign = parse_timer(timer_string)
        except ValueError as err:
            now = datetime.datetime.now().isoformat()
            cv2.imwrite('/home/desu/htdocs/desu/zfg/errors/captured_frame_{}.png'.format(now), fc)
            cv2.imwrite('/home/desu/htdocs/desu/zfg/errors/psplit_crop_{}.png'.format(now), psplit_crop)
            cv2.imwrite('/home/desu/htdocs/desu/zfg/errors/psplit_r_{}.png'.format(now), psplit_r)
            cv2.imwrite('/home/desu/htdocs/desu/zfg/errors/timer_crop_{}.png'.format(now), timer_crop)
            cv2.imwrite('/home/desu/htdocs/desu/zfg/errors/tc_r_{}.png'.format(now), tc_r)
            return bot.say("Timer parsing error, error:{} ... try again in a bit. https://dasu.moe/desu/zfg/".format(err))
        dampe = datetime.timedelta(hours=1, minutes=45, seconds=0)
        ttd_s = (timer_td.total_seconds() - (dampe.total_seconds() - psplit_td.total_seconds())) if not psplitsign else (timer_td.total_seconds() - (dampe.total_seconds() + psplit_td.total_seconds()))
        ttd = secondstotimer(ttd_s)
        if not ttd.startswith('-'):
            ttd = "Already passed"
    else:
        ttd = "-1:45:00" #just show this for the first 12~ minutes of a run
    bot.say("Time: {} ({} PB) | Est. time to Dampe: {} | Images: https://dasu.moe/desu/zfg/ | https://twitch.tv/zfg1 ".format(timer_string, "\x0303"+psplit_string.replace(' ','')+"\x0F" if psplit_string.startswith('-') else "\x0304"+psplit_string.replace(' ','')+"\x0F" , ttd))

def parse_timer(time):
    time = time.strip()
    if time.startswith('-'):
        sign = False
    elif time.startswith('+'):
        sign = True
    else:
        sign = None
    if sign is not None:
        time = time[1:]
    if ":" in time:
        if time.count(':') == 2:
            ptime = datetime.datetime.strptime(time, "%H:%M:%S{}".format(".%f" if sign == None else ""))
            tdtime = datetime.timedelta(hours=ptime.hour, minutes=ptime.minute, seconds=ptime.second, microseconds=ptime.microsecond)
        else:
            ptime = datetime.datetime.strptime(time, "%M:%S{}".format(".%f" if sign == None else  ""))
            tdtime = datetime.timedelta(minutes=ptime.minute, seconds=ptime.second, microseconds=ptime.microsecond)
    else:
        ptime = datetime.datetime.strptime(time, "%S.%f")
        tdtime = datetime.timedelta(seconds=ptime.second, microseconds=ptime.microsecond)
    return tdtime, sign

def secondstotimer(seconds):
    if seconds < 0:
        negative = True
    else:
        negative = False
    timer = str(datetime.timedelta(seconds=int(abs(seconds))))
    if negative:
        return "-{}".format(timer)
    else:
        return "{}".format(timer)
