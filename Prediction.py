# -*- coding: utf-8 -*-

import os
import sys
import numpy as np
from sklearn import linear_model
import csv
import time
import math

CURRENT_PATH = sys.path[0]#获取当前路径
ARTIST_P_D_C = os.path.join(CURRENT_PATH, "artist_p_d_c.txt")
DAYS = 183
START_UNIX = 1425139200#表示20150301
DAY_SECOND = 86400#每天的秒数
START_WEEKDAY = 7#表示是一周的第几天

#线性预测函数
def LinearPrediction(train_X, train_y, predict_x):
    regr = linear_model.Ridge(alpha=.05, fit_intercept=False)
    regr.fit(train_X, train_y)
    initial_y = regr.predict(predict_x)
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

if __name__ == "__main__":
    headers1 = ["ID", "Play", "Date"]
    with open(ARTIST_P_D_C) as fr:
        realPlayData = []
        predictPlayData = []
        artistID = fr.readline().strip("\n")
        while artistID:
            play = list(map(int, fr.readline().strip("\n").split(",")))
            download = list(map(int, fr.readline().strip("\n").split(",")))
            collect = list(map(int, fr.readline().strip("\n").split(",")))
            play = np.array(play)
            x = [[i, 1] for i in range(183)]
            x = np.array(x)
            #使用3\4月的数据训练得到predict,download,collect的预测模型
            feature_x = x[0:61]
            play_y = play[0:61]
            download_y = download[0:61]
            collect_y = collect[0:61]
            predict_x = x[61:122]#预测的时间
            predict_play_y = LinearPrediction(feature_x, play_y, predict_x)#得到预测的播放量
            predict_download_y = LinearPrediction(feature_x, download_y, predict_x)#得到预测的下载量
            predict_collect_y = LinearPrediction(feature_x, collect_y, predict_x)#得到预测的收藏量
            #将5\6月份的数据以及预测的5,6月份的数据进行回归训练
            final_feature_x = [[i, 1, predict_play_y[i], predict_download_y[i], predict_download_y[i]] for i in \
                               range(len(predict_play_y))]
            final_play_y = play[61:122]
            #将5\6月份的数据训练得到predict,download,collect的预测模型
            feature_x = [[i, 1] for i in range(61)]
            play_y = play[61:122]
            download_y = download[61:122]
            collect_y = collect[61:122]
            predict_x = [[i, 1] for i in range(61, 122)]
            predict_play_y = LinearPrediction(feature_x, play_y, predict_x)#得到预测的播放量
            predict_download_y = LinearPrediction(feature_x, download_y, predict_x)#得到预测的下载量
            predict_collect_y = LinearPrediction(feature_x, collect_y, predict_x)#得到预测的收藏量
            #组合测试特征
            feature_test_x = [[predict_x[i][0], 1, predict_play_y[i], predict_download_y[i], predict_collect_y[i]] for i\
                              in range(len(predict_x))]
            predict_y = LinearPrediction(final_feature_x, final_play_y, feature_test_x)
            realPlayData.append(play[122:183])
            predictPlayData.append(predict_y)
            '''
            predict_x = []
            for days in range(61):
                predict_x.append([days+183, 1])
            prediction_y = LinearPrediction(x, play, predict_x)#预测
            predict_file_path = os.path.join(CURRENT_PATH, "mars_tianchi_predict_data.csv")
            WriteResult(artistID, predict_file_path, prediction_y)
            '''
            artistID = fr.readline().strip("\n")
        print(CalculateF1Score(realPlayData, predictPlayData))
        print(CalculateF1Score(realPlayData, realPlayData))
