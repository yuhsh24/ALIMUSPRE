# -*- coding: utf-8 -*-

import time
import numpy as np
import csv
import matplotlib.pyplot as plt

import os
import sys

path = os.getcwd()
parent_path = os.path.dirname(path)
sys.path.append(parent_path)

CURRENT_PATH = sys.path[0]#获取当前的路径
ARTIST_FOLDER = os.path.join(CURRENT_PATH,'pic','artist')
ARTIST = os.path.join(CURRENT_PATH, "mars_tianchi_songs.csv")#该文件记录了每首歌对应的艺人
SONGS = os.path.join(CURRENT_PATH, "mars_tianchi_user_actions.csv")#该文件记录了每个用户对不同歌曲的操作
SONG_P_D_C = os.path.join(CURRENT_PATH, "song_p_d_c.txt")#记录每首歌每日的播放量,下载量以及收藏量的数目
ARTIST_P_D_C = os.path.join(CURRENT_PATH, "artist_p_d_c.txt")#记录每天该艺人的播放量,下载量以及收藏量的数目
SONG_FAN = os.path.join(CURRENT_PATH, "song_fan.txt")#记录每天听对应歌曲的不同用户数目
ARTIST_FAN = os.path.join(CURRENT_PATH, "artist_fan.txt")#记录每天听该艺人的不同用户数目
DAYS = 183 #一共记录的天数
START_UNIX = 1425139200#表示20150301
DAY_SECOND = 86400#每天的秒数
START_WEEK = 7

def date2Num(date):
    return (int(time.mktime(time.strptime(date, "%Y%m%d")))-START_UNIX)//DAY_SECOND

def IfNoSongTXT():
    user = {}
    songs = {}
    with open(SONGS) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=",")
        for row in spamreader:
            if row[1] not in songs:#当前行的这首歌并没有出现
                songs[row[1]] = [[0 for j in range(DAYS)] for j in range(3)]#用于保存播放,下载，收藏
            songs[row[1]][int(row[3])-1][date2Num(row[4])] +=1#记录当天的行为

            if row[3] == "1":#1表示播放
                if row[1] not in user:
                    user[row[1]] = [{} for j in range(DAYS)]
                user[row[1]][date2Num(row[4])][row[0]] = True#表示该首歌在当前日被该用户播放

    with open(SONG_P_D_C, "w") as fw:
        for i in songs:
            fw.write(i+"\n")
            fw.write(",".join(str(x) for x in songs[i][0])+"\n")#将每日的播放数目记录
            fw.write(",".join(str(x) for x in songs[i][1])+"\n")#将每日的下载数目记录
            fw.write(",".join(str(x) for x in songs[i][2])+"\n")#将每日的收藏数目记录

    with open(SONG_FAN, "w") as fw:
        for i in user:
            fw.write(i+"\n")
            fw.write(",".join(str(len(x)) for x in user[i])+"\n")#将每日播放该首歌的用户数目记录

def IfNoArtistTXT():
    user = {}
    artist = {}
    index = {}
    with open(ARTIST) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=",")
        for row in spamreader:
            index[row[0]] = row[1]#记录该歌曲对应的artist
            if row[1] not in artist:#该艺人从没出现
                artist[row[1]] = [[0 for j in range(DAYS)] for j in range(3)]
                user[row[1]] = [{} for j in range(DAYS)]

    with open(SONG_P_D_C, "r") as fr:
        songs_id = fr.readline().strip("\n")
        while songs_id:
            temp = []
            play = list(map(int, fr.readline().strip("\n").split(",")))#获得该首歌每天的播放量
            download = list(map(int, fr.readline().strip("\n").split(",")))#获得该首歌每天的下载量
            collect = list(map(int, fr.readline().strip("\n").split(",")))#获得该首歌每天的收藏量
            temp.append(play)
            temp.append(download)
            temp.append(collect)
            t = artist[index[songs_id]]#获得该艺人之前的数据
            #累加数值
            for i in range(3):
                for j in range(DAYS):
                    t[i][j] += temp[i][j]
            artist[index[songs_id]] = t
            songs_id = fr.readline().strip("\n")

    with open(ARTIST_P_D_C, "w") as fw:
        for i in artist:
            fw.write(i+"\n")
            fw.write(",".join(str(x) for x in artist[i][0])+"\n")#记录每天的播放量
            fw.write(",".join(str(x) for x in artist[i][1])+"\n")#记录每天的下载量
            fw.write(",".join(str(x) for x in artist[i][2])+"\n")#记录每天的收藏量

    with open(SONGS) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=",")
        for row in spamreader:
            if row[1] in index:
                user[index[row[1]]][date2Num(row[4])][row[0]] = True

    with open(ARTIST_FAN, "w") as fw:
        for i in user:
            fw.write(i+"\n")
            fw.write(",".join(str(len(x)) for x in user[i])+"\n")#记录每天该有多少用户选择播放

