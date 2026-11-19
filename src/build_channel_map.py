import pandas as pd 
#df = pd.read_csv("data/raw/CLEAN_REFIT_081116/CLEAN_House1.csv", parse_dates=["Time"])

load_types = {
    # short high load: high power for a short time
    "kettle": "high_load",
    "toaster": "high_load",
    "microwave": "high_load",

    # motor load: compressors that switch on and off by themselves
    "fridge": "motor_load",
    "freezer": "motor_load",
    "fridge freezer": "motor_load",
    "chest freezer": "motor_load",
    "dehumidifier": "motor_load",       # also has a compressor

    # continuous load: electronics with roughly constant power while on
    "computer": "continuous_load",
    "computer site": "continuous_load",
    "desktop computer": "continuous_load",
    "mjy computer": "continuous_load",  # House 6, computer named after a person
    "pgm computer": "continuous_load",  # House 6, second computer
    "television": "continuous_load",
    "television site": "continuous_load",
    "tv site": "continuous_load",       # House 17, bedroom TV
    "tv/satellite": "continuous_load",  # House 6
    "hi fi": "continuous_load",
    "games console": "continuous_load",

    # excluded: mixed behaviour (heating + motor, several phases)
    "washing machine": "excluded",
    "washer dryer": "excluded",
    "tumble dryer": "excluded",
    "dishwasher": "excluded",

    # excluded: high power, but runs for hours, not short
    "electric heater": "excluded",

    # excluded: almost always on, so hardly any switching events
    "router": "excluded",
    "network site": "excluded",
    "vivarium": "excluded",
    "pond pump": "excluded",

    # excluded: too rare or unclear
    "food mixer": "excluded",
    "magimix": "excluded",
    "k mix": "excluded",
    "bread maker": "excluded",
    "overhead fan": "excluded",         # only one house, see our decision
    "???": "excluded",                  # unknown devices (Houses 12, 13)
}

excel = pd.ExcelFile("data/raw/MetaData_Tables.xlsx") 
rows = []

for sheet_name in excel.sheet_names:
  sheet_name = str(sheet_name)
  if not sheet_name.startswith("House"):
      continue
  house_number = int(sheet_name.split()[1])
  sheet = pd.read_excel(excel, sheet_name=sheet_name, header=None)

  for _, row in sheet.iterrows():
      channel_num = int (row[0])
      if channel_num == 0:
          continue  
      name = row[1]  
      name = name.split("(")[0].strip().lower().replace("-", " ")  
      load_type = load_types.get(name, "unknown")

      rows.append ({"house_number": house_number, 
                    "channel_num": channel_num,
                    "name": name, 
                    "load_type": load_type,
                    "note": row.get(4),
                   })
table = pd.DataFrame(rows)

print (table["load_type"].value_counts())

unknown = table[table["load_type"] == "unknown"]
print ("unknown names:" ,sorted(unknown["name"].unique()))

table.to_csv("data/processed/channel_map.csv", index=False)