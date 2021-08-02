import math, random
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# sns.set(font='UTF-8')

code_dir = Path(__file__)
ipt_dir = Path(code_dir.parents[1], 'in')
otpt_dir = Path(code_dir.parents[1], 'out')

class Onward_list_generator():

    def __init__(self, ipt_dir) -> None:
        # 希望日のエクセルリスト
        self.kibou_lists = []
        for path in ipt_dir.iterdir():
            self.kibou_lists.append(pd.read_excel(path.resolve()))

        self.kibou_lists = [pddf.fillna(0) for pddf in self.kibou_lists]

        # 当直回数のカウンター
        self.n_days = self.kibou_lists[0].shape[0]
        self.counter_dict = {'勝木': 6}
        self.counter_dict['松本'] = self.counter_dict['濱田'] = math.floor((self.n_days - self.counter_dict['勝木'])/3)
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

    def is_kyujitsu(self, date):
        if (self.kibou_lists[0].loc[date, '土日'] == 1 or
            self.kibou_lists[0].loc[date, '祝日'] == 1):
            return True
        else:
            return False

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
        # print("kibou_ninzu")
        # print(kibou_ninzu)
        # print(sum(kibou_ninzu.values()))
        
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
            if self.is_kyujitsu(date):
                self.yasumi_dict[tantou] = self.yasumi_dict[tantou] + 1
            
        # print(self.result)
        # print(self.counter_dict)

    def kyujitsu_ume(self):
        # 休日リスト
        kyujitsu_list = []
        for date in range(self.result.shape[0]):
            # 埋まっていない休日をリスト化
            if (self.is_kyujitsu(date) and
                self.result.loc[date, '担当'] == 'いません'):
                    kyujitsu_list.append(date)
        print("kyujitsu list")
        print(kyujitsu_list)
        # 埋まっていない休日をランダムチョイス
        counter = 0
        while len(kyujitsu_list) > 0:
            date = random.choice(kyujitsu_list)
            print(date)
            # 候補の作成
            # 休日が最小の人から選ぶ
            kouho = []
            kyujitsu_min = min(self.yasumi_dict.values())

            for df in self.kibou_lists:
                hito = df.loc[0, '名前']
                if self.yasumi_dict[hito] == kyujitsu_min:
                    if (df.loc[date, '不希望日'] == 0 and self.counter_dict[hito] > 0 ):
                        kouho.append(hito)

            print("一次候補")
            print(kouho)
            # 休日には連続して入らないようにする
            if date > 0 and self.is_kyujitsu(date - 1):
                if self.result.loc[date - 1, '担当'] in kouho:
                    kouho.remove(self.result.loc[date - 1, '担当'])

            if date < self.kibou_lists[0].shape[0] - 1 and self.is_kyujitsu(date + 1):
                if self.result.loc[date + 1, '担当'] in kouho:
                    kouho.remove(self.result.loc[date + 1, '担当'])

            # 候補がいれば埋める
            if len(kouho) > 0:
                tantou = random.choice(kouho)
                print("正式候補")
                print(tantou)
                self.result.loc[date, '担当'] = tantou
                self.counter_dict[tantou] = self.counter_dict[tantou] - 1
                self.yasumi_dict[tantou] = self.yasumi_dict[tantou] + 1
                kyujitsu_list.remove(date)
                # 休日が埋まりきらない場合がある?
            else:
                counter += 1
                print(date)
                print("候補いない")

            if counter == 10:
                break
        print(self.counter_dict)
        print(self.yasumi_dict)

    def nokori_ume(self):
        # 残りの埋まってないところのリスト
        nokori_list = []
        for date in range(self.result.shape[0]):
            if self.result.loc[date, '担当'] == 'いません':
                nokori_list.append(date)
        
        counter = 0
        while len(nokori_list) > 0:
            # 埋める日にち
            date = random.choice(nokori_list)

            # 候補の作成
            # 残り日数最大の人から埋めていく
            kouho = []
            max_nissu = max(self.counter_dict.values())
            for df in self.kibou_lists:
                hito = df.loc[0, '名前']
                if self.counter_dict[hito] == max_nissu:
                    if (df.loc[date, '不希望日'] == 0 
                    # and self.counter_dict[hito] > 0
                    ):
                        kouho.append(hito)
        
            # # 連続して入らないようにする
            # if date > 0:
            #     if self.result.loc[date - 1, '担当'] in kouho:
            #         kouho.remove(self.result.loc[date - 1, '担当'])

            # if date < self.kibou_lists[0].shape[0] - 1:
            #     if self.result.loc[date + 1, '担当'] in kouho:
            #         kouho.remove(self.result.loc[date + 1, '担当'])

            # 候補がいれば埋める
            if len(kouho) > 0:
                tantou = random.choice(kouho)
                self.result.loc[date, '担当'] = tantou
                self.counter_dict[tantou] = self.counter_dict[tantou] - 1
                nokori_list.remove(date)
            else:
                counter +=1
                print("候補いない")
            if counter == 10:
                break
        print(self.counter_dict)

    def plot_day_count(self):
        s = self.result['担当'].value_counts()
        print(s)
        sns.barplot(x=s.index, y=s.values)
        plt.title('セカンドの日数です')
        plt.savefig(otpt_dir/"total.png")

    def plot_kyujitsu_count(self):
        s = pd.Series(self.yasumi_dict)
        print(s)
        sns.barplot(x=s.index, y=s.values)
        plt.title('休日担当の日数です')
        plt.savefig(otpt_dir/"holidays.png")

    def return_result(self):
        return self.result

olg = Onward_list_generator(ipt_dir=ipt_dir)
olg.kibou_ume()
olg.kyujitsu_ume()
olg.nokori_ume()
# olg.plot_day_count()
# olg.plot_kyujitsu_count()

result = olg.return_result()
result.to_csv(Path(otpt_dir, '今月のセカンド担当表.csv'), encoding='shift-jis', index=False)