#定义艺人的成员类
class Artist(object):
    songPlayFolder = ""
    songFanFolder = ""
    artistID = ""
    fPath = ""
    #私有方法,__表示该方法是私有的,init函数在实例化对象时使用
    def __init__(self, artist_id):
        self.artistID = artist_id
        self.fPath = os.path.join(ARTIST_FOLDER, self.artistID)
        if not os.path.exists(self.fPath):
            os.mkdir(self.fPath)
        self.songPlayFolder = os.path.join(self.fPath, "song_play")
        self.songFanFolder = os.path.join(self.fPath, "song_fan")
        if not os.path.exists(self.songPlayFolder):
            os.mkdir(self.songPlayFolder)
        if not os.path.exists(self.songFanFolder):
            os.mkdir(self.songFanFolder)
    #画出特定艺人的播放数,下载量以及收藏量随时间的变化
    def PlotArtistPlay(self):
        ylabel = "count"
        xlabel = "days"
        with open(ARTIST_P_D_C, "r") as fr:
            artistID = fr.readline().strip("\n")
            while artistID:
                play = list(map(int, fr.readline().strip("\n").split(",")))
                download = list(map(int, fr.readline().strip("\n").split(",")))
                collect = list(map(int, fr.readline().strip("\n").split(",")))
                if artistID == self.artistID:
                    play = np.array(play)
                    mu = np.mean(play)
                    sigma = np.sqrt((play * play).sum()/DAYS - mu*mu)
                    p = plt.plot(play, "bo", play, "b-", marker="o")
                    d = plt.plot(download, "ro", download, "r-", marker="o")
                    c = plt.plot(collect, "go", collect, "g-", marker="o")
                    plt.legend([p[1], d[1], c[1]], ["play", "download", "collect"])
                    plt.title("".join(("mu=", str(mu), ",", "sigma=", str(sigma))))
                    plt.xlabel(xlabel)
                    plt.ylabel(ylabel)
                    plt.savefig(os.path.join(self.fPath, "play.png"))
                    plt.clf()
                    break
                artistID = fr.readline().strip("\n")
    #画出特定艺人的粉丝数
    def PlotArtistFan(self):
        ylabel = "count"
        xlabel = "days"
        with open(ARTIST_FAN, "r") as fr:
            artistID = fr.readline().strip("\n")
            while artistID:
                fan = list(map(int, fr.readline().strip("\n").split(",")))
                if artistID == self.artistID:
                    fan = np.array(fan)
                    mu = np.mean(fan)
                    sigma = np.sqrt((fan*fan).sum()/DAYS-mu*mu)
                    f = plt.plot(fan, "bo", fan, "b-", marker="o")
                    plt.xlabel(xlabel)
                    plt.ylabel(ylabel)
                    plt.legend([f[1]], ["artist fans"])
                    plt.title("".join(("mu=", str(mu), ",", "sigma=", str(sigma))))
                    plt.savefig(os.path.join(self.fPath, "fan.png"))
                    plt.clf()
                    break
                artistID = fr.readline().strip("\n")
    #画出该艺人每首歌每日的播放量
    def PlotSongPlay(self):
        ylabel = "count"
        xlabel = "days"
        songs = self.GetSongsListByArtistID()
        with open(SONG_P_D_C) as fr:
            songsID = fr.readline().strip("\n")
            while songsID:
                play = list(map(int, fr.readline().strip("\n").split(",")))
                download = list(map(int, fr.readline().strip("\n").split(",")))
                collect = list(map(int, fr.readline().strip("\n").split(",")))
                if songsID in songs:
                    play = np.array(play)
                    mu = np.mean(play)
                    sigma = np.sqrt((play*play).sum()/DAYS-mu*mu)
                    p = plt.plot(play, "bo", play, "b-", marker="o")
                    d = plt.plot(download, "ro", download, "r-", marker="o")
                    c = plt.plot(collect, "go", collect, "g-", marker="o")
                    plt.legend([p[1], d[1], c[1]], ["play", "download", "collect"])
                    plt.title("".join(("mu=", str(mu), ",", "sigma=", str(sigma))))
                    plt.xlabel(xlabel)
                    plt.ylabel(ylabel)
                    plt.savefig(os.path.join(self.songPlayFolder, songsID+".png"))
                    plt.clf()
                songsID = fr.readline().strip("\n")
    #画出特定艺人的每首歌曲的粉丝数量
    def PlotSongFan(self):
        ylabel = "count"
        xlabel = "days"
        songs = self.GetSongsListByArtistID()
        with open(SONG_FAN) as fr:
            songsID = fr.readline().strip("\n")
            while songsID:
                fan = list(map(int, fr.readline().strip("\n").split(",")))
                if songsID in songs:
                    fan = np.array(fan)
                    mu = np.mean(fan)
                    sigma = np.sqrt((fan*fan).sum()/DAYS-mu*mu)
                    f = plt.plot(fan, "bo", fan, "b-", marker="o")
                    plt.xlabel(xlabel)
                    plt.ylabel(ylabel)
                    plt.title("".join(("mu=", str(mu), ",", "sigma=", str(sigma))))
                    plt.legend([f[1]], ["fans"])
                    plt.savefig(os.path.join(self.songFanFolder, songsID+".png"))
                    plt.clf()
                songsID = fr.readline().strip("\n")
    #获取该艺人的所有歌的歌名
    def GetSongsListByArtistID(self):
        songs = {}
        with open(ARTIST) as csvfile:
            spamreader = csv.reader(csvfile, delimiter=",")
            for row in spamreader:
                if row[1]==self.artistID:
                    songs[row[0]] = True
        return songs

if __name__ == "__main__":
    #IfNoSongTXT()
    #IfNoArtistTXT()
    a = Artist("0c80008b0a28d356026f4b1097041689")
    a.PlotArtistPlay()
    a.PlotArtistFan()
    a.PlotSongPlay()
    a.PlotSongFan()











