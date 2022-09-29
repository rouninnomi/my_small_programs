import math
import random
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
sns.set(font='Yu Gothic')

code_dir = Path('.')
ipt_dir = Path(code_dir.parent, 'in')
otpt_dir = Path(code_dir.parent, 'out')

class Onward_list_generator():

    def __init__(self, ipt_dir) -> None:
        # 希望日のエクセルリスト
        self.kibou_lists = []
        for path in ipt_dir.iterdir():
            self.kibou_lists.append(pd.read_excel(path.resolve()))

        self.kibou_lists = [pddf.fillna(0) for pddf in self.kibou_lists]

        # 当直回数のカウンター
        self.n_days = self.kibou_lists[0].shape[0]
        ninzu = 4
        self.counter_dict = {'勝木': math.floor(self.n_days/(ninzu + 1))}
        self.counter_dict['松本'] = self.counter_dict['濱田'] = math.ceil((self.n_days - self.counter_dict['勝木'])/4)
        self.counter_dict['根岸'] = (
            self.n_days 
            -self.counter_dict['勝木']
            -self.counter_dict['松本']
            -self.counter_dict['濱田']
            )

        # 休みのカウンター
        self.yasumi_dict = {'勝木': 0,
                    '根岸': 0,
                    '松本': 0,
                    '濱田': 0}

        # 結果の表
        self.result = pd.DataFrame({'日付': self.kibou_lists[0]['日付'],
                            '担当': 'いません'})

        # ランダムチョイスするための覚書
        self.random_pool = [i for i in range(self.n_days)]

    def kibou_ume(self):
        for date in range(self.result.shape[0]):
        # 候補の作成
            kouho = []
            for df in self.kibou_lists:
                hito = df.loc[0, '名前']
                if (df.loc[date, '希望日'] == 1 and 
                    self.counter_dict[hito] > 0):
                        kouho.append(hito)

            # 候補がいれば埋める
            if len(kouho) > 0:
                tantou = random.choice(kouho)
                self.result.loc[date, '担当'] = tantou
                self.counter_dict[tantou] = self.counter_dict[tantou] - 1

                # 休日だったらカウンター増やす
                is_kyujitsu = (self.kibou_lists[0].loc[date, '土日'] == 1 or
                                self.kibou_lists[0].loc[date, '祝日'] == 1)
                if is_kyujitsu:
                        self.yasumi_dict[tantou] = self.yasumi_dict[tantou] + 1

    def kyujitsu_ume(self):
        for date in range(self.result.shape[0]):
            is_kyujitsu = (self.kibou_lists[0].loc[date, '土日'] == 1 or 
                            self.kibou_lists[0].loc[date, '祝日'] == 1)
            # 埋まっていない休日を埋める
            if (is_kyujitsu and
                self.result.loc[date, '担当'] == 'いません'):
                # 候補の作成
                # 休日がその時点で最大の人は避ける
                kouho = []
                kyujitsu_max = pd.Series(self.yasumi_dict).max()

                for df in self.kibou_lists:
                    hito = df.loc[0, '名前']
                    if (df.loc[date, '不希望日'] == 0 and
                        self.counter_dict[hito] > 0 
                        and
                        self.yasumi_dict[hito] != kyujitsu_max
                        ):
                            kouho.append(hito)

                # 連続して入らないようにする
                if date > 0 and (self.result.loc[date - 1, '担当'] in kouho):
                    kouho.remove(self.result.loc[date - 1, '担当'])

                if date < self.kibou_lists[0].shape[0] and (self.result.loc[date + 1, '担当'] in kouho):
                    kouho.remove(self.result.loc[date + 1, '担当'])

                # if date != self.result.shape[0] -1 and (self.result.loc[date + 1, '担当'] in kouho):
                #     kouho.remove(self.result.loc[date + 1, '担当'])

                # 候補がいれば埋める
                if len(kouho) > 0:
                    tantou = random.choice(kouho)
                    self.result.loc[date, '担当'] = tantou
                    self.counter_dict[tantou] = self.counter_dict[tantou] - 1
                    self.yasumi_dict[tantou] = self.yasumi_dict[tantou] + 1
                    # 休日が埋まりきらない場合がある

    def nokori_ume(self):
        for date in range(self.result.shape[0]):
            if self.result.loc[date, '担当'] == 'いません':
                # 候補の作成
                kouho = []
                for df in self.kibou_lists:
                    hito = df.loc[0, '名前']
                    if (df.loc[date, '不希望日'] == 0 and
                        self.counter_dict[hito] > 0):
                            kouho.append(hito)
            
                # 連続して入らないようにする
                if date > 0 and (self.result.loc[date - 1, '担当'] in kouho):
                    kouho.remove(self.result.loc[date - 1, '担当'])

                if date < self.kibou_lists[0].shape[0] and (self.result.loc[date + 1, '担当'] in kouho):
                    kouho.remove(self.result.loc[date + 1, '担当'])

                # if date != self.result.shape[0] -1 and (self.result.loc[date + 1, '担当'] in kouho):
                #     kouho.remove(self.result.loc[date + 1, '担当'])
                # 平日に関して前後を全部配慮するとだれも入れない日ができてしまうのでOff

                # 候補がいれば埋める
                if len(kouho) > 0:
                    tantou = random.choice(kouho)
                    self.result.loc[date, '担当'] = tantou
                    self.counter_dict[tantou] = self.counter_dict[tantou] - 1

                    # 休日だったらカウンター増やす
                    is_kyujitsu = (self.kibou_lists[0].loc[date, '土日'] == 1 or
                                    self.kibou_lists[0].loc[date, '祝日'] == 1)
                    if is_kyujitsu:
                            self.yasumi_dict[tantou] = self.yasumi_dict[tantou] + 1

    def plot_day_count(self):
        s = self.result['担当'].value_counts()
        print(s)
        sns.barplot(x=s.index, y=s.values)
        plt.title('セカンドの日数です')
        plt.show()

    def plot_kyujitsu_count(self):
        s = pd.Series(self.yasumi_dict)
        print(s)
        sns.barplot(x=s.index, y=s.values)
        plt.title('休日担当の日数です')
        plt.show()

    def return_result(self):
        return self.result

olg = Onward_list_generator(ipt_dir=ipt_dir)
olg.kibou_ume()
olg.kyujitsu_ume()
olg.nokori_ume()

# # 未定日が1日以下になるように、休日日数が一定になるように、など条件つけて最適化
# while olg.result['担当'].value_counts()['いません'] >= 0:
#     olg.kibou_ume()
#     olg.kyujitsu_ume()
#     olg.nokori_ume()

olg.plot_day_count()
olg.plot_kyujitsu_count()
result = olg.return_result()
result.to_csv(Path(otpt_dir, '今月のセカンド担当表.csv'), encoding='shift-jis', index=False)