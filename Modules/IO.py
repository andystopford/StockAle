import sys, os.path
from PyQt4 import QtCore, QtGui
import xml.etree.ElementTree as ET
sys.path.append("./Modules")
from ingredients import*
from Model import*

class IO:
    def __init__(self, parent):
        """ Utility to handle all file input/output."""
        self.parent = parent
        self.month_to_num = dict(Jan=1, Feb=2, Mar=3, Apr=4, May=5, Jun=6,
                                 Jul=7, Aug=8, Sep=9, Oct=10, Nov=11, Dec=12)

    def get_path(self):
        """Gets path to data folder from prefs.xml preferences file"""
        with open('./prefs.xml', 'r') as fo:
            tree = ET.ElementTree(file=fo)
            root = tree.getroot()
            for elem in root.iter():
                if elem.tag == 'Path':
                    path = elem.text + '/'
                    return path

    def open_brews(self):
        """Open brew data"""
        try:
            path = self.get_path()
            if path:
                brew_path = path + 'Brews/'
                brew_list = []
                for brewFile in os.listdir(brew_path):
                    if not brewFile.startswith('.'): # filter unix hidden files
                        day = int(brewFile[0:2])
                        month = str(brewFile[2:5])
                        year = int('20' + brewFile[5:7])
                        if year not in self.parent.model_dict:
                            model = Model(self.parent)
                            model.setup()
                            model.set_year(year)
                            self.parent.model_dict[year] = model
                        month = self.month_to_num[month]
                        date = QtCore.QDate(year, month, day)
                        model = self.parent.model_dict[year]
                        model.add_brew(date)
        except:
            print('Brew data not found')

    def save_data(self):
        """ Save stock data, with backup of previous save."""
        root = ET.Element('Root')
        stock = ET.SubElement(root, 'Stock')
        grain = ET.SubElement(stock, 'Grain')
        hop = ET.SubElement(stock, 'Hop')
        for item in self.parent.grain_list:
            name = item.get_name()
            name = str(name)
            name = name.replace(' ', '_')
            name = ET.SubElement(grain, name)
            ebc = str(item.get_ebc())
            ebc = "_" + ebc
            ebc = ET.SubElement(name, ebc)
            extr = str(item.get_extr())
            extr = "_" + extr
            extr = ET.SubElement(name, extr)
            wgt = str(item.get_wgt())
            wgt = "_" + wgt
            wgt = ET.SubElement(name, wgt)
        for item in self.parent.hop_list:
            name = item.get_name()
            name = str(name)
            name = name.replace(' ', '_')
            name = ET.SubElement(hop, name)
            alpha = str(item.get_alpha())
            alpha = "_" + alpha
            alpha = ET.SubElement(name, alpha)
            wgt = str(item.get_wgt())
            wgt = "_" + wgt
            wgt = ET.SubElement(name, wgt)

        path = self.get_path()
        # Remove previous backup (if present):
        if os.path.isfile("{0}BAK_stockData.xml".format(path)):
            os.remove("{0}BAK_stockData.xml".format(path))
        # Backup previous file as BAK_stockData.xml and write new file:
        if os.path.isfile("{0}stockData.xml".format(path)):
            os.rename("{0}stockData.xml".format(path), "{0}BAK_stockData.xml".
                      format(path))
        # Write the tree:
        with open("{0}stockData.xml".format(path), "wb") as fo:
            tree = ET.ElementTree(root)
            tree.write(fo)
        self.parent.stock_dirty = False

    def load_data(self):
        """Loads stock data into application"""
        try:
            path = self.get_path()
            with open("{0}stockData.xml".format(path), "a"):
                tree = ET.ElementTree(file="{0}stockData.xml".format(path))
                root = tree.getroot()
                for elem in root.iter():
                    if elem.tag == 'Grain':
                        for grain in elem:
                            grain_data = []
                            for data in grain:
                                data = data.tag[1:]
                                grain_data.append(data)
                            grainName = grain.tag.replace('_', ' ')
                            a_grain = Grain(grainName, grain_data[0],
                                            grain_data[1], grain_data[2])
                            self.parent.grain_list.append(a_grain)
                        self.parent.grain_table_update()
                    if elem.tag == 'Hop':
                        for hop in elem:
                            hop_data = []
                            for data in hop:
                                data = data.tag[1:]
                                hop_data.append(data)
                            hop_name = hop.tag.replace('_', ' ')
                            a_hop = Hop(hop_name, hop_data[0], hop_data[1], 0)
                            self.parent.hop_list.append(a_hop)
                        self.parent.hop_table_update()
        except:
            self.parent.error_message("No Stock Data Found")

    def save_notes(self):
        """ Save notes, style and rating from selected brew."""
        proc_note = self.parent.ui.process_notes.toPlainText()
        style = str(self.parent.ui.box_style.currentText())
        taste = self.parent.ui.tasting_notes.toPlainText()
        rating = str(self.parent.ui.rating.value())
        brew_path = self.get_path() + 'Brews/'
        try:
            path = brew_path + self.parent.recipe_filename
            tree = ET.parse(path)
            root = tree.getroot()
            for elem in root.iter('Process'):
                elem.text = str(proc_note)
            for elem in root.iter('Style'):
                elem.text = style
            for elem in root.iter('Tasting'):
                elem.text = str(taste)
            for elem in root.iter('Rating'):
                elem.text = rating
            tree.write(path)
        except TypeError:
            # Event filter(?) causes exceptionj at start-up
            print('No recipe filename set')

    def save_brew(self, fname, date):
        """ Save brew and enable Commit button if brew date is today or
        in the past.
        """
        root = ET.Element('Root')
        ingredient = ET.SubElement(root, 'Ingredient')
        notes = ET.SubElement(root, 'Notes')
        grain = ET.SubElement(ingredient, 'Grain')
        hop = ET.SubElement(ingredient, 'Hops')
        params = ET.SubElement(root, 'Params')
        temp = ET.SubElement(params, 'Temp')
        eff = ET.SubElement(params, 'Eff')
        vol = ET.SubElement(params, 'Vol')
        results = ET.SubElement(root, 'Results')
        EBU = ET.SubElement(results, 'EBU')
        EBC = ET.SubElement(results, 'EBC')
        OG = ET.SubElement(results, 'OG')
        proc_note = ET.SubElement(notes, 'Process')
        taste_note = ET.SubElement(notes, 'Tasting')
        style = ET.SubElement(notes, 'Style')
        rating = ET.SubElement(notes, 'Rating')
        for item in self.parent.used_grain_list:
            name = item.get_name()
            name = str(name)
            name = name.replace(' ', '_')
            name = ET.SubElement(grain, name)
            ebc = str(item.get_ebc())
            ebc = "_" + ebc
            ebc = ET.SubElement(name, ebc)
            extr = str(item.get_extr())
            extr = "_" + extr
            extr = ET.SubElement(name, extr)
            wgt = str(item.get_wgt())
            wgt = "_" + wgt
            wgt = ET.SubElement(name, wgt)
        for item in self.parent.used_hop_list:
            name = item.get_name()
            name = str(name)
            name = name.replace(' ', '_')
            name = ET.SubElement(hop, name)
            alpha = str(item.get_alpha())
            alpha = "_" + alpha
            alpha = ET.SubElement(name, alpha)
            wgt = str(item.get_wgt())
            wgt = "_" + wgt
            wgt = ET.SubElement(name, wgt)
            time = str(item.get_time())
            time = "_" + time
            time = ET.SubElement(name, time)
        temp.text = self.parent.ui.rcg.mash_temp_disp.text()
        eff.text = self.parent.ui.rcg.mash_eff_disp.text()
        vol.text = self.parent.ui.rcg.vol_disp.text()
        EBU.text = self.parent.ui.rcg.ebu_disp.text()
        EBC.text = self.parent.ui.rcg.ebc_disp.text()
        OG.text = self.parent.ui.rcg.og_disp.text()
        proc_note.text = str(self.parent.textEdit.toPlainText())
        path = self.get_path()
        path = path + 'Brews/'
        os.makedirs(path, exist_ok=True)
        path = path + fname
        with open(path, "wb") as fo:
            self.parent.ui.recipe_box.setTitle(fname)
            tree = ET.ElementTree(root)
            tree.write(fo)
        curr_date = QtCore.QDate.currentDate()
        days = curr_date.daysTo(date)
        if days <= 0:
            self.parent.commit_enable()

    def load_brew(self, name):
        """Loads brew selected from calendar/search into review panel"""
        self.parent.grainRecipe_list = []
        self.parent.hopRecipe_list = []
        if name is False:
            fname = unicode(QtGui.QFileDialog.getOpenFileName(self.parent))
            self.parent.recipe_filename = os.path.basename(fname)
        else:
            self.parent.recipe_filename = name
        path = self.get_path()
        path = path + '/Brews/' + self.parent.recipe_filename
        self.parent.ui.date_box.setTitle(self.parent.recipe_filename)
        self.parent.ui.brew_date.setText(self.parent.recipe_filename)
        with open(path, "r"):
            tree = ET.ElementTree(file=path)
            root = tree.getroot()
            for elem in root.iter():
                if elem.tag == 'Grain':
                    for grain in elem:
                        grain_data = []
                        for data in grain:
                            data = data.tag[1:]
                            grain_data.append(data)
                        grain_name = grain.tag.replace('_', ' ')
                        a_grain = Grain(grain_name, grain_data[0],
                                        grain_data[1], grain_data[2])
                        self.parent.grainRecipe_list.append(a_grain)
                    self.parent.grain_recipe_update()
                if elem.tag == 'Hops':
                    for hop in elem:
                        hop_data = []
                        for data in hop:
                            data = data.tag[1:]
                            hop_data.append(data)
                        hop_name = hop.tag.replace('_', ' ')
                        a_hop = Hop(hop_name, hop_data[0], hop_data[1],
                                    hop_data[2])
                        self.parent.hopRecipe_list.append(a_hop)
                    self.parent.hop_recipe_update()
                if elem.tag == 'Process':
                    if elem.text is not None:
                        self.parent.ui.process_notes.setPlainText(elem.text)
                    else:
                        self.parent.ui.process_notes.clear()
                if elem.tag == 'Tasting':
                    if elem.text is not None:
                        self.parent.ui.tasting_notes.setPlainText(elem.text)
                    else:
                        self.parent.ui.tasting_notes.clear()
                if elem.tag == 'Style':
                    if elem.text is not None:
                        style = elem.text
                        index = self.parent.ui.box_style.findText(style)
                        if index != -1:
                            self.parent.ui.box_style.setCurrentIndex(index)
                        else:
                            self.parent.ui.box_style.insertItem(0, style)
                            self.parent.ui.box_style.setCurrentIndex(0)
                    else:
                        # Sets blank box if no style saved               
                        self.parent.ui.box_style.setCurrentIndex(-1)
                if elem.tag == 'Rating':
                    if elem.text is not None:
                        self.parent.ui.rating.setValue(int(elem.text))
                    else:
                        self.parent.ui.rating.setValue(0)
                if elem.tag == 'EBU':
                    ebu = str(elem.text)
                    self.parent.ui.hcg.ebu_disp.setText(ebu)
                if elem.tag == 'EBC':
                    ebc = str(elem.text)
                    self.parent.ui.hcg.ebc_disp.setText(ebc)
                if elem.tag == 'OG':
                    og = str(elem.text)
                    self.parent.ui.hcg.og_disp.setText(og)
                if elem.tag == 'Temp':
                    temp = str(elem.text)
                    self.parent.ui.hcg.mash_temp_disp.setText(temp)
                if elem.tag == 'Eff':
                    eff = str(elem.text)
                    self.parent.ui.hcg.mash_eff_disp.setText(eff)
                if elem.tag == 'Vol':
                    vol = str(elem.text)
                    self.parent.ui.hcg.vol_disp.setText(vol)
        self.parent.time_ago()

