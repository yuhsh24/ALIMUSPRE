# -*- coding: utf-8 -*-

import os
import sys
import numpy as np
from sklearn import linear_model
import csv
import time
import math
from sklearn.ensemble import RandomForestRegressor

CURRENT_PATH = sys.path[0]#获取当前路径
ARTIST_P_D_C = os.path.join(CURRENT_PATH, "artist_p_d_c.txt")
DAYS = 183
START_UNIX = 1425139200#表示20150301
DAY_SECOND = 86400#每天的秒数
START_WEEKDAY = 7#表示是一周的第几天
HOLIDAY = ["20150405", "20150406", "20150501", "20150502", "20150503", ...
           , "20150620", "20150621", "20150622", "20150927", "20151001", ...
           , "20151002", "20151003", "20151004", "20151005", "20151006", ...
           , "20151007"]
HOLIDAYCHANGE = ["20151010"]

#线性预测函数
def LinearPrediction(train_X, train_y, predict_x):
    regr = linear_model.Ridge(alpha=.05, fit_intercept=False)
    regr.fit(train_X, train_y)
    initial_y = regr.predict(predict_x)
    prediction_y = []#返回的整数预测值
    for i in range(len(initial_y)):
        prediction_y.append(max(1, int(initial_y[i])))
    return prediction_y

#随机森林预测
def RandomForestPrediction(train_x, train_y, predict_x):
    rf = RandomForestRegressor()
    rf.fit(train_x, train_y)
    initial_y = rf.predict(predict_x)
    prediction_y = []#返回的整数预测值
    for i in range(len(initial_y)):
        prediction_y.append(max(1, int(initial_y[i])))
    return prediction_y

#写入预测的结果
def WriteResult(artistID, predict_file_path, prediction_y):
    headers = ["ID", "Play", "Date"]
    with open(predict_file_path, "a") as f:
        f_csv = csv.DictWriter(f, headers)
        for i in range(1, 61):
            unixTime = START_UNIX+(DAYS+i)*DAY_SECOND
            date = Unix2Date(unixTime)
            f_csv.writerows([{headers[0]: artistID, headers[1]: prediction_y[i], headers[2]: date}])

def WriteF1Score(file_path, Score):
    headers = ["SCORE"]
    with open(file_path, "a") as f:
        f_csv = csv.DictWriter(f, headers)
        for score in Score:
           f_csv.writerows([{headers[0]: score}])

#实现unix时间转换为如20150901的日期
def Unix2Date(unixTime):
    dt = time.localtime(unixTime)
    date = time.strftime("%Y%m%d", dt)
    return date

#返回一周的第几日
def Num2WeekDay(day):
    weekDay = (START_WEEKDAY+day)%7
    if weekDay == 0:
        return 7
    return weekDay

#计算F1Score
#realPlayData每一个元素代表的是一名歌手的实际播放数据
#predictPlayData每一个元素代表的是一个歌手的预测播放数据
def CalculateF1Score(realPlayData, predictPlayData):
    F1Score = 0
    for i in range(len(realPlayData)):
        sigma = 0
        theta = 0
        for j in range(len(realPlayData[i])):
            if realPlayData[i][j] == 0:
                continue
            sigma += ((predictPlayData[i][j]-realPlayData[i][j])/realPlayData[i][j])**2
            theta += realPlayData[i][j]
        sigma = math.sqrt(sigma/len(realPlayData[i]))
        theta = math.sqrt(theta)
        F1Score += (1-sigma)*theta
    return F1Score

def Unix2Day(unixTime):
    dt = time.localtime(unixTime)
    date = time.strftime("%d", dt)
    return date

def MakeFeature(day):
    feature = []
    #feature.append(day)
    #日期特征
    weekDay = Num2WeekDay(day)
    for i in range(1, 8):
        if i == weekDay:
            feature.append(1)
        else:
            feature.append(0)
    '''
    unixTime = START_UNIX+day*DAY_SECOND
    day = Unix2Day(unixTime)
    day = int(day)
    if day <= 10:
        feature.append(1)
        feature.append(0)
        feature.append(0)
    elif day <= 20:
        feature.append(0)
        feature.append(1)
        feature.append(0)
    else:
        feature.append(0)
        feature.append(0)
        feature.append(1)
    '''
    '''
    #是否法定假日
    unixTime = START_UNIX+day*DAY_SECOND
    date = Unix2Date(unixTime)
    if date in HOLIDAY:
        feature.append(1)
    else:
        feature.append(0)
    #是否放假
    if date in HOLIDAY:
        feature.append(1)
    elif date in HOLIDAYCHANGE:
        feature.append(0)
    elif weekDay>=6 and weekDay<=7:
        feature.append(1)
    else:
        feature.append(0)
    '''
    #feature.append(1)
    #feature.append(weekDay)
    return feature

