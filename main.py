import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QCheckBox, QButtonGroup
from PySide6.QtGui import QShortcut, QKeySequence
from main_window import Ui_MainWindow  # this class is defined in the generated file
import json
import mme_processor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Importing the json database in memory
        with open("test_type_database.json", "r", encoding="utf-8") as f:
            self.database = json.load(f)

        # Importing the vehicle spec and displaing it in the plain textbox
        self.vehicle_spec_file = Path("vehicle_spec.txt")
        with open(self.vehicle_spec_file, "r", encoding="utf-8") as file:
            spec_file_content = file.read()
        self.ui.textbox_vehicle_spec.setPlainText(spec_file_content)
        # Commento di prova
        # Adds the radio button in a buttonGroup
        self.ui.button_group = QButtonGroup()
        self.ui.button_group.addButton(self.ui.radio_car)
        self.ui.button_group.addButton(self.ui.radio_van)
        self.ui.button_group.addButton(self.ui.radio_truck)

        # Shortcut to select everything for debug reasons
        self.shortcut_h = QShortcut(QKeySequence("Ctrl+A"), self)
        self.shortcut_h.activated.connect(self.select_all)

        # Connects the buttons to the functions
        self.ui.create_folders_button.clicked.connect(self.button_pressed)
        self.ui.save_spec_button.clicked.connect(self.save_spec_file)

        # Function to get the name of the tab, this is not very clean it could be rewritten
    def get_tab_name(self,checkbox):

        tab_widget = self.ui.tabWidget

        parent = checkbox.parent()
        while parent and parent != tab_widget:
            if tab_widget.indexOf(parent) != -1:
                # Found the tab page widget that contains this checkbox
                tab_name = parent.objectName()
            parent = parent.parent()

        return(tab_name)

    # The function that get used by the ctrl+A shortcut
    def select_all(self):
        checkboxes = self.findChildren(QCheckBox)

        for checkbox in checkboxes:
            checkbox.setChecked(True)

    # Function called by the Save Specfile button
    def save_spec_file(self):
        with open(self.vehicle_spec_file, "w", encoding="utf-8") as file:
            textbox_content = self.ui.textbox_vehicle_spec.toPlainText()
            file.write(textbox_content)
        QMessageBox.information(self, "vehicle_spec.txt", "The file was correctly saved.")

    # Function called by the main button (create folders)
    def button_pressed(self):
        # Check if the textboxes are full and saves the data in them
        if self.ui.textbox_model.text().strip() == "" or \
        self.ui.textbox_year.text().strip() == "" or\
        self.ui.textbox_oem.text().strip() == "" or \
        self.ui.textbox_number.text().strip() == "":
             QMessageBox.warning(self, "Warning", "Some of the specifications are missing")
             return

        model = self.ui.textbox_model.text().strip()
        year = self.ui.textbox_year.text().strip()
        oem = self.ui.textbox_oem.text().strip()
        encap_number = self.ui.textbox_number.text().strip()

        # Asks with a dialog box where the user want to create the folders
        main_folder_string = QFileDialog.getExistingDirectory(None, "Select where you want the folder to be created: ") 
        if not main_folder_string:
            QMessageBox.warning(self, "Warning", "No folder was selected.")
            return
        else:
            main_folder = Path(main_folder_string)


        # Creation of the folders
        folders_name_root =  year + "-" + oem + "-" + encap_number

        parent_folder_name = folders_name_root + "-" + model
        parent_folder = main_folder / parent_folder_name
        parent_folder.mkdir(exist_ok = True)

        aebc_folder_name = folders_name_root + "-AEBC"
        aebp_folder_name = folders_name_root + "-AEBP"
        aebb_folder_name = folders_name_root + "-AEBB"
        aebm_folder_name = folders_name_root + "-AEBM"
        lss_folder_name = folders_name_root + "-LSS"
        sas_folder_name = folders_name_root + "-SAS"

        aebc_folder = parent_folder / aebc_folder_name
        aebp_folder = parent_folder / aebp_folder_name
        aebb_folder = parent_folder / aebb_folder_name
        aebm_folder = parent_folder / aebm_folder_name
        lss_folder = parent_folder / lss_folder_name
        sas_folder = parent_folder / sas_folder_name

        aebc_folder.mkdir(parents=True, exist_ok=True)
        aebp_folder.mkdir(parents=True, exist_ok=True)
        aebb_folder.mkdir(parents=True, exist_ok=True)
        aebm_folder.mkdir(parents=True, exist_ok=True)
        lss_folder.mkdir(parents=True, exist_ok=True)
        sas_folder.mkdir(parents=True, exist_ok=True)

        # Finds all the checkboxes in the UI and then starts a loop with them
        checkboxes = self.findChildren(QCheckBox)

        # Main loop
        for checkbox in checkboxes:

            # Skips all the empty checkboxes
            if not checkbox.isChecked():
                continue

            # Takes the name of the tab and gets the identifier (like "ped" or "moto")
            tab_name = self.get_tab_name(checkbox).strip()
            test_identifier = tab_name.split("_")[1]

            match tab_name:
                case "tab_ped":
                    active_folder = aebp_folder
                case "tab_bicy":
                    active_folder = aebb_folder
                case "tab_moto":
                    active_folder = aebm_folder
                case "tab_c2c":
                    active_folder = aebc_folder
                case "tab_lss":
                    active_folder = lss_folder
                case _:
                    print("no tab was found.")

            # Retrives the "test_name" property from the UI checkbox
            test_name = checkbox.property("test_name")

            print(test_name)

            # Takes the information relative to the specific test from the dictionary
            test_template = self.database[test_name]

            # Adds the test name to the "test_data" object that will have the whole 
            test_data = {"test_name":test_name}

            # TODO add better error handling, at least when it doesnt find the correct parameter in the checkbox
            for key, value in test_template.items():
                if key == "naming_convention":
                    continue
                if value == "user_defined":
                    test_data[key] = checkbox.property(key)
                else:
                    test_data[key] = value

            if "lateral_speed" not in test_data:
                test_data["lateral_speed"] = None 

            if "target_speed" not in test_data:
                test_data["target_speed"] = "" 
            
            # Extracts the naming format from the database and it fills the parameters with what it has saved in the test_data
            naming_format = test_template["naming_convention"]
            run_name = naming_format.format(**test_data)

            # These are the minimum requirements needed in the .mme files for the run
            vut_speed = test_data["vut_speed"]
            target_speed = test_data["target_speed"]
            lateral_speed = test_data["lateral_speed"]
            target_type = test_data["target_type"]
            test_type = test_data["test_type"]

            # Constract the full folder name
            folder_name = encap_number + "-" + run_name + "-01"

            # Creates the folder for the test and the sub folders 
            test_path = active_folder / folder_name
            test_path.mkdir(parents=True, exist_ok=True)
            channel_path = test_path / "Channel"
            channel_path.mkdir(parents=True, exist_ok=True)
            movie_path = test_path / "Movie"
            movie_path.mkdir(parents=True, exist_ok=True)

            # Calls the function that fills the contents of the .mme file
            mme_file_lines = mme_processor.mmefile_creator(self.vehicle_spec_file,year,
                                              model, folder_name, test_name,test_identifier,
                                              vut_speed, lateral_speed, target_speed, target_type, test_type)

            # Saves the .mme file
            with open(test_path / (folder_name + ".mme"), "w", encoding="utf-8") as file:
                for line in mme_file_lines:
                    file.write(line + "\n")

        QMessageBox.information(self, "Euro NCAP foldering", "The folders were created correctly.")

#TODO understand how the dooring works

# Simple Qt main that runs the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
