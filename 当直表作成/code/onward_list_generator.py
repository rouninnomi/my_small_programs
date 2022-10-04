# TODO: 
# 希望表出してない人の処理をどうするか？
# 候補者リストを読み込ませ、出してない人をすべての日にちOKとしてリスト生成する


import math, random
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# https://www.yutaka-note.com/entry/matplotlib_japanese
# import matplotlib.font_manager as fm
# import matplotlib as mpl

# fontpath = '/opt/conda/lib/python3.9/site-packages/matplotlib/mpl-data/fonts/ttf/ipaexg.ttf'
# prop = fm.FontProperties(fname=fontpath)
# mpl.rcParams['font.family'] = prop.get_name()
# plt.rcParams['font.family'] = "IPAexGothic"


code_dir = Path(__file__)
ipt_dir = Path(code_dir.parents[1], 'in')
otpt_dir = Path(code_dir.parents[1], 'out')
sns.set(font='IPAexGothic')

class Onward_list_generator():

    def __init__(self, ipt_dir, otpt_dir) -> None:
        # 希望日のエクセルリストから希望の日にち、メンバー、学年のデータを抽出

        def extract_basic_data_from_excels(ipt_dir):
            self.kibou_lists = []
            self.members = []
            self.gakunen = []

            for path in ipt_dir.iterdir():
                self.kibou_lists.append(pd.read_excel(path.resolve(), usecols=["日付", "土日", "祝日", "希望日", "不希望日"]))
                self.kibou_lists = [pddf.fillna(0) for pddf in self.kibou_lists]

                self.members.append(pd.read_excel(path.resolve(), usecols=["フルネーム"]).iloc[0, 0])
                self.gakunen.append(int(pd.read_excel(path.resolve(), usecols=["医師年数（半角入力）"]).iloc[0, 0]))

        def make_duty_counters():
            # 当直回数の残りカウンターを設定する
            self.n_days = self.kibou_lists[0].shape[0]

            self.counter_dict = dict()
            for person in self.members:
                self.counter_dict[person] = self.n_days // len(self.members)

            # 一番学年が若く,、回数少ない順に残り回数を振り分ける
            rest = self.n_days % len(self.members)
            members = self.members.copy()
            members.remove('勝木')
            while rest > 0:
                target = min(self.counter_dict, key=self.counter_dict.get)
                self.counter_dict[target] = self.counter_dict[target] + 1
                rest -= 1

            self.counter_dict['勝木'] = self.n_days // len(self.members)

        def make_holiday_counters():
            # 休みのカウンター
            self.kyujitsu_kaisu_dict = dict()
            for person in self.members:
                self.kyujitsu_kaisu_dict[person] = 0

        def make_result():
            # 結果の表
            self.result = pd.DataFrame({'日付': self.kibou_lists[0]['日付'],
                                '担当': 'いません'})
            
        def read_past_record(otpt_dir):
            # 過去の実績
            if otpt_dir/"past_record.csv":
                self.past_record = pd.read_csv(otpt_dir/"past_record.csv")
            else:
                self.past_record = pd.DataFrame({"名前":self.members, "回数":0})

        extract_basic_data_from_excels(ipt_dir=ipt_dir)
        make_duty_counters()
        make_holiday_counters()
        make_result()
        read_past_record(otpt_dir=otpt_dir)

    def is_kyujitsu(self, date):
        if (self.kibou_lists[0].loc[date, '土日'] == 1 or
            self.kibou_lists[0].loc[date, '祝日'] == 1):
            return True
        else:
            return False

    def kyujitsu_ume(self):
        # 休日リスト
        kyujitsu_date_list = []
        for date in range(self.result.shape[0]):
            # 休日をリスト化
            if self.is_kyujitsu(date):
                kyujitsu_date_list.append(date)

        # 休日をランダムチョイス
        counter = 0
        while len(kyujitsu_date_list) > 0:
            date = random.choice(kyujitsu_date_list)
        
            # 候補の作成
            # 休日が最小の人から選ぶ
            kouho = []
            kyujitsu_min = min(self.kyujitsu_kaisu_dict.values())

            for df in self.kibou_lists:
                hito = df.loc[0, '名前']
                if self.kyujitsu_kaisu_dict[hito] == kyujitsu_min:
                    if (df.loc[date, '不希望日'] == 0 and self.counter_dict[hito] > 0 ):
                        kouho.append(hito)

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
                self.result.loc[date, '担当'] = tantou
                self.counter_dict[tantou] = self.counter_dict[tantou] - 1
                self.kyujitsu_kaisu_dict[tantou] = self.kyujitsu_kaisu_dict[tantou] + 1
                kyujitsu_date_list.remove(date)
                # 休日が埋まりきらない場合がある?
            else:
                counter += 1
                print(date)
                print("候補いない")

            if counter == 10:
                break

    def kibou_ume(self):
        # 候補辞書の作成
        kouho = {}
        for date in range(self.n_days):
            kouho[date] = []
            for hito, df in zip(self.members, self.kibou_lists):
                if self.counter_dict[hito] > 0:
                    if df.loc[date, '希望日'] == 1:
                        kouho[date].append(hito)
        
        # 希望者がいる日にちのみ埋める
        # 最も希望者が少ない、0でない日にちから埋める
        # 希望人数の辞書も
        kibou_ninzu = {}
        for date in kouho:
            n = len(kouho[date])
            if n > 0:
                kibou_ninzu[date] = n
        
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
                self.kyujitsu_kaisu_dict[tantou] = self.kyujitsu_kaisu_dict[tantou] + 1

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

    def plot_day_count(self):
        s = self.result['担当'].value_counts()
        sns.barplot(x=s.index, y=s.values)
        plt.title('セカンドの日数です')
        plt.savefig(otpt_dir/"total.png")

    def plot_kyujitsu_count(self):
        s = pd.Series(self.kyujitsu_kaisu_dict)
        sns.barplot(x=s.index, y=s.values)
        plt.title('休日担当の日数です')
        plt.savefig(otpt_dir/"holidays.png")

    def plot_past_record(self):
        pass

    def return_result(self):
        return self.result