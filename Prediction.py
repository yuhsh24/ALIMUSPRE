# -*- coding: utf-8 -*-

import os
import sys
import numpy as np
from sklearn import linear_model
import csv
import time

CURRENT_PATH = sys.path[0]#获取当前路径
ARTIST_P_D_C = os.path.join(CURRENT_PATH, "artist_p_d_c.txt")
DAYS = 183
START_UNIX = 1425139200#表示20150301
DAY_SECOND = 86400#每天的秒数

def LinearPrediction(train_X, train_y, predict_x):
    regr = linear_model.Ridge(alpha=.05, fit_intercept=False)
    regr.fit(train_X, train_y)
    initial_y = regr.predict(predict_x)
    prediction_y = []#返回的整数预测值
    for i in range(len(initial_y)):
        prediction_y.append(max(0, int(initial_y[i])))
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

if __name__ == "__main__":
    headers1 = ["ID", "Play", "Date"]
    with open(ARTIST_P_D_C) as fr:
        artistID = fr.readline().strip("\n")
        while artistID:
            play = list(map(int, fr.readline().strip("\n").split(",")))
            download = list(map(int, fr.readline().strip("\n").split(",")))
            collect = list(map(int, fr.readline().strip("\n").split(",")))
            play = np.array(play)
            x = [[i, 1] for i in range(183)]
            x = np.array(x)
            predict_x = []
            for days in range(61):
                predict_x.append([days+183, 1])
            prediction_y = LinearPrediction(x, play, predict_x)#预测
            predict_file_path = os.path.join(CURRENT_PATH, "mars_tianchi_predict_data.csv")
            WriteResult(artistID, predict_file_path, prediction_y)
            artistID = fr.readline().strip("\n")
