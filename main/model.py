import re
from typing import Dict, List, Optional

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder

from .db import DataBase

def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
    data['construct_time'] = data['construct_time'].map(
        lambda x: re.sub('\D', '', str(x))
    ).astype(int)
    return data.dropna()


def subway_data_processor(subway: pd.DataFrame) -> pd.DataFrame:
    ret = subway.dropna().                                 \
        groupby(by=['community_name', 'station_name']).     \
        agg({'distance': 'mean'}).                          \
        reset_index().                                      \
        groupby(by=['community_name']).                     \
        agg({'distance': 'mean', 'station_name': 'count'}). \
        reset_index()

    ret['station_num'] = ret['station_name']
        
    return ret[[
        'community_name',
        'distance',
        'station_num'
    ]]


def integer_encoder(data: pd.DataFrame) -> pd.DataFrame:
    encoder = OrdinalEncoder()
    encoder.fit(data[['area', 'street']])
    
    result = pd.concat([
        data.drop(['area', 'street', 'community_name'], axis=1). \
            reset_index(drop=True),
        pd.DataFrame(
            encoder.transform(data[['area', 'street']]),
            columns=['area', 'street']
        )], axis=1)

    # 处理construct_time数据
    result.construct_time = result.construct_time.astype(int). \
        apply(lambda x: -1 if x == 0 else 2021-x)
    for i in data.drop(['area', 'street', 'community_name'], axis=1).columns:
        result[i].astype(float)
    return result


def ten_fold_predict(encoded_df):
    '''
        经过跟前端组的讨论，目前的方案是：
        将数据分为10组，对于每1组，每次使用剩下9组作为训练集，训练模型，对该组进行价格预测，将模型输出作为剩下1组的预测价格
        将预测价格作为一个属性并入房屋数据中，在前端进行可视化展示

        关于模型：
        仍然使用随机森林
        考虑到计算成本，使用了integer编码，并且筛掉了col中的特征
        增加决策树个数可以一定程度上提高R^2，但考虑到计算成本，决定将决策树个数设为100
    '''
    #预测价格

    x_t, y_t = {}, {}
    x_tr, y_tr = {}, {}
    ret, df_tmp = pd.DataFrame(), pd.DataFrame()

    x_t[9], x_t[10], y_t[9], y_t[10] = train_test_split(
        encoded_df.drop(['price_per_square'], axis=1),
        encoded_df.price_per_square,
        test_size=0.1
    )

    for i in range(9, 1, -1):
        x_t[i - 1], x_t[i], y_t[i - 1], y_t[i] = train_test_split(
            x_t[i], y_t[i],
            test_size=1 / (i)
        )

    for i in range(1, 11):
        x_tr[i] = encoded_df.drop(x_t[i].index).drop(['price_per_square'], axis=1)
        y_tr[i] = encoded_df.drop(x_t[i].index).price_per_square
    for i in range(1, 11):
        regr = RandomForestRegressor(random_state=0, n_estimators=100)
        regr.fit(x_tr[i], y_tr[i])
        y_p = regr.predict(x_t[i])
        df_tmp = pd.concat([
            encoded_df.iloc[x_t[i].index].reset_index(),
            pd.DataFrame(y_p, columns=['predict_price'])
        ], axis=1)
        ret = ret.append(df_tmp)

    ret.sort_values(by='index', inplace=True)
    ret.drop(['index'], axis=1, inplace=True)
    ret.reset_index(drop=True, inplace=True)

    return ret


async def train():
    print((await DataBase().get_regression_data())[0])
    data = preprocess_data(
        pd.DataFrame.from_records(await DataBase().get_regression_data())
    )
    subway = subway_data_processor(
        pd.DataFrame.from_records(await DataBase().get_subway_data())
    )

    train = pd.merge(data, subway,
        how='left',
        on=['community_name']
    )
    train['distance'] = train['distance'].fillna(value=0)
    train['station_num'] = train['station_num'].fillna(value=0)

    ret = ten_fold_predict(integer_encoder(train))[['beike_ID', 'predict_price']]
    ret.set_index('beike_ID', inplace=True)
    return ret['predict_price']




class ModelResult():

    _result: Optional[Dict[int, float]] = None
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(ModelResult)
        return cls._instance

    def __init__(self):
        pass

    async def run(self, beike_ID: List[int] = []) -> Dict[int, float]:
        if self._result is None:
            self._result = (await train()).to_dict()

        return [self._result.get(_, None) for _ in beike_ID]

    def clear(self):
        self._result is None
