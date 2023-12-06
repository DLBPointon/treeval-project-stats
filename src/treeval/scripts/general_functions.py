import sys

def get_contents(self) -> list:
    with open (self.file) as datafile:
        return datafile.readlines()


def normalise_values(self, item: str) -> float:
    """
    normalise co2e into miligrams
    normalise Watt Hour data into mili Watt hours
    normalise memory values into MB
    """
    item_data = item.split(' ')
    match item_data[-1].strip():
        case 'kg' | 'Kg' | 'kWh' | 'KWh' | 'TB':
            return int(round(float(item_data[0]) * 1000000, 2))
        case 'g' | 'Wh'| 'GB':
            return int(round(float(item_data[0]) * 1000, 2))
        case 'mg' | 'mWh' | 'MB':
            return int(round(float(item_data[0]), 2))           # Because these are what we want everything converted too
        case 'ug' | 'uWh' | 'KB':
            return int(round(float(item_data[0]) / 1000, 2))
        case 'ng' | 'nWh':
            return int(round(float(item_data[0]) / 1000000, 2))
        case 'pg' | 'pWh':
            return int(round(float(item_data[0]) / 1000000000, 2))
        case _:
            if int(item_data[0].strip()) == 0:
                #"Zero value with no suffix! Happens when process so short lived that resources can't be polled, but I can deal with it"
                return int(item_data[0])
            else:
                sys.exit(f"Incorrect value ({item}), it's not 0 and there's no suffix!")


def fix_time(time_list: list) -> dict:
    """
    Fix all of time!
    Calculate the total runtime in h, m and s using the time taken per process
    Time taken over pipeline includes wait time on local HPC
    """
    total = 0
    time_dict = {}
    if time_list[0] == "CANNOT":
        total = -1
    else:
        for i in time_list:
            if i.endswith('d'):
                total += int(i.split('d')[0]) * 86400        # number of days * seconds in day
            elif i.endswith('h'):
                total += (int(i.split('h')[0]) * 60) * 60    # number of hours * minutes in hour * seconds in minute
            elif i.endswith('ms'):
                total += int(float(i.split('ms')[0])) / 1000 # divide ms by 1000 to convert milliseconds to seconds
            elif i.endswith('m'):
                total += int(i.split('m')[0]) * 60           # number of minutes * seconds in minute
            elif i.endswith('s'):
                total += int(float(i.split('s')[0]))         # nothing.. it's already in seconds
            else:
                total = int(float(i))                        # nothing.. means its the newer formats which are already converted
        time_dict['s'] = total
        time_dict['m'] = round(total / 60, 2)
        time_dict['h'] = round(( total / 60 ) / 60, 2)
    return time_dict