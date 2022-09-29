import pandas as pd
from pathlib import Path
from datetime import date
import calendar
import jpholiday
import random
from collections import Counter

# code_dir = Path(".").resolve()
# ipt_dir = code_dir.parent / "in"
# otpt_dir = code_dir.parent / "out"

class Data:
    # 注文者と盛り、候補メニューについての情報をまとめるクラス
    def __init__(self, data_path='../static/files/test.xlsx') -> pd.DataFrame:
        self.raw_df = pd.read_excel(data_path)

    def extract_data(self):
        data = {}
        for person, mori in zip(self.raw_df['注文者'].dropna(), self.raw_df['盛り'].dropna()):
            menu = list(self.raw_df['メニュー'].dropna().values)
            random.shuffle(menu)
            data[person] = {'mori':mori, 'kouho_menu': menu}
        self.data = data

    def dislike_menus(self):
        # To do
        # flaskで入力を受けて実際のリストを編集するようにしたい
        # 自分で入力
        # QRコード
        hito = ''
        iya = ''
        if iya in self.data[hito]['kouho_menu']:
            self.data[hito]['kouho_menu'].remove(iya)

class Chumon:
    # 実際の注文カレンダーを出力するクラス
    def __init__(self, month, data) -> None:
        self.month = month
        self.data = data.data

        def calc_order_days():
            today = date.today()
            target_month_day1 = date(today.year, month, 1)
            if month == 1:
                target_month_day1.year = today.year + 1

            days = [date(target_month_day1.year, target_month_day1.month, day) for day in range(1, calendar.monthrange(target_month_day1.year, target_month_day1.month)[1] + 1)]
            is_holiday = [jpholiday.is_holiday(day) for day in days]
            self.order_days = [day for day, holiTF in zip(days, is_holiday) if (day.weekday() not in [5, 6]) and (not holiTF)]

        def combine_menu_names():
            for person in self.data.keys():
                self.data[person]['kouho_menu'] = [' '.join([menu, self.data[person]['mori']]) for menu in self.data[person]['kouho_menu']]

        calc_order_days()
        combine_menu_names()

    def make_calendar(self):
        cal = [f'{date.year}年{date.month}月{date.day}日' for date in self.order_days]
        
        for person in self.data.keys():
            kouho = self.data[person]['kouho_menu']
            unit_num = len(kouho)
            loops = len(cal) // unit_num
            former_orders = kouho * loops
            latter_orders = kouho[:len(cal) % unit_num]
            self.data[person]['orders'] = former_orders + latter_orders

        total_calendar = pd.DataFrame({'日付':cal})
        for person in self.data.keys():
            ser = pd.Series(self.data[person]['orders'])
            ser.name = person
            total_calendar = pd.concat([total_calendar, ser], axis=1)

        total_calendar = total_calendar.set_index('日付')
        self.total_calendar = total_calendar

    def make_daily_order(self):
        daily_orders = []
        for date in self.total_calendar.index:
            daily_orders.append(Counter(self.total_calendar.loc[date, :]))
        self.daily_orders = daily_orders
        return self.daily_orders



    # return それぞれの人の注文と合計

# data = Data(ipt_dir / "注文者とメニュー.xlsx")
# data.extract_data()
# chumon = Chumon(10, data)

# chumon.make_calendar()
# chumon.make_daily_order()
# chumon.daily_orders
