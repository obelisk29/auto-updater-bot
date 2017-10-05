import praw
import pytz
import json
import getpass
import requests
import HTMLParser
from time import sleep
from datetime import datetime
 
class Auto_Updater_Bot(object):
    def __init__(self):
        self.ruser = raw_input('Username: ')
        self.rpass = getpass.getpass(prompt='Password (will not be visible): ')
        self.userAgent = 'Updating GDTs for /r/hockey'
 
        self.teams = {'VGK': ['/r/goldenknights', 'Vegas', 'Golden Knights'], 
			'MIN': ['/r/wildhockey', 'Minnesota', 'Wild'], 
			'TOR': ['/r/leafs', 'Toronto', 'Leafs'], 
			'WSH': ['/r/caps', 'Washington', 'Capitals'], 
			'BOS': ['/r/bostonbruins', 'Boston', 'Bruins'], 
			'DET': ['/r/detroitredwings', 'Detroit', 'Red Wings'], 
			'NYI': ['/r/newyorkislanders', 'New York', 'Islanders'], 
			'FLA': ['/r/floridapanthers', 'Florida', 'Panthers'], 
			'COL': ['/r/coloradoavalanche', 'Colorado', 'Avalanche'], 
			'NSH': ['/r/predators', 'Nashville', 'Predators'], 
			'CHI': ['/r/hawks', 'Chicago', 'Blackhawks'], 
			'NJD': ['/r/devils', 'New Jersey', 'Devils'], 
			'DAL': ['/r/dallasstars', 'Dallas', 'Stars'], 
			'CGY': ['/r/calgaryflames', 'Calgary', 'Flames'], 
			'NYR': ['/r/rangers', 'New York', 'Rangers'], 
			'CAR': ['/r/canes', 'Carolina', 'Hurricanes'], 
			'WPG': ['/r/winnipegjets', 'Winnipeg', 'Jets'], 
			'BUF': ['/r/sabres', 'Buffalo', 'Sabres'], 
			'VAN': ['/r/canucks', 'Vancouver', 'Canucks'], 
			'STL': ['/r/stlouisblues', 'St Louis', 'Blues'], 
			'SJS': ['/r/sanjosesharks', 'San Jose', 'Sharks'], 
			'MTL': ['/r/habs', 'Montreal', 'Canadiens'], 
			'PHI': ['/r/flyers', 'Philadelphia', 'Flyers'], 
			'ANA': ['/r/anaheimducks', 'Anaheim', 'Ducks'], 
			'LAK': ['/r/losangeleskings', 'Los Angeles', 'Kings'], 
			'CBJ': ['/r/bluejackets', 'Columbus', 'Blue Jackets'], 
			'PIT': ['/r/penguins', 'Pittsburgh', 'Penguins'], 
			'EDM': ['/r/edmontonoilers', 'Edmonton', 'Oilers'], 
			'TBL': ['/r/tampabaylightning', 'Tampa Bay', 'Lightning'], 
			'ARI': ['/r/coyotes', 'Arizona', 'Coyotes'], 
			'OTT': ['/r/ottawasenators', 'Ottawa', 'Senators']}
        self.convert = {'Vegas Golden Knights': 'VGK', 
			'San Jose Sharks': 'SJS', 
			'Detroit Red Wings': 'DET', 
			'Arizona Coyotes': 'ARI', 
			'Carolina Hurricanes': 'CAR', 
			'Toronto Maple Leafs': 'TOR', 
			'Boston Bruins': 'BOS', 
			'Florida Panthers': 'FLA', 
			'Columbus Blue Jackets': 'CBJ', 
			'Anaheim Ducks': 'ANA', 
			'Buffalo Sabres': 'BUF', 
			'Montreal Canadiens': 'MTL', 
			'Edmonton Oilers': 'EDM', 
			'Pittsburgh Penguins': 'PIT', 
			'New York Rangers': 'NYR', 
			'Washington Capitals': 'WSH', 
			'St Louis Blues': 'STL', 
			'Colorado Avalanche': 'COL', 
			'Minnesota Wild': 'MIN', 
			'Dallas Stars': 'DAL', 
			'Winnipeg Jets': 'WPG', 
			'New Jersey Devils': 'NJD', 
			'Tampa Bay Lightning': 'TBL', 
			'Los Angeles Kings': 'LAK', 
			'Calgary Flames': 'CGY', 
			'Chicago Blackhawks': 'CHI', 
			'New York Islanders': 'NYI', 
			'Nashville Predators': 'NSH', 
			'Ottawa Senators': 'OTT', 
			'Vancouver Canucks': 'VAN', 
			'Philadelphia Flyers': 'PHI'}
 
        self.utc = pytz.timezone('UTC')
        self.pacific = pytz.timezone('US/Pacific')
 
        self.gameThread = {}
        self.final = False
 
    def scrape_games(self):
        today = datetime.now(self.pacific).strftime('%Y-%m-%d')
        url = 'https://statsapi.web.nhl.com/api/v1/schedule?startDate='+today+'&endDate='+today+'&expand=schedule.teams,schedule.linescore'
        w = requests.get(url)
        data = json.loads(w.content)['dates'][0]['games']
        w.close()
 
        games = {}
        z = 1
        for x in data[:]:
            games[z] = {'a':x['teams']['away']['team']['abbreviation'],'h':x['teams']['home']['team']['abbreviation'],'id':x['gamePk']}
            if x['linescore']['currentPeriod'] == 0:
                games[z]['time'] = 'Pre-game'
            elif x['linescore']['currentPeriodTimeRemaining'] == 'FINAL':
                games[z]['time'] = 'Finished'
            else:
                games[z]['time'] = x['linescore']['currentPeriodOrdinal']+' '+x['linescore']['currentPeriodTimeRemaining']
            z += 1
 
        for x in sorted(games.keys()):
            print '{0}. {1} at {2} - {3}'.format(x,games[x]['a'],games[x]['h'],games[x]['time'])
 
        response = raw_input('Please enter the number of the game you need: ')
        valid = False
        while not valid:
            try:
                self.gameThread = games[int(response)]
            except Exception as e:
                response = raw_input('Invalid input, please enter the number of the game you need: ')
            else:
                valid = True
 
    def find_gdt(self,game):
        search = raw_input('Have you already posted the GDT? (y/n) ')
        if search.lower() == 'y':
            user = r.get_redditor(self.ruser)
            posts = [x for x in user.get_submitted(limit=100)]
 
            game_check = {}
            for x in posts[:]:
                made = self.utc.localize(datetime.utcfromtimestamp(x.created_utc)).astimezone(self.pacific)
                if (made.strftime('%d%m%Y') == datetime.now(self.pacific).strftime('%d%m%Y')) and (x.subreddit.display_name.lower() == 'hockey'):
                    team_lst = [self.teams[self.gameThread['a']][1],self.teams[self.gameThread['a']][2],self.teams[self.gameThread['h']][1],self.teams[self.gameThread['h']][2]]
                    check = sum(bool(y) for y in [team_lst[0].lower() in x.title.lower(), team_lst[1].lower() in x.title.lower(), team_lst[2].lower() in x.title.lower(), team_lst[3].lower() in x.title.lower()])
                    if check > 0:
                        game_check[x] = check
            print game_check
            game_check_sorted = sorted(game_check.items(), key=lambda x:x[1], reverse=True)
            if len(game_check_sorted) == 0:
                search = 'n'
                print 'GDT not found.'
                print search
            else:
                self.gameThread['thread'] = game_check_sorted[0][0]
                print 'GDT found: '+self.gameThread['thread'].title
        if search.lower() == 'n':
            thread = raw_input('GDT URL? ')
            self.gameThread['thread'] = r.get_submission(thread)
 
    def update_gdt(self, game):
        url = 'https://statsapi.web.nhl.com/api/v1/game/'+str(self.gameThread['id'])+'/feed/live'
        w = requests.get(url)
        data = json.loads(w.content)
        w.close()
 
        period = data['liveData']['linescore']['currentPeriod']
        if period == 0:
            print 'No updates'
            time = 'Pre-game'
        else:
            time = data['liveData']['linescore']['currentPeriodTimeRemaining']
            ordinal = data['liveData']['linescore']['currentPeriodOrdinal']
            if ordinal+' '+time == self.gameThread['time']:
                print 'No updates'
            else:
                self.gameThread['time'] = ordinal+' '+time
