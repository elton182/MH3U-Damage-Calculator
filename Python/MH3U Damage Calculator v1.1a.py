import tkinter as tk
from tkinter import ttk
from tkinter import font
import sys

#Press F5 to run

"""
MH3U Damage Calculator v. 1.0
created by EphemeralRain
"""

class MH3Ucalc(ttk.Frame):
    """
    MH3U Damage Calculator processes the most damaging weapons of a given type
    for any given monster. This program has the following dependancies:

    Python 3.3
    wepmod.txt
    weapons.csv
    monsters.csv

    ==========================================================================

    Lines of wepmod.csv should be of the following form:

    Two letter weapon code, weapon attack multiplier, weapon modifier
    HM, 75, 5.2

    Lines of weapons.csv should be of the following form:
    
    Two letter weapon code, Weapon Name, Damage, Affinity, Element Damage, Element Type, Base Sharpness, Sharp+1
    GS,Devastator Blade,1200,0,(410),Ice,W,P,

    Note that weapons with awaken should have their elemental damage in parentheses.

    Lines from monsters.csv should be of the following form:

    Name, Slash Defense, Blunt Defense, Fire D, Water D, Ice D, Thunder D, Dragon D
    Arzuros,44.4,44.4,20,5,18,13,0

    ===========================================================================

    This program makes the following assumptions in calculating damage:

    1. All weapons are given an average attack multiplier instead of a
       multiplier for each attack. This is done to simplify the program.
       If you disagree with the averages I chose, modify the values in
       wepmod.txt.

       Note that these values, in my opinion, represent the general attacks
       you will use. I excluded attacks that are weak and used infrequently.

    2. All monsters are given an average defense instead of a defense per
       zone. This is done to simplify the calculations. These values should
       represent the average damage you do to a monster - I weighted higest
       the zones which are hit frequently and weakest to damage, and excluded
       those infrequently hit or always avoided due to high defense.

    3. Due to the nature of the ranking, status weapons aren't well represented.
       This is due to the difficulty in ranking the efficacy of poison, etc as
       a value.

    4. I couldn't find exact values for the other SA vials (poison, dragon). I
       assumed they functioned as free awaken in sword mode.

    5. If anyone has accurate values for Dire Miralis, please forward them to me.

    6. Average damage increase from affinity is accounted for.

    7. Not all weapons are included because I copied them all by hand after
       I couldn't find a nice bundled resource with the data. Only final stages
       of weapons are included for now; weapons that are obviously bad aren't
       included.

       If anyone can point me to a resource that I can easily extract all
       weapon and monster information from, I will gladly enhance the program
       to use all available information.
    """
    
    def __init__(self, master = None):
        """
        Initialize variables and strings for use in damage calculation
        and drop down menus.
        """

        self.results_str = ''
        
        #CheckBox Variables
        self.sharpvar  = tk.IntVar()
        self.awakenvar = tk.IntVar()
        self.pcharm    = tk.IntVar()
        self.ptalon    = tk.IntVar()
        self.statusvar = tk.IntVar()

        #Sharpness Dictionary
        self.sharp      = dict()
        self.sharp["G"] = (1.05, 1     )
        self.sharp["B"] = (1.20, 1.0625)
        self.sharp["W"] = (1.32, 1.125 )
        self.sharp["P"] = (1.44, 1.2   )
    
        #Values for drop down boxes
        self.ddrug = tk.StringVar()
        self.ddrug.set("None")
        self.doptions = ("None", "Demondrug","Mega Demondrug",\
                         "Kitchen S", "Kitchen L")
        
        self.mseed = tk.StringVar()
        self.mseed.set("None")
        self.moptions = ("None", "Might Seed","Demon Flute", "Might Pill")

        self.eleup = tk.StringVar()
        self.eleup.set("None")
        self.eleop = ("None","All +1","All +2","Fire +1","Fire +2",\
                      "Water +1","Water +2","Ice +1","Ice +2",\
                      "Thunder +1","Thunder +2","Dragon +1", "Dragon+2")

        self.atkup = tk.StringVar()
        self.atkup.set("None")
        self.atkop = ("None", "Attack Up S",\
                      "Attack Up M","Attack Up L")

        self.critup = tk.StringVar()
        self.critup.set("None")
        self.critop = ("None", "Critical Eye +1","Critical Eye +2",\
                       "Critical Eye +3")

        self.challenge = tk.StringVar()
        self.challenge.set("None")
        self.challop = ("None", "Challenger +1", "Challenger +2",\
                        "Latent Power +1","Latent Power +2",\
                        "Peak Performance")

        self.adren = tk.StringVar()
        self.adren.set("None")
        self.adrenop = ("None", "Adrenaline +2", "Felyne Heroics")

        self.fortify = tk.StringVar()
        self.fortify.set("None")
        self.fortop = ("None","1 Death","2 Deaths")
        

        #Relate weapons to weapon keys
        self.wepkey = {"Dual Blades":"DB","Greatsword":"GS", "Gunlance":"GL", \
                        "Hammer":"HM", "Hunting Horn":"HH", "Lance":"LN", \
                        "Longsword":"LS", "Switch Axe":"SA", "Sword and Shield":"SS"}

        #Import monster and weapons from outside files
        self.importMonsters()
        self.importWeapons()

        self.currentwep = tk.StringVar()
        self.currentwep.set("Sword and Shield")

        self.currentmon = tk.StringVar()
        self.currentmon.set("Great Jaggi")
        self.monlist = tuple(sorted(self.monsters.keys()))

        #Initialize tk window framework
        tk.Frame.__init__(self,master)

        #Initialize Font Choices
        self.my_font = font.Font(family="Courier New", size = 10)
        self.my_font2 = font.Font(family="Courier New", size = 12)
        
        s = ttk.Style()
        s.configure('.', font = self.my_font)
        s.configure('H.TLabel', font = self.my_font2)
        self.master.title("MH3U Damage Calculator")

        #Initialize grid, pad widths, create widgets
        self.grid()
        self.rowconfigure(2, pad=30)
        self.columnconfigure(2, pad=100)
        self.columnconfigure(3, pad=75)
        self.createWidgets()

    def createWidgets(self):
        """Create user interface"""
        #Options header
        self.optlab = ttk.Label(self, text = "Options",\
                                background = "dark grey",\
                                anchor=tk.CENTER, style = 'H.TLabel')
        self.optlab.grid(row = 0, column = 0, columnspan = 5, ipady=6,sticky="nsew")
        self.optsep = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.optsep.grid(row=1,column=0,columnspan=15, sticky= "ews")
        
        #Dropboxes
        self.wepframe = ttk.LabelFrame(self, text = "Current Weapon")
        self.wepframe.grid(column = 1, row = 2, columnspan = 2, sticky=tk.S)
        self.wepbox = ttk.Combobox(self.wepframe, textvariable=self.currentwep,\
                                   values=sorted(self.wepkey.keys()))
        self.wepbox.grid()
        
        self.monlabel = ttk.LabelFrame(self, text="Current Monster")
        self.monlabel.grid(row=2,column=3,columnspan=2,sticky=tk.SW)
        self.monbox = ttk.Combobox(self.monlabel,textvariable=self.currentmon,\
                                   values=self.monlist)
        self.monbox.grid()
        
        self.dlabel = ttk.LabelFrame(self,text="Demon Buffs")
        self.dlabel.grid(row=4,column=1,columnspan=2)
        self.ddrugbox = ttk.Combobox(self.dlabel,textvariable=self.ddrug,\
                                     values=self.doptions)
        self.ddrugbox.grid()

        self.mlabel = ttk.LabelFrame(self, text="Might Buffs")
        self.mlabel.grid(row=4,column=3,columnspan=2,sticky='w')
        self.mseedbox = ttk.Combobox(self.mlabel, textvariable=self.mseed,\
                                     values=self.moptions)
        self.mseedbox.grid()

        self.alabel = ttk.LabelFrame(self, text="Attack Up")
        self.alabel.grid(row=5,column=1,columnspan=2)
        self.atkbox = ttk.Combobox(self.alabel, textvariable=self.atkup,\
                                   values=self.atkop)
        self.atkbox.grid()

        self.clabel = ttk.LabelFrame(self, text="Critical Eye")
        self.clabel.grid(row=5,column=3,columnspan=2,sticky='w')
        self.critbox = ttk.Combobox(self.clabel, textvariable=self.critup,\
                                    values=self.critop)
        self.critbox.grid()

        self.elabel = ttk.LabelFrame(self, text="Element Up")
        self.elabel.grid(row=6,column=1,columnspan=2)
        self.elebox = ttk.Combobox(self.elabel, textvariable=self.eleup,\
                                   values=self.eleop)
        self.elebox.grid()
        
        self.fortframe = ttk.LabelFrame(self, text = "Fortify")
        self.fortframe.grid(column = 3, row = 6, columnspan = 2, sticky='w')
        self.fortbox = ttk.Combobox(self.fortframe, textvariable=self.fortify,\
                                    values =self.fortop)
        self.fortbox.grid()

        self.adrenframe = ttk.LabelFrame(self, text = "Adrenaline")
        self.adrenframe.grid(column = 1, row = 7, columnspan = 2)
        self.adrenbox = ttk.Combobox(self.adrenframe, textvariable=self.adren,\
                                     values =self.adrenop)
        self.adrenbox.grid()

        self.chalframe = ttk.LabelFrame(self, text = "Challenger")
        self.chalframe.grid(column = 3, row = 7, columnspan = 2, sticky = 'w')
        self.chalbox = ttk.Combobox(self.chalframe, textvariable=self.challenge,\
                                    values =self.challop)
        self.chalbox.grid()

        #Checkboxes
        self.sharpplus = ttk.Checkbutton(self, width=10, text='Sharp+1',\
                                         variable=self.sharpvar)
        self.sharpplus.grid(column=2, row=8, sticky='e')

        self.awaken = ttk.Checkbutton(self, width=10, text='Awaken',\
                                      variable=self.awakenvar)
        self.awaken.grid(column=2, row=9, sticky='e')

        self.charm = ttk.Checkbutton(self, text='Powercharm',\
                                     variable=self.pcharm)
        self.charm.grid(column = 3, row = 8, sticky='w')

        self.talon = ttk.Checkbutton(self, text='Powertalon',\
                                     variable=self.ptalon)
        self.talon.grid(column=3, row=9, sticky='w')

        self.status = ttk.Checkbutton(self, text = "Show Status List",\
                                      variable = self.statusvar,width=20)
        self.status.grid(column = 2, row = 10, columnspan = 2)

        #Results window
        self.restabs = ttk.Notebook(self)
        self.restabs.grid(row=0, column=10, rowspan=26)
        
        self.results = tk.Text(self.restabs, height=26, width = 60)
        self.results.grid()
        self.presults1 = tk.Text(self.restabs, height=26, width=60)
        self.presults1.grid()
        self.presults2 = tk.Text(self.restabs, height=26, width=60)
        self.presults2.grid()
        self.presults3 = tk.Text(self.restabs, height=26, width=60)
        self.presults3.grid()
        self.presults4 = tk.Text(self.restabs, height=26, width=60)
        self.presults4.grid()
        
        self.separator = ttk.Separator(self, orient=tk.VERTICAL)
        self.separator.grid(column = 5, row=0, rowspan = 30, sticky = 'ns')

        self.restabs.add(self.results, text="Current Results")
        self.restabs.add(self.presults1, text="Previous 1")
        self.restabs.add(self.presults2, text="Previous 2")
        self.restabs.add(self.presults3, text="Previous 3")
        self.restabs.add(self.presults4, text="Previous 4")
        

        #Calculate Button
        self.calculate = ttk.Button(self, text='Calculate',
                                    command = self.prep_calc)
        self.calculate.grid(row = 12, column = 2, columnspan=2)

        #Credits label
        self.credits = ttk.Label(self, text = "created by EphemeralRain")
        self.credits.grid(row = 13, column = 2, columnspan = 2,sticky='s',\
                          pady=20)
    
    def importMonsters(self):
        """Import monster information from .csv file"""
        
        self.monsters = dict()
        monsterfile = open("monsters.csv")
        monsterfile.readline()
        for line in monsterfile:
            line = line.strip().split(',')
            self.monsters[line[0]] = line[1:]

        monsterfile.close()

    def importWeapons(self):
        """Import weapon information from .csv and .txt files"""
        self.weplist = dict()
        wepfile = open("weapons.csv")
        wepfile.readline()
        for line in wepfile:
            line = line.strip().split(',')
            if line[0] in self.weplist:
                self.weplist[line[0] ].append(tuple(line[1:]))
            else:
                self.weplist[line[0] ] = [tuple(line[1:])]
                
        wepfile.close()
        
        self.wepmod = dict()
        modfile = open("wepmod.txt")
        for line in modfile:
            line = line.strip().split(',')
            self.wepmod[ line[0] ] = tuple(line[1:])

        modfile.close()

    def verifyValue(self,val,options):
        v = val.get()
        for ele in options:
            if v.lower() == ele.lower()[:len(v)]:
                val.set(ele)
                break
        else:
            val.set(options[0])

    def shiftResults(self):
        self.presults4.delete('1.0', 'end')
        self.presults4.insert('1.0', self.presults3.get('1.0','end'))
        self.presults3.delete('1.0', 'end')
        self.presults3.insert('1.0', self.presults2.get('1.0','end'))
        self.presults2.delete('1.0', 'end')
        self.presults2.insert('1.0', self.presults1.get('1.0','end'))
        self.presults1.delete('1.0', 'end')
        self.presults1.insert('1.0', self.results.get('1.0','end'))
        self.results.delete('1.0','end')
        self.results.insert('1.0',self.results_str)
        
        
    def prep_calc(self):
        """
        Prepare information for damage calculation that is not specific to
        individual weapons
        """
        
        self.verifyValue(self.currentwep, sorted(self.wepkey.keys()))
        self.verifyValue(self.currentmon, self.monlist)
        self.verifyValue(self.ddrug, self.doptions)
        self.verifyValue(self.mseed, self.moptions)
        self.verifyValue(self.atkup, self.atkop)
        self.verifyValue(self.critup, self.critop)
        self.verifyValue(self.eleup, self.eleop)
        self.verifyValue(self.fortify, self.fortop)
        self.verifyValue(self.adren, self.adrenop)
        self.verifyValue(self.challenge, self.challop)
        
        #Extract monster and weapon key
        self.cur_wep = self.wepkey[self.currentwep.get()]
        self.wep_mod = float(self.wepmod[self.cur_wep][1])
        self.atk_mod = float(self.wepmod[self.cur_wep][0])
        self.cur_mon = self.monsters[self.currentmon.get()]

        #Get weaknesses
        if self.cur_wep in ["HH", "HM"]:
            self.hitzone = float(self.cur_mon[1])
        else:
            self.hitzone = float(self.cur_mon[0])

        self.elezone = dict()
        self.elezone["Fir"] = float(self.cur_mon[2])
        self.elezone["Wat"] = float(self.cur_mon[3])
        self.elezone["Ice"] = float(self.cur_mon[4])
        self.elezone["Thu"] = float(self.cur_mon[5])
        self.elezone["Dra"] = float(self.cur_mon[6])
        
        #Demondrug Modifier
        if self.ddrug.get() in ["Demondrug","Kitchen S"]:
            drugmod = 3
        elif self.ddrug.get() in ["Mega Demondrug", "Kitchen L"]:
            drugmod = 5
        else:
            drugmod = 0

        #Might Modifier
        if self.mseed.get() in ["Might Seed", "Demon Flute"]:
            pillmod = 10
        elif self.mseed.get() == "Might Pill":
            pillmod = 25
        else:
            pillmod = 0
        
        #Attack up Modifier
        if self.atkup.get()[-1] == 'S':
            atkmod = 10
        elif self.atkup.get()[-1] == 'M':
            atkmod = 15
        elif self.atkup.get()[-1] == 'L':
            atkmod = 20
        else:
            atkmod = 0

        #Critical Eye Modifier
        if self.critup.get()[-1] == '1':
            self.base_crit = 10
        elif self.critup.get()[-1] == '2':
            self.base_crit = 20
        elif self.critup.get()[-1] == '3':
            self.base_crit = 30
        else:
            self.base_crit = 0

        #Charm/Talons
        if self.pcharm.get() == 1:
            charmmod = 6
        else:
            charmmod = 0

        if self.ptalon.get() == 1:
            talonmod = 9
        else:
            talonmod = 0

        #Challenger Class Buff
        if self.challenge.get() == "Challenger +1":
            chalaff = 10
            chalmod = 10
        elif self.challenge.get() == "Challenger +2":
            chalaff = 20
            chalmod = 25
        elif self.challenge.get() == "Latent Power +1":
            chalaff = 30
            chalmod = 0
        elif self.challenge.get() == "Latent Power +2":
            chalaff = 50
            chalmod = 0
        elif self.challenge.get() == "Peak Performance":
            chalaff = 0
            chalmod = 20
        else:
            chalaff = 0
            chalmod = 0

        #Fortify Buff
        fort = self.fortify.get()
        if fort == "1 Death":
            self.fortmod = 10
        elif fort == "2 Deaths":
            self.fortmod = 20
        else:
            self.fortmod = 0

        #Adrenaline Class
        adre = self.adren.get()
        if adre == "Adrenaline +2":
            self.adremul = 30
        elif adre == "Felyne Heroics":
            self.adremul = 35
        else:
            self.adremul = 0
            
            
        #Element up modifier
        self.element = 'None'
        if self.eleup.get() != 'None':
            elem = self.eleup.get().split()
            if elem[1][-1] == '1':
                self.elemod = 10
            elif elem[1][-1] == '2':
                self.elemod = 20
            else:
                self.elemod = 0
            self.element = elem[0][:3]

        #sharp/awaken toggles
        self.sharpon = self.sharpvar.get() == 1
        self.awakenon = self.awakenvar.get() == 1

        #Calculate base attack from buffs
        self.base_attack = self.wep_mod*(drugmod+pillmod+atkmod\
                                         + charmmod + talonmod + \
                                         chalmod)
        self.base_crit += chalaff
        
        #Calculate and display damage
        self.calculate_damage()
        self.update_output()
        
        

    def calculate_damage(self):
        """
        Calculate final damage for all included weapons.
        Creates a list of weapons sorted from highest to
        lowest damage.
        """

        #Initialize final list and get all weapons of current type
        self.weapon_scores = []
        self.status_scores = []
        weapons = self.weplist[self.cur_wep]

        for weapon in weapons:
            
            #Get final attack/affinity values
            attack = self.base_attack + int(weapon[1])
            affinity = self.base_crit + int(weapon[2])

            if affinity > 100:
                affinity = 100

            #Extract elemental damage info
            elevial = False
            awaken = False
            if weapon[3].isdigit():
                element = int(weapon[3])
            elif self.awakenon:
                awaken = True
                element = int(weapon[3][1:-1])
            elif self.cur_wep == "SA":
                if weapon[-1] == weapon[4]:
                    element = int(weapon[3][1:-1])
                    elevial = True
            else:
                element = 0
                awaken = True

            #Get weapon element type
            eletype = weapon[4]

            #Extract sharpness multipliers
            if self.sharpon:
                sharp = self.sharp[ weapon[6]][0]
                elesharp = self.sharp[ weapon[6]][1]
            else:
                sharp = self.sharp[ weapon[5]][0]
                elesharp = self.sharp[ weapon[5]][1]

            #Calculate base physical damage; adjust for affinity/buffs
            if weapon[0] == "Agnaktor Inferno":
                print(attack, self.atk_mod, sharp, self.hitzone, self.wep_mod)
            phys_damage = (attack * self.atk_mod/100 \
                           * sharp * self.hitzone/100) / self.wep_mod

            phys_damage *= 1+(affinity/100*0.25)
            phys_damage *= 1+self.adremul/100
            phys_damage *= 1+self.fortmod/100
                
            #Calculate elemental damage
            status = False
            try:
                ele_damage = self.elezone[eletype]/100 \
                             * element * elesharp / 10
            except KeyError:
                status = True
                ele_damage = 0

            if self.element == eletype or self.element == "All":
                ele_damage *= 1+self.elemod/100

            if self.cur_wep == "SA":
                if weapon[-1] == "Pow":
                    phys_damage *= 1.2
                elif weapon[-1] == "Ele":
                    ele_damage *= 1.25
                name = "{:<21s}{:>3s}".format(weapon[0], weapon[-1])
            else:
                name = weapon[0]

            total_damage = phys_damage + ele_damage

            if awaken:
                eletype = '(' + eletype + ')'
            elif elevial:
                eletype = "V: " + eletype

            #Return all information on weapon
            if status:
                weapon_tuple = total_damage, name, eletype, phys_damage, element
            else:
                weapon_tuple = total_damage, name, eletype, phys_damage, ele_damage

            self.weapon_scores.append(weapon_tuple)
            if status:
                self.status_scores.append(weapon_tuple)

        self.status_scores.sort(reverse = True)
        self.weapon_scores.sort(reverse = True)

    def update_output(self):
        """
        Prints out the top weapons for the current setup.
        Copies previous results to secondary window for quick compare.
        """
        
        format_string = "|{:<24s}|{:>6s}|{:>11.2f}|{:>8.2f}|{:>5d}|\n"
        format_string2 = "|{:<24s}|{:>6s}|Stat:{:>6d}|{:>8.2f}|{:>5d}|\n"
        header_string = "|{:^24s}|{:>6s}|{:>11s}|{:>8s}|{:>5s}|\n"
        out_string = ""

        if self.sharpon:
            sharp = "Yes"
        else:
            sharp = "No"

        if self.awakenon:
            awake = "Yes"
        else:
            awake = "No"

        if self.pcharm.get():
            charm = "Yes"
        else:
            charm = "No"

        if self.ptalon.get():
            talon = "Yes"
        else:
            talon = "No"     
        
        summary = self.currentwep.get() + " vs. " + self.currentmon.get()
        out_string += '='*60 + '\n'
        out_string += "{:^60s}\n".format(summary)
        out_string += '='*60 + '\n'
        out_string += "  Demon       : {:<14s} Might     : {:<12s}\n".format(self.ddrug.get(),self.mseed.get())
        out_string += "  Attack Up   : {:<14s} Crit Eye  : {:<15s}\n".format(self.atkup.get(),self.critup.get())
        out_string += "  Element Up  : {:<14s} Fortify   : {:<15s}\n".format(self.eleup.get(), self.fortify.get())
        out_string += "  Adrenaline  : {:<14s} Challenger: {:<15s}\n".format(self.adren.get(), self.challenge.get())
        out_string += "  Sharpness +1: {:<14s} Pow Charm : {:<10s}\n".format(sharp, charm)
        out_string += "  Awaken      : {:<14s} Pow Talon : {:<10s}\n".format(awake,talon)
        out_string += '='*60 + '\n'
        

        if self.statusvar.get():
            length = 6
            status = True
            out_string += "|{:^58s}|\n".format("Highest Damage Weapons")
        else:
            length = 15
            status = False
            
        out_string += header_string.format("Weapon","Type","Ele Dmg","Phy Dmg","Dmg")
        
        for i in range(length):
            wep = self.weapon_scores[i]
            if type(wep[4]) == int:
                line = format_string2.format(wep[1],wep[2],wep[4],wep[3],int(wep[0]))
            else:
                line = format_string.format(wep[1],wep[2],wep[4],wep[3],int(wep[0]))
            out_string += line

        if status:
            out_string += '='*60 + '\n'
            out_string += "|{:^58s}|\n".format("Highest Damage Status Weapons")
            out_string += header_string.format("Weapon Name","Type","Ele Dmg","Phy Dmg","Dmg")
            for i in range(5):
                try:
                    wep = self.status_scores[i]
                except IndexError:
                    break
                if type(wep[4]) == int:
                    line = format_string2.format(wep[1],wep[2],wep[4],wep[3],int(wep[0]))
                else:
                    line = format_string.format(wep[1],wep[2],wep[4],wep[3],int(wep[0]))
                out_string += line
                
        out_string = out_string.strip()
        self.results_str = out_string
        self.shiftResults()
        self.restabs.select(0)


root = tk.Tk()
calc = MH3Ucalc(master=root)
calc.mainloop()
