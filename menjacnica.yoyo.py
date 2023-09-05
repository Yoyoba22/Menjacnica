import psycopg2 as pg
import pandas as pd
from tkinter import *
import tkinter as tk

root=Tk()
root.title('Menjacnica')

class Menjacnica:
    def __init__(self):
        self.con=pg.connect(
            database='Menjacnica',
            host='localhost',
            port='5432',
            user='postgres',
            password='Yoyoba22'
            )
        self.upit=None
        self.transakcija=None
        self.konvertovano=None
        self.valuta_df=None
        self.valuta=None
    
    def get_transakcije(self):
        self.transakcija=pd.read_sql_query('''SELECT * FROM Transakcija
                                        ORDER BY sifra_transakcije''',self.con)
        return self.transakcija
    
 

    def konvertuj(self,iz_koje_valute,u_valutu,iznos_konvertovano):
        self.get_transakcije()
        cursor=self.con.cursor()
        sifra_transakcije=int(self.transakcija.iloc[-1,0])+1 if len(self.transakcija)>0 else 1
        iz_koje_valute = selected_valuta1.get()
        u_valutu = selected_valuta2.get()
        query="INSERT INTO Transakcija (sifra_transakcije,iz_koje_valute,u_valutu,iznos_konvertovano,iznos_posle_konverzije) VALUES (%s, %s, %s, %s, '0')"
        vrednosti=(sifra_transakcije,iz_koje_valute,u_valutu,iznos_konvertovano,)
        cursor.execute(query,vrednosti)
        self.con.commit()
        cursor.close()
        self.update_konvertovano()
        message()
        updated_iznos_posle_konverzije = self.retrieve_updated_iznos_posle_konverzije(sifra_transakcije)
        e2.delete(0, 'end')  # Clear the current value
        e2.insert(0, str(updated_iznos_posle_konverzije))  # Insert the new value
    
    def retrieve_updated_iznos_posle_konverzije(self, sifra_transakcije):
        cursor = self.con.cursor()
        query = '''SELECT iznos_posle_konverzije FROM Transakcija WHERE sifra_transakcije = %s'''
        cursor.execute(query, (sifra_transakcije,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            return result[0]
        else:
            return 0.0
    

    def update_konvertovano(self):
        cursor=self.con.cursor()
        query='''UPDATE Transakcija t
                SET iznos_posle_konverzije =
                  CASE
                    WHEN t.u_valutu != 'DIN' THEN t.iznos_konvertovano / k.iznos_valute_dinar
                    WHEN t.iz_koje_valute != 'DIN' THEN t.iznos_konvertovano * k.iznos_valute_dinar
                    ELSE t.iznos_posle_konverzije -- Optionally, handle the 'DIN' case here
                END
            FROM Kursna_lista k
            WHERE (t.u_valutu != 'DIN' AND k.valute = t.u_valutu) OR
            (t.iz_koje_valute != 'DIN' AND k.valute = t.iz_koje_valute);'''
        cursor.execute(query)
        self.con.commit()
        cursor.close()


    def get_sql(self,query):
        self.upit=pd.read_sql_query(query,self.con)
    
    def export_excel(self,naziv_fajla,kolone):
        self.upit.to_excel(naziv_fajla,index=False)

    def get_valute(self):
        self.valuta_df=pd.read_sql_query('''
            SELECT valute FROM Kursna_lista''',self.con)
        self.valuta=self.valuta_df['valute'].astype(str)
        return self.valuta


M=Menjacnica()


def export_selected(choice):
    if choice == 'Kursna lista':
        execute_query('''
                SELECT * FROM Kursna_lista''', 'kursna_lista.xlsx', ['valute', 'iznos_valute', 'iznos_valute_dinar'])
        message1()    
    elif choice == 'Transakcije':
        execute_query('''
                SELECT * FROM Transakcija
                ORDER BY sifra_transakcije''', 'transakcije.xlsx', ['sifra_transakcije', 'iz_koje_valute', 'u_valutu', 'iznos_konvertovano', 'iznos_posle_konverzije'])
        message2()

def execute_query(query, naziv_fajla, kolone):
    M.get_sql(query)
    M.export_excel(naziv_fajla, kolone)

izabrana_vrednost = StringVar()
izabrana_vrednost.set('Kursna lista')

menubar = Menu(root)
export_menu = Menu(menubar, tearoff=0)
export_menu.add_command(label='Kursna lista', command=lambda: export_selected('Kursna lista'))
export_menu.add_command(label='Transakcije', command=lambda: export_selected('Transakcije'))
menubar.add_cascade(label='Export', menu=export_menu)
root.config(menu=menubar)

global selected_valuta1,selected_valuta2
def update_dropdowns(*args):
    valuta1 = selected_valuta1.get()
    valuta2 = selected_valuta2.get()

    if valuta2 != "DIN":
        valute_without_din = [valuta for valuta in valute if valuta != "DIN"]
        selected_valuta1.set("DIN")
        dropdown_valuta1['menu'].delete(0, 'end')
        for val in valute_without_din:
            dropdown_valuta1['menu'].add_command(label=val, command=tk._setit(selected_valuta1, val))

    if valuta1 != "DIN":
        valute_without_din = [valuta for valuta in valute if valuta != "DIN"]
        selected_valuta2.set("DIN")
        dropdown_valuta2['menu'].delete(0, 'end')
        for val in valute_without_din:
            dropdown_valuta2['menu'].add_command(label=val, command=tk._setit(selected_valuta2, val))

l = Label(root, text='Menjacnica')
l.grid(row=0, column=1, columnspan=2)
l1 = Label(root, text='Iz Valute:')
l1.grid(row=2, column=0)
e1 = Entry(root)
e1.grid(row=3, column=0)
l2 = Label(root, text='U Valutu:')
l2.grid(row=2, column=3)
e2 = Entry(root)
e2.grid(row=3, column=3)

b = Button(root, text='Konvertuj', command=lambda: M.konvertuj(selected_valuta1.get(), selected_valuta2.get(), e1.get()))
b.grid(row=10, column=1, columnspan=2)
valute = M.get_valute()

selected_valuta1 = StringVar(root)
selected_valuta2 = StringVar(root)

selected_valuta1.set(valute[0])
selected_valuta2.set("DIN")

dropdown_valuta1 = OptionMenu(root, selected_valuta1, *valute)
dropdown_valuta1.grid(row=3, column=1)
dropdown_valuta2 = OptionMenu(root, selected_valuta2, *valute)
dropdown_valuta2.grid(row=3, column=4)

selected_valuta1.trace_add("write", update_dropdowns)
selected_valuta2.trace_add("write", update_dropdowns)



def message():
    t=Toplevel()
    l=Label(t,text='Konverzija uspesna')
    l.pack()

def message1():
    t=Toplevel()
    l=Label(t,text='Kursna_lista.xlsx uspesno exportovana')
    l.pack()

def message2():
    t=Toplevel()
    l=Label(t,text='Transakcije.xlsx uspesno exportovane')
    l.pack()









mainloop()