#Time Table
                print 'Creating time table...'
                if time == 'FINAL':
                    timeTable = '|Time Clock|\n|:--:|\n|FINAL|\n\n'
                else:
                    timeTable = '|Time Clock|\n|:--:|\n|{0} - {1}|\n\n'.format(ordinal, time)
 
                homeTeam = self.teams[data['gameData']['teams']['home']['abbreviation']][0]
                awayTeam = self.teams[data['gameData']['teams']['away']['abbreviation']][0]
#Boxscore
                print 'Creating boxscore...'
                boxscore = '|Teams|1st|2nd|3rd|'
 
                if data['gameData']['game']['type'] == 'R':
                    if period == 4:
                        boxscore += 'OT|Total|\n|:--:|:--:|:--:|:--:|:--:|:--:|\n'
                    elif period == 5:
                        boxscore += 'OT|SO|Total|\n|:--:|:--:|:--:|:--:|:--:|:--:|:--:|\n'
                    else:
                        boxscore += 'Total|\n|:--:|:--:|:--:|:--:|:--:|\n'
                elif data['gameData']['game']['type'] == 'P':
                    for x in range(0,(period-3)):
                        boxscore += 'OT{0}|'.format(x+1)
                    boxscore += 'Total|\n|:--:|:--:|:--:|:--:|'
                    for x in range(0,period-3):
                        boxscore += ':--:|'
                    boxscore += ':--:|\n'
 
                homeTotal = data['liveData']['linescore']['teams']['home']['goals']
                awayTotal = data['liveData']['linescore']['teams']['away']['goals']
 
                scoreDict = {}
 
                OT = 1
                for x in data['liveData']['linescore']['periods']:
                    score = [x['away']['goals'],x['home']['goals']]
                    if (data['gameData']['game']['type'] == 'P') and ('OT' in x['ordinalNum']) and (period > 4):
                        scoreDict['OT'+str(OT)] = score
                        OT += 1
                    else:
                        scoreDict[x['ordinalNum']] = score
 
                if period == 1:
                    scoreDict['2nd'] = ['--','--']
                    scoreDict['3rd'] = ['--','--']
                elif period == 2:
                    scoreDict['3rd'] = ['--','--']
 
                if data['liveData']['linescore']['hasShootout']:
                    awaySO = data['liveData']['linescore']['shootoutInfo']['away']['scores']
                    homeSO = data['liveData']['linescore']['shootoutInfo']['home']['scores']
                    if awaySO > homeSO:
                        scoreDict['SO'] = [1, 0]
                    else:
                        scoreDict['SO'] = [0, 1]
 
                boxscore += '|[]({0})|'.format(awayTeam)
                for x in sorted(scoreDict.keys()):
                    boxscore += '{0}|'.format(scoreDict[x][0])
           
                boxscore += '{0}|\n|[]({1})|'.format(awayTotal,homeTeam)
                for x in sorted(scoreDict.keys()):
                    boxscore += '{0}|'.format(scoreDict[x][1])
           
                boxscore += '{0}|\n\n'.format(homeTotal)
