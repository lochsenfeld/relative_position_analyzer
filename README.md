python main.py calibrate -p "../Kalibrierung 17.05/Kranstellungen 17.05" -i "./calibration-example.csv"
python main.py analyze -p "C:/24hc" -t 8 -d measurements.db
python main.py output -o "../results" -d measurements.db
python main.py plot -dt "2022-05-24" -d measurements.db