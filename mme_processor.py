from datetime import datetime


def mmefile_creator(specfile, model,folder_name,test_name, test_identifier, vut_speed,lateral_speed,target_speed,target_type):

    specfile_data = {}

    with open(specfile, "r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            if ':' in line:
                key, value = line.split(":", 1)
                key = key.strip()
                specfile_data[key] = value

    mme_lines = []
    mme_lines.append( "Data format edition number:\t\t1.6")
    mme_lines[1] = "Laboratory name:\t\tCSI"
    mme_lines[2] = "Customer name:\t\tEuro NCAP"
    mme_lines[3] = "Customer test ref. number:\t\t"+folder_name
    mme_lines[4] = "Customer project ref. number:\t\t"+folder_name.split("-")[0]
    mme_lines[5] = "Title:\t\tEuro NCAP " + datetime.now().strftime("%A")
    mme_lines[6] = "Timestamp:\t\t"+ datetime.now().strftime("%d-%b-%Y %H:%M:%S")

    if "AEB" in test_name:
        test_type = "AEB"
    elif "FCW" in test_name:
        test_type = "FCW"
    elif any(x in test_name for x in ["ELK", "LKA", "LDW"]):
        test_type = "LSS"
    elif "CPLa25" or "CBLa25" in test_name:
        test_type = "FCW"
    else:
        test_type = "AEB"

    mme_lines[7] = "Type of the test:\t\t" + test_type
    mme_lines[8] = "Subtype of the test:\t\t" + test_name 

    match test_identifier:
        case "ped":
            regulation = specfile_data["Regulation VRU"]
        case "bicy":
            regulation = specfile_data["Regulation VRU"]
        case "moto":
            regulation = specfile_data["Regulation VRU"]
        case "c2c":
            regulation = specfile_data["Regulation C2C"]
        case "lss":
            regulation = specfile_data["Regulation LSS"]


    mme_lines[9] = "Regulation:\t\t" + regulation 
    
    match test_identifier:
        case "ped":
            date = specfile_data["Date of the test VRU P"]
        case "bicy":
            date = specfile_data["Date of the test VRU B"]
        case "moto":
            date = specfile_data["Date of the test VRU M"]
        case "c2c":
            date = specfile_data["Date of the test C2C"]
        case "lss":
            date = specfile_data["Date of the test LSS"]

    mme_lines[10] = "Date of the test:\t\t" + date 
    mme_lines[11] = "Name of test object 1:\t\t" + model 
    mme_lines[12] = "Ref. number of test object 1:\t\t" + specfile_data["VIN"] 
    mme_lines[13] = "Velocity test object 1 lon.:\t\t" + str(vut_speed) + " km/h" 

    if lateral_speed == None:
        lat_speed = "0 km/h"
    else:
        lat_speed = lat_speed + " m/s"

    mme_lines[14] = "Velocity test object 1 lat.:\t\t" + lat_speed
    mme_lines[15] = "Mass test object 1:\t\t" + specfile_data["Mass VUT"] + " Kg"
    mme_lines[16] = "Driver position object 1:\t\t1"
    mme_lines[17] = "Impact side test object 1:\t\tRI" 
    mme_lines[18] = ".Dimension test object 1:\t\t" + specfile_data["Lenght VUT"] + ", "+ specfile_data["Width VUT"]
    mme_lines[19] = ".Profile-X test object 1:\t\t" + specfile_data["Profile-X"]
    mme_lines[20] = ".Profile-Y test object 1:\t\t" + specfile_data["Profile-Y"]
    mme_lines[21] = "Name of test object 2:\t\t" + target_type

    if target_speed == None:
        target_speed = ""
    else:
        target_speed = str(target_speed) + " km/h"

    mme_lines[22] = "Velocity test object 2:\t\t" + target_speed
    mme_lines[23] = "Type of data source:\t\tHardware"

    return mme_lines


