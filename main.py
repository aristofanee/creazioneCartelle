import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QCheckBox
from main_window import Ui_MainWindow  # this class is defined in the generated file

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self) 
        self.ui.create_folders_button.clicked.connect(self.button_pressed)

    def get_tab_name(self,checkbox):
        tab_widget = self.ui.tabWidget

        parent = checkbox.parent()
        while parent and parent != tab_widget:
            if tab_widget.indexOf(parent) != -1:
                # Found the tab page widget that contains this checkbox
                tab_name = parent.objectName()
            parent = parent.parent()

        return(tab_name)




    def button_pressed(self):
        if self.ui.textbox_model.text().strip() == "" or \
        self.ui.textbox_year.text().strip() == "" or\
        self.ui.textbox_oem.text().strip() == "" or \
        self.ui.textbox_number.text().strip() == "":
             QMessageBox.warning(self, "Warning", "Some of the specifications are missing")
             return

        vehicle_spec_file = Path("veihcle_spec.txt")

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
                
            folder_name = year
            
            metadata = [checkbox.property("test_metadata") + "VUT"]
            parent = checkbox.parent()

            while parent:
                
                metadata.append(parent.property("test_metadata"))
                parent = parent.parent()
            
            metadata = [x for x in metadata if x is not None]
            metadata.reverse()

            if len(metadata) == 3:
                if tab_name == "tab_lss":
                    folder_name = encap_number + "-" + metadata[1] + "-" + metadata[2] + "-" + metadata[0] + "GVT"
                else:
                    print("fix this")
                    #TODO moto
            elif len(metadata) == 2:
                for element in metadata:
                    folder_name = folder_name + "-" + element

            folder_name = folder_name + "-01"

            print(folder_name)



    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
