# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib2

def getSoup(url):
    if url.startswith('/'):
        url = 'http://www.kongregate.com' + url
    print url
    content = urllib2.urlopen(url).read()
    # print content
    content = content[content.find('<body') : content.find('</body>') + 7]
    soup = BeautifulSoup(content.decode('utf-8'))
    return soup

def purify(s):
    if type(s) is not unicode and type(s) is not str:
        s = str(s)
    s = s.replace('\r', ' ').replace('\n', ' ').strip()
    if type(s) is unicode:
        return s.encode('utf-8')
    else:
        return s

url = "http://www.kongregate.com/accounts/CAQ9/points"
mycount = 0

filename = 'pointhistory.txt'
fw = open(filename, 'w')
fw.write('Page Url\t#\tDate\tPoints\tReward Description\tGame Link\tBadge Image\tGame\tImage Title\tReward Subject\tSpan\n')
fw.close()

while url is not None:
    soup = getSoup(url)
    body = soup.body

    fw = open('pointhistory.txt', 'a')

    ## parse history table
    table = body.findAll('table', {'class':'rewards'}, limit=1)[0]
    for tr in table.findAll('tr'):
        if tr.has_key('class') and 'summary' in tr['class']:
            continue
        tds = tr.findAll('td')
        if tds is None or len(tds) == 0:
            continue
        date = tds[0].get_text()
        if date is None:
            date = ""
        points = tds[1].get_text()
        if points is None:
            points = ""

        description = tds[2]
        ## parse description
        ##   reward_description: text of the description
        reward_description = ""
        ##   game_link: link of the game
        game_link = ""
        ##   badge_img: src (url) of the badge image
        badge_img = ""
        ##   game: title (text) of the game
        game = ""
        ##   imgtitle = name of the badge
        imgtitle = ""
        ##   reward_subject: text of the subject
        reward_subject = ""
        ##   wholespan: all the spans
        wholespan = ""

        spans = description.findAll('span')
        reward_description = spans[0].get_text()
        if reward_description == 'Acquired badge' or reward_description == 'Acquired badge of the day':
            game_link = spans[1].a['href']
            img = spans[1].a.div.div.img
            badge_img = img['src']
            game = img['game']
            imgtitle = img['title']
        elif reward_description == 'Completed achievement' or reward_description == 'Completed challenge':
            reward_subject = spans[1].get_text()
        elif reward_description == 'Acquired card':
            reward_subject = "".join([str(x) for x in spans[1].children])
        elif reward_description == 'Rated game':
            game = spans[1].a.get_text()
            game_link = spans[1].a['href']
        else:
            if len(spans) > 1:
                reward_subject = "".join([x.encode('utf-8') for x in spans[1].children])
            if len(spans) > 2:
                wholespan = "".join([str(x) for x in spans[2:]])

        date = purify(date)
        points = purify(points)
        reward_description = purify(reward_description)
        game_link = purify(game_link)
        badge_img = purify(badge_img)
        game = purify(game)
        imgtitle = purify(imgtitle)
        #for c in reward_subject:
        #    print ord(c), hex(ord(c)), c
        reward_subject = purify(reward_subject)
        wholespan = purify(wholespan)

        try:
            fw.write(url + '\t' + str(mycount) + '\t' + date + '\t' + points + '\t')
            fw.write(reward_description + '\t' + game_link + '\t' + badge_img + '\t')
            fw.write(game + '\t' + imgtitle + '\t')
            fw.write(reward_subject + '\t')
            fw.write(wholespan + '\n')
        except:
            spanstr = purify(spans)
            #print type(wholespan), type(spanstr)
            #raise
            #print url, spanstr
            #for c in spanstr[230:]:
            #    print ord(c), hex(ord(c)), '\'', c, '\''
            fw.write(url + '\t' + str(mycount) + '\t' + date + '\t' + points + '\t' + reward_description + '\t' + game_link + '\t' + badge_img + '\t' + 'game\timgtitle\treward_subject\twholespan:')
            fw.write(spanstr + '\n')

        mycount += 1

    fw.close()

    ## get next page link
    pagination = body.findAll('ul', {'class':'pagination simple_pagination'}, limit=1)[0]
    nextpagelink = pagination.findAll('li', {'class':'next'}, limit=1)[0]
    url = nextpagelink.a
    if url is not None:
        url = url['href']

    #break
