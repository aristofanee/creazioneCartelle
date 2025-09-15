import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QCheckBox, QButtonGroup
from main_window import Ui_MainWindow  # this class is defined in the generated file
import json
import mme_processor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        with open("vru.json", "r", encoding="utf-8") as f:
            self.vru_table = json.load(f)

        self.ui.button_group = QButtonGroup()
        self.ui.button_group.addButton(self.ui.radio_car)
        self.ui.button_group.addButton(self.ui.radio_van)
        self.ui.button_group.addButton(self.ui.radio_truck)

        self.ui.create_folders_button.clicked.connect(self.button_pressed)
        self.ui.select_all_button.clicked.connect(self.select_all)

    def get_tab_name(self,checkbox):
        tab_widget = self.ui.tabWidget

        parent = checkbox.parent()
        while parent and parent != tab_widget:
            if tab_widget.indexOf(parent) != -1:
                # Found the tab page widget that contains this checkbox
                tab_name = parent.objectName()
            parent = parent.parent()

        return(tab_name)
    
    def select_all(self):
        checkboxes = self.findChildren(QCheckBox)

        for checkbox in checkboxes:
            checkbox.setChecked(True)



    def button_pressed(self):
        if self.ui.textbox_model.text().strip() == "" or \
        self.ui.textbox_year.text().strip() == "" or\
        self.ui.textbox_oem.text().strip() == "" or \
        self.ui.textbox_number.text().strip() == "":
             QMessageBox.warning(self, "Warning", "Some of the specifications are missing")
             return

        vehicle_spec_file = Path("vehicle_spec.txt")

        #remove the spec check
        if vehicle_spec_file.is_file():
            QMessageBox.warning(self, "Warning", "Could not find Vehicle_spec.txt")
            vehicle_spec_path, _ = QFileDialog.getOpenFileName(self, "Select vehicle_spec.txt", "", "Text Files (*.txt)")
            vehicle_spec_file = Path(vehicle_spec_path)
            if not vehicle_spec_file.is_file():
                QMessageBox.warning(self, "Warning", "No file was selected")
                return

        model = self.ui.textbox_model.text().strip()
        year = self.ui.textbox_year.text().strip()
        oem = self.ui.textbox_oem.text().strip()
        encap_number = self.ui.textbox_number.text().strip()

        folders_name_root =  year + "-" + oem + "-" + encap_number

        parent_folder_name =folders_name_root + "-" + model
        parent_folder = Path(parent_folder_name)
        parent_folder.mkdir(exist_ok = True)

        aebc_folder_name =folders_name_root + "-AEBC"
        aebp_folder_name =folders_name_root + "-AEBP"
        aebb_folder_name =folders_name_root + "-AEBB"
        aebm_folder_name =folders_name_root + "-AEBM"
        lss_folder_name =folders_name_root + "-LSS"
        sas_folder_name =folders_name_root + "-SAS"

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

        checkboxes = self.findChildren(QCheckBox)

        for checkbox in checkboxes:
            if not checkbox.isChecked():
                continue

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

            folder_name = "" 

            metadata = [checkbox.property("test_metadata")]
            parent = checkbox.parent()

            while parent:

                metadata.append(parent.property("test_metadata"))
                parent = parent.parent()

            metadata = [x for x in metadata if x is not None]
            metadata.reverse()

            test_name = [x for x in metadata if not x.isnumeric()][0]

            print(test_name)

            vut_speed = None
            target_speed = None
            lateral_speed = None
            target_type = None


            if len(metadata) == 3:
                if tab_name == "tab_lss":
                    folder_name = metadata[1] + "_" + metadata[2] + "_" + metadata[0] + "GVT"
                    vut_speed = 72
                    lateral_speed = metadata[2]
                    target_speed = metadata[0]
                    target_type = "GVT"

                elif test_name.startswith("CCC") or test_name.startswith("CCFt"):
                    folder_name = metadata[0] + "_" + metadata[2] + "VUT_" + metadata[1] + "GVT"
                    vut_speed = metadata[2] 
                    target_speed = metadata[1]
                    target_type = "GVT"
                     
                elif test_name.startswith("CMFt"): 
                    folder_name = metadata[0] + "_" + metadata[2] + "VUT_" + metadata[1] + "GVT"
                    vut_speed = metadata[2] 
                    target_speed = metadata[1]
                    target_type = "EMT"
                     
                elif test_name.startswith("CCRs"):
                    folder_name = metadata[0] + "_" + metadata[2] + "VUT_" + metadata[1]
                    vut_speed = metadata[2]
                    target_speed = 0
                    target_type = "GVT"
                     
                elif test_name.startswith("CCRm"):
                    folder_name = metadata[0] + "_" + metadata[2] + "VUT_" + metadata[1]
                    vut_speed = metadata[2]
                    target_speed = 20 
                    target_type = "GVT"

                elif test_name.startswith("ELK") and active_folder == aebm_folder:
                    folder_name = metadata[1] + "_" + metadata[2] + "_" + metadata[0] + "EMT"
                    target_speed = int(metadata[0])
                    if target_speed == 60:
                        vut_speed = 50
                    elif target_speed == 80:
                        vut_speed = 72
                    
                    lateral_speed = metadata[2]

                    target_type = "EMT"

                else:
                    #TODO errore
                    print("ERRORE")
                    

            elif len(metadata) == 2:
                folder_name = metadata[0] + "_" + metadata[1]
                
                if test_name.startswith("CCRb"):
                    vut_speed = 50
                    target_speed = 50 
                    target_type = "GVT"

                elif test_name.startswith("CCFhol") or test_name.startswith("CCFhos") :
                    vut_speed = int(metadata[1])
                    target_speed = int(metadata[1]) 
                    target_type = "GVT"
                     
                elif test_name.startswith("CMRb"):
                    vut_speed = 50
                    target_speed = 50 
                    target_type = "EMT"

                elif test_name.startswith("CMRs"):
                    vut_speed = int(metadata[1])
                    target_speed = 0 
                    target_type = "EMT"
                
                elif active_folder == aebm_folder and test_name.startswith("ELK_ONC"):
                    vut_speed = 72 
                    target_speed = 72 
                    target_type = "EMT"
                    lateral_speed = metadata[1]
                
                elif active_folder == lss_folder and not "GVT" in metadata[1]:
                    vut_speed = 72 
                    target_type = "NVT"
                    lateral_speed = metadata[1].split("_")[0]

                elif active_folder == lss_folder and "GVT" in metadata[1]:
                    vut_speed = 72 
                    target_type = "GVT"
                    lateral_speed = metadata[1].split("_")[0]
                else:
                    vut_speed = int(metadata[1])
                    target_speed = self.vru_table[test_name]["target_speed"]
                    target_type = self.vru_table[test_name]["target_type"]



            #veihcle_type_checkbox = self.ui.button_group.checkedButton()
            #folder_name = veihcle_type_checkbox.property("test_metadata") + folder_name[2:]

 
            folder_name = encap_number + "_" + folder_name

            folder_name = folder_name + "-01"

            test_path = active_folder / folder_name
            test_path.mkdir(parents=True, exist_ok=True)

            channel_path = test_path / "Channel"
            channel_path.mkdir(parents=True, exist_ok=True)

            movie_path = test_path / "Movie"
            movie_path.mkdir(parents=True, exist_ok=True)

            mme_file_lines = mme_processor.mmefile_creator(vehicle_spec_file, 
                                              model, folder_name, test_name,test_identifier,
                                              vut_speed, lateral_speed, target_speed, target_type)

            with open(test_path / folder_name + ".mme", "w", encoding="utf-8") as file:
                file.writelines(mme_file_lines)

            print(folder_name)


#TODO understand how the dooring works


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