#Team Stats
                print 'Creating team stats...'
                homeStats = data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']
                awayStats = data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']
 
                teamStats = '|Team|Shots|Hits|Blocked|FO Wins|Giveaways|Takeaways|Power Plays|\n|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|\n'
                teamStats += '|[]({0})|{1}|{2}|{3}|{4}%|{5}|{6}|{7}/{8}|\n'.format(awayTeam,awayStats['shots'],awayStats['hits'],awayStats['blocked'],awayStats['faceOffWinPercentage'],awayStats['giveaways'],awayStats['takeaways'],str(int(awayStats['powerPlayGoals'])),str(int(awayStats['powerPlayOpportunities'])))
                teamStats += '|[]({0})|{1}|{2}|{3}|{4}%|{5}|{6}|{7}/{8}|\n\n'.format(homeTeam,homeStats['shots'],homeStats['hits'],homeStats['blocked'],homeStats['faceOffWinPercentage'],homeStats['giveaways'],homeStats['takeaways'],str(int(homeStats['powerPlayGoals'])),str(int(homeStats['powerPlayOpportunities'])))
#Goals
                print 'Creating goal table...'
                allPlays = data['liveData']['plays']['allPlays']
                scoringPlays = data['liveData']['plays']['scoringPlays']
 
                goalDict = {'1st':[],'2nd':[],'3rd':[],'OT':[]}
 
                if (data['gameData']['game']['type'] == 'R') and (period == 5):
                    goalDict['SO'] = []
                if (data['gameData']['game']['type'] == 'P') and (period > 4):
                    del goalDict['OT']
                    for x in range(0,(period-4)):
                        goalDict['OT'+str(x+1)] = []
               
                OT = 1
                for x in scoringPlays:
                    goal = allPlays[x]
                    if (data['gameData']['game']['type'] == 'P') and ('OT' in goal['about']['ordinalNum']) and (period > 4):
                        goalDict['OT'+str(OT)].append([goal['about']['periodTime'],self.teams[self.convert[goal['team']['name'].replace(u'\xe9','e').replace('.','')]][0],goal['result']['strength']['name'],goal['result']['description'].replace(u'\xe9','e')])
                        OT += 1
                    else:
                        goalDict[goal['about']['ordinalNum']].append([goal['about']['periodTime'],self.teams[self.convert[goal['team']['name'].replace(u'\xe9','e').replace('.','')]][0],goal['result']['strength']['name'],goal['result']['description'].replace(u'\xe9','e')])
               
                goalTable = '|Period|Time|Team|Strength|Description|\n|:--:|:--:|:--:|:--:|:--:|\n'
                #Reverse for GDT and forward for PGT
                for x in sorted(goalDict.keys(),reverse=True):
                    for y in goalDict[x][::-1]:
                        if x == 'SO':
                            goalTable += '|{0}|{1}|[]({2})|---|{3}|\n'.format(x,y[0],y[1],y[3])
                        else:
                            goalTable += '|{0}|{1}|[]({2})|{3}|{4}|\n'.format(x,y[0],y[1],y[2],y[3])
 
                goalTable += '\n\n'