def CalculateF1ScorePer(realPlayData, predictPlayData):
    F1Score = 0
    for i in range(len(realPlayData)):
        sigma = 0
        theta = 0
        if realPlayData[i] == 0:
            continue
        sigma += ((predictPlayData[i]-realPlayData[i])/realPlayData[i])**2
        theta += realPlayData[i]
        sigma = math.sqrt(sigma/len(realPlayData))
        theta = math.sqrt(theta)
        F1Score += (1-sigma)*theta
    return 1-sigma

if __name__ == "__main__":
    headers1 = ["ID", "Play", "Date"]
    with open(ARTIST_P_D_C) as fr:
        realPlayData = []
        predictPlayData = []
        artistID = fr.readline().strip("\n")
        mean_F1Score = []
        linear_F1Score = []
        while artistID:
            play = list(map(int, fr.readline().strip("\n").split(",")))
            download = list(map(int, fr.readline().strip("\n").split(",")))
            collect = list(map(int, fr.readline().strip("\n").split(",")))
            play = np.array(play)
            x = [MakeFeature(i) for i in range(183)]
            x = np.array(x)
            '''
            #使用3,4月份预测5,6月份
            train_x = x[0:61]
            train_y = play[0:61]
            test_x = x[61:122]
            test_y = play[61:122]
            mean_y = int(np.mean(train_y[len(train_y)-5:len(train_y)]))
            mean_predict_y = []
            for i in range(len(test_x)):
                mean_predict_y.append(mean_y)
            linear_predict_y = LinearPrediction(train_x, train_y, test_x)
            mean_predict_F1Score = CalculateF1ScorePer(test_y, mean_predict_y)
            linear_predict_F1Score = CalculateF1ScorePer(test_y, linear_predict_y)
            #使用5,6月份预测7,8月份
            train_x = x[-120:-60]
            train_y = play[-120:-60]
            test_x = x[-60:]
            test_y = play[-60:]
            mean_y = int(np.mean(train_y[len(train_y)-5:len(train_y)]))
            mean_predict_y = []
            for i in range(len(test_x)):
                mean_predict_y.append(mean_y)
            linear_predict_y = LinearPrediction(train_x, train_y, test_x)

            predict_y = []
            for i in range(len(mean_predict_y)):
                if mean_predict_F1Score > linear_predict_F1Score:
                    predict_y.append(mean_predict_y[i])
                else:
                    predict_y.append(linear_predict_y[i])
            #predict_y = RandomForestPrediction(train_x, train_y, test_x)
            realPlayData.append(test_y)
            predictPlayData.append(predict_y)
            '''
            #使用5,6月份预测7,8月份
            train_x = x[61:122]
            train_y = play[61:122]
            test_x = x[122:183]
            test_y = play[122:183]
            mean_y = int(np.mean(train_y[len(train_y)-3:len(train_y)]))
            mean_predict_y = []
            for i in range(len(test_x)):
                mean_predict_y.append(mean_y)
            linear_predict_y = LinearPrediction(train_x, train_y, test_x)
            mean_predict_F1Score = CalculateF1ScorePer(test_y, mean_predict_y)
            linear_predict_F1Score = CalculateF1ScorePer(test_y, linear_predict_y)
            mean_F1Score.append(mean_predict_F1Score)
            linear_F1Score.append(linear_predict_F1Score)
            #使用7,8月份预测9,10月份
            train_x = x[122:183]
            train_y = play[122:183]
            predict_x = []
            for days in range(61):
                predict_x.append(MakeFeature(days+183))
            mean_y = int(np.mean(train_y[len(train_y)-7:len(train_y)]))
            mean_predict_y = []
            for i in range(len(predict_x)):
                mean_predict_y.append(mean_y)
            linear_predict_y = LinearPrediction(train_x, train_y, predict_x)#预测
            prediction_y = []
            for i in range(len(mean_predict_y)):
                if math.fabs((linear_predict_y[i]-mean_predict_y[i])) > 0.025*mean_predict_y[i]:
                    prediction_y.append(mean_predict_y[i])
                else:
                    prediction_y.append(linear_predict_y[i])
                '''
                if mean_predict_F1Score > linear_predict_F1Score:
                    prediction_y.append(mean_predict_y[i])
                else:
                    prediction_y.append(linear_predict_y[i])
                '''
            predict_file_path = os.path.join(CURRENT_PATH, "mars_tianchi_predict_data.csv")
            WriteResult(artistID, predict_file_path, prediction_y)
            artistID = fr.readline().strip("\n")
        print(CalculateF1Score(realPlayData, predictPlayData))
        print(mean_F1Score)
        print(linear_F1Score)
        '''
        print(ARTIST_F1SCORE)
        file_path = os.path.join(CURRENT_PATH, "linear_score.csv")
        WriteF1Score(file_path, ARTIST_F1SCORE)
        '''

