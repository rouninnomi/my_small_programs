import math, random, time
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

    def kibou_ume(self):
        # 候補辞書の作成
        kouho = {}
        for date in range(self.n_days):
            kouho[date] = []
            for df in self.kibou_lists:
                hito = df.loc[0, '名前']
                if (df.loc[date, '希望日'] == 1 and 
                    self.counter_dict[hito] > 0):
                        kouho[date].append(hito)
        
        # 希望者がいる日にちのみ埋める
        # 最も希望者が少ない、0でない日にちから埋める
        # 希望人数の辞書も
        kibou_ninzu = {}
        for date in kouho:
            n = len(kouho[date])
            if n > 0:
                kibou_ninzu[date] = n
        
        # start = time.time()
        while len(kibou_ninzu) > 0:
            # now = time.time()
            saishouninzu = min(kibou_ninzu.values())
            saisho_ninzu_kouhobi_dict = {date:kouho[date] for date in kibou_ninzu if kibou_ninzu[date] == saishouninzu}
            date = random.choice(list(saisho_ninzu_kouhobi_dict.keys()))
            # 候補を埋める     
            tantou = random.choice(kouho[date])
            self.result.loc[date, '担当'] = tantou
            self.counter_dict[tantou] = self.counter_dict[tantou] - 1

            # 辞書を削る
            del kouho[date]
            del kibou_ninzu[date]

            # 休日だったらカウンター増やす
            is_kyujitsu = (self.kibou_lists[0].loc[date, '土日'] == 1 or
                            self.kibou_lists[0].loc[date, '祝日'] == 1)
            if is_kyujitsu:
                self.yasumi_dict[tantou] = self.yasumi_dict[tantou] + 1
            
            # # 1分過ぎても埋まらないときはbreak
            # if now - start >= 60:
            #     break

    def kyujitsu_ume(self):
        # 休日リスト
        kyujitsu_list = []
        for date in range(self.result.shape[0]):
            is_kyujitsu = (self.kibou_lists[0].loc[date, '土日'] == 1 or 
                            self.kibou_lists[0].loc[date, '祝日'] == 1)
            # 埋まっていない休日をリスト化
            if (is_kyujitsu and
                self.result.loc[date, '担当'] == 'いません'):
                    kyujitsu_list.append(date)
        # 埋まっていない休日をランダムチョイス
        start = time.time()
        while len(kyujitsu_list) > 0:
            now = time.time()
            date = random.choice(kyujitsu_list)

            # 候補の作成
            # 休日がその時点で最大の人は避ける
            kouho = []
            kyujitsu_max = max(self.yasumi_dict.values())

            for df in self.kibou_lists:
                hito = df.loc[0, '名前']
                if (df.loc[date, '不希望日'] == 0 
                    and
                    self.counter_dict[hito] > 0 
                    and
                    (self.yasumi_dict[hito] != kyujitsu_max and len(set(self.yasumi_dict.values())) != 1)
                    # こうしないと全員の休み日数が同じになったときに候補がいなくなる
                    ):
                        kouho.append(hito)

            # 連続して入らないようにする
            if date > 0:
                if self.result.loc[date - 1, '担当'] in kouho:
                    kouho.remove(self.result.loc[date - 1, '担当'])

            if date < self.kibou_lists[0].shape[0] - 1:
                if self.result.loc[date + 1, '担当'] in kouho:
                    kouho.remove(self.result.loc[date + 1, '担当'])

            # 候補がいれば埋める
            if len(kouho) > 0:
                tantou = random.choice(kouho)
                self.result.loc[date, '担当'] = tantou
                self.counter_dict[tantou] = self.counter_dict[tantou] - 1
                self.yasumi_dict[tantou] = self.yasumi_dict[tantou] + 1
                # 休日が埋まりきらない場合がある?

            if now - start >= 60:
                break

    def nokori_ume(self):
        # 残りの埋まってないところのリスト
        nokori_list = []
        for date in range(self.result.shape[0]):
            if self.result.loc[date, '担当'] == 'いません':
                nokori_list.append(date)
        
        start = time.time()
        while len(nokori_list) > 0:
            now = time.time()
            # 埋める日にち
            date = random.choice(nokori_list)
            
            # 候補の作成
            kouho = []
            for df in self.kibou_lists:
                hito = df.loc[0, '名前']
                if (df.loc[date, '不希望日'] == 0 and
                    self.counter_dict[hito] > 0):
                        kouho.append(hito)
        
            # 連続して入らないようにする
            if date > 0:
                if self.result.loc[date - 1, '担当'] in kouho:
                    kouho.remove(self.result.loc[date - 1, '担当'])

            if date < self.kibou_lists[0].shape[0] - 1:
                if self.result.loc[date + 1, '担当'] in kouho:
                    kouho.remove(self.result.loc[date + 1, '担当'])

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
            if now - start >= 120:
                break

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
print("kibou")
olg.kibou_ume()
olg.plot_day_count()
olg.plot_kyujitsu_count()
print("kyujitsu")
olg.kyujitsu_ume()
olg.plot_day_count()
olg.plot_kyujitsu_count()
print("nokori")
olg.nokori_ume()
olg.plot_day_count()
olg.plot_kyujitsu_count()

result = olg.return_result()
result.to_csv(Path(otpt_dir, '今月のセカンド担当表.csv'), encoding='shift-jis', index=False)