#Penalties
                print 'Creating penalty table...'
                penaltyPlays = data['liveData']['plays']['penaltyPlays']
 
                penaltyDict = {'1st':[],'2nd':[],'3rd':[],'OT':[]}
       
                if (data['gameData']['game']['type'] == 'P') and (period > 4):
                    del penaltyDict['OT']
                    for x in range(0,(period-4)):
                        penaltyDict['OT'+str(x+1)] = []
 
                OT = 1
                for x in penaltyPlays:
                    penalty = allPlays[x]
                    if (data['gameData']['game']['type'] == 'P') and ('OT' in penalty['about']['ordinalNum']) and (period > 4):
                        penaltyDict['OT'+str(OT)].append([penalty['about']['periodTime'],self.teams[self.convert[penalty['team']['name'].replace(u'\xe9','e').replace('.','')]][0],penalty['result']['penaltySeverity'],penalty['result']['penaltyMinutes'],penalty['result']['description'].replace(u'\xe9','e')])
                    else:
                        penaltyDict[penalty['about']['ordinalNum']].append([penalty['about']['periodTime'],self.teams[self.convert[penalty['team']['name'].replace(u'\xe9','e').replace('.','')]][0],penalty['result']['penaltySeverity'],penalty['result']['penaltyMinutes'],penalty['result']['description'].replace(u'\xe9','e')])
 
                penaltyTable = '|Period|Time|Team|Type|Min|Description|\n|:--:|:--:|:-:|:--:|:--:|:--:|\n'
                #Reverse for GDT and forward for PGT
                for x in sorted(penaltyDict.keys(),reverse=True):
                    for y in penaltyDict[x][::-1]:
                        penaltyTable += '|{0}|{1}|[]({2})|{3}|{4}|{5}|\n'.format(x,y[0],y[1],y[2],y[3],y[4])
 
                penaltyTable += '\n\n'
 
                tables = '***\n\n'+timeTable+boxscore+goalTable+penaltyTable+'***'
 
                now = datetime.now()
                print now.strftime('%I:%M%p')+' - Updating thread...'
                h = HTMLParser.HTMLParser()
                op = self.gameThread['thread'].selftext.split('***')
                self.gameThread['thread'] = self.gameThread['thread'].edit(h.unescape(op[0]+tables+op[2]))
 
        if time == 'FINAL':
            self.final = True
            close = raw_input('Game over, hit enter/return to exit.')
        else:
            print 'Sleeping...\n\n'
            sleep(60)
 
    def run(self):
        try:
            self.scrape_games()
            self.find_gdt(self.gameThread)
            while not self.final:
                self.update_gdt(self.gameThread)
        except Exception as e:
            print e
 
AUB = Auto_Updater_Bot()
 
r = praw.Reddit(AUB.userAgent)
r.login(AUB.ruser,AUB.rpass,disable_warning=True)
 
AUB.run()
