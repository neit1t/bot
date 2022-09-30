import matplotlib.pyplot as plt
import numpy as np
import re
import sqlite3
import os
from datetime import date

class Database():

    def __init__(self) -> None:
        self.conn = sqlite3.connect('показания test.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS показания (
            Номер INT,
            Месяц_год TEXT,
            Показания_Т1 REAL,
            Показания_Т2 REAL,
            Показания_горячей_воды REAL,
            Показания_холодной_воды REAL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Admin (
                    Номер_для_поиска INT,
                    Последний_номер_заполнения INT,
                    Последний_месяц_заполнения INT,
                    Последний_год_заполнения INT)''')
        self.conn.commit()
        self.month = {j:i for j,i in zip(list(range(1,13)),['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'])}

        self.__admin = [j for i in self.cursor.execute(f'''select * from Admin''') for j in i]

        if self.__admin == []:
            self.last_month,self.last_year = int(date.today().strftime("%-m")),int(date.today().strftime("%Y"))
            self.cursor.execute(f'''INSERT INTO Admin 
            (Номер_для_поиска,Последний_номер_заполнения,Последний_месяц_заполнения,Последний_год_заполнения) 
            VALUES 
            ("{1}","{1}","{self.last_month}","{self.last_year}")''')
            self.cursor.execute(f'''insert into показания 
            (Номер,Месяц_год ,Показания_Т1,Показания_Т2,Показания_горячей_воды,Показания_холодной_воды) 
            values 
            ("{1}","{self.month[self.last_month]}/{self.last_year}","{0}","{0}","{0}","{0}")''')
            self.conn.commit()

        self.__admin = [j for i in self.cursor.execute(f'''select * from Admin''') for j in i]
        self.last_number,self.last_month,self.last_year = self.__admin[1],self.__admin[2],self.__admin[3]

    def mauns_update(self) -> bool:
        if (date.today().strftime("%-m%Y") != f'{self.last_month}{self.last_year}'):

            if self.last_month ==12:
                self.last_month = 1
                self.last_year += 1
            else:
                self.last_month += 1

            self.last_number += 1

            self.cursor.execute(f'''insert into показания 
            (Номер,Месяц_год ,Показания_Т1,Показания_Т2,Показания_горячей_воды,Показания_холодной_воды) 
            values 
            ("{self.last_number}","{self.month[self.last_month]}/{self.last_year}","{0}","{0}","{0}","{0}")''')

            self.cursor.execute(f'''update Admin set Номер_для_поиска = "{1}",
            Последний_номер_заполнения = "{self.last_number}",
            Последний_месяц_заполнения  = "{self.last_month}",
            Последний_год_заполнения = "{self.last_year}"''')

            self.conn.commit()

            return False
        else:
            return True


    def prints(self,numbers) ->str:

        ends = ''
        for i in reversed(range(self.last_number-numbers+1,self.last_number+1)):
            returns_print = list(map(str,[j for i in self.cursor.execute(f"""select * from показания where Номер = {i}""") for j in i]))
            ends += f"""{returns_print[1]}\n
            Показания Т1: {(8-len(returns_print[2]))*'0'+returns_print[2]}\n
            Показания Т2: {(8-len(returns_print[3]))*'0'+returns_print[3]}\n
            Показания горячей воды: {(9-len(returns_print[4]))*'0'+returns_print[4]}\n
            Показания холодной воды: {(9-len(returns_print[5]))*'0'+returns_print[5]}\n\n"""

        return ends

    def add_tone(self,masage:str) -> None:
        self.cursor.execute(f"UPDATE показания SET Показания_Т1 = '{masage}' WHERE Номер =  '{self.last_number}'")
        self.conn.commit()

    def add_ttwo(self,masage:str) -> None:
        self.cursor.execute(f"UPDATE показания SET Показания_Т2 = '{masage}' WHERE Номер =  '{self.last_number}'")
        self.conn.commit()

    def add_cullwather(self,masage:str) -> None:
        self.cursor.execute(f"UPDATE показания SET Показания_горячей_воды = '{masage}' WHERE Номер =  '{self.last_number}'")
        self.conn.commit()

    def add_firewather(self,masage:str) -> None:
        self.cursor.execute(f"UPDATE показания SET Показания_холодной_воды = '{masage}' WHERE Номер =  '{self.last_number}'")
        self.conn.commit()

    def analytics(self,period):
        #212121, #181818, #ff9800
        point = "o"
        color_point = "lime"
        color_line = "#ff9800"
        color_plot = '#181818'
        color_figure = '#212121'
        color_grtid = 'black'
        color_title = 'white'
        front_size_figure = 36
        front_size_plot = 20
        front_size_X = 16
        front_size_Y = 16
        fig,axs = plt.subplots(2,2,figsize = (28,14))
        fig.suptitle('Показания электроэнергии и воды',fontsize=front_size_figure)
        fig.set(facecolor = color_figure)
        
        dataset = np.array([],dtype=float)
        month = np.array([])
        for num in range(self.last_number-2*period+1,self.last_number+1):
            dataset = np.append(dataset,np.array([i for i in self.cursor.execute( f"""select 
            Показания_Т1,Показания_Т2,Показания_горячей_воды,Показания_холодной_воды from показания 
            where Номер = '{num}'""")][0]))
        for num in range(self.last_number-period+1,self.last_number+1):   
            month = np.append(month,"".join(re.findall(r'(\w*)[/]20(\d*)',[i for i in self.cursor.execute( f"""select Месяц_год from показания where Номер = '{num}'""")][0][0])[0]))
        dataset = dataset.reshape(-1,4)
        dataset_first = dataset[:period]
        dataset = dataset[period:]
        axs[0,0].plot(month,dataset[:,0],color = color_line)
        axs[0,0].set_title('Показания Т1 по месяцам',fontsize = front_size_plot,color = color_title)
        axs[0,0].set_xlabel('Период времени',fontsize = front_size_X,color = color_title)
        axs[0,0].set_ylabel('Значение Т1',fontsize = front_size_Y,color = color_title)
        axs[0,0].scatter(month,dataset[:,0],color = color_point, marker = point)
        axs[0,0].set(facecolor = color_plot)
        axs[0,0].grid(color=color_grtid)

        axs[1,0].plot(month,dataset[:,1],color = color_line)
        axs[1,0].set_title('Показания Т2 по месяцам',fontsize = front_size_plot,color = color_title)
        axs[1,0].set_xlabel('Период времени',fontsize = front_size_X,color = color_title)
        axs[1,0].set_ylabel('Значение Т2',fontsize = front_size_Y,color = color_title)
        axs[1,0].scatter(month,dataset[:,1],color = color_point, marker = point)
        axs[1,0].set(facecolor = color_plot)
        axs[1,0].grid(color=color_grtid)

        axs[0,1].plot(month,dataset[:,2],color = color_line)
        axs[0,1].set_title('Показания горячей воды по месяцам',fontsize = front_size_plot,color = color_title)
        axs[0,1].set_xlabel('Период времени',fontsize = front_size_X,color = color_title)
        axs[0,1].set_ylabel('Значение горячей воды',fontsize = front_size_Y,color = color_title)
        axs[0,1].scatter(month,dataset[:,2],color = color_point, marker = point)
        axs[0,1].set(facecolor = color_plot)
        axs[0,1].grid(color=color_grtid)

        axs[1,1].plot(month,dataset[:,3],color = color_line)
        axs[1,1].set_title('Показания холодной воды по месяцам',fontsize = front_size_plot,color = color_title)
        axs[1,1].set_xlabel('Период времени',fontsize = front_size_X,color = color_title)
        axs[1,1].set_ylabel('Значение холодной воды',fontsize = front_size_Y,color = color_title)
        axs[1,1].scatter(month,dataset[:,3],color = color_point, marker = point)
        axs[1,1].set(facecolor = color_plot)
        axs[1,1].grid(color=color_grtid)

        fig.savefig('Photo_stat.png')

        statistic = np.around(((np.sum(dataset - dataset[0],axis = 0)/(np.sum(dataset_first - dataset_first[0],axis = 0)))-1)*100,decimals=2)
        statistic = ''.join([f"""Статистика за последние указанный промежуток времени\n\n""" ,\
             f'Расход дневной электроэнергии увеличился на {statistic[0]}%\n' if statistic[0]>0 else f'Расход дневной электроэнергии уменьшился на {-1*statistic[0]}%\n',\
                f'Расход ночной электроэнергии увеличился на {statistic[1]}%\n' if  statistic[1]>0 else f'Расход ночной электроэнергии уменьшился на {-1*statistic[1]}%\n',\
                    f'Расход горячей воды увеличился на {statistic[2]}%\n' if  statistic[2]>0 else f'Расход горячей воды уменьшился на {-1*statistic[2]}%\n',\
                        f'Расход холодной воды увеличился на {statistic[3]}%\n' if  statistic[3]>0 else f'Расход холодной воды уменьшился на {-1*statistic[3]}%\n'])

        fig.clf()

        return statistic

    def del_photo(self):
        os.remove('Photo_stat.png')