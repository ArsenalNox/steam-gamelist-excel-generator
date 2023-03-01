import argparse
import requests
import xlsxwriter

from datetime import datetime
from howlongtobeatpy import HowLongToBeat

parser = argparse.ArgumentParser()

parser.add_argument('--key', 
					help="Your steam api key",
					required=True)

parser.add_argument('--steamid', 
					help="Your steam profile id",
					required=True)

parser.add_argument('--show_play_time', default=True, action='store_true')

parser.add_argument('--show_last_played', default=True, action='store_true')

parser.add_argument('--show_appid', default=False, action='store_true')

parser.add_argument('--include_app_info', default=True, action='store_true')

parser.add_argument('--include_played_free_games', default=True, action='store_true')

parser.add_argument('--exclude', 
					help="Which howlongtobeat game times to exclude ('complete', 'main', 'avg')", 
					nargs='+',
					default=None)

args = parser.parse_args()

print(args)

steam_library = requests.get(
	"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
	f"?key={args.key}"
	f"&steamid={args.steamid}"
	"&format=json"
	f"&include_appinfo={args.include_app_info}"
	f"&include_played_free_games={args.include_played_free_games}"
	).json()

xlsxWorkBook = xlsxwriter.Workbook('output.xlsx')
sheet = xlsxWorkBook.add_worksheet('games')

cursor_row = 0
cursor_col = 0

sheet.write(cursor_row, cursor_col, 'game')

if args.show_play_time:
	cursor_col+=1
	sheet.write(cursor_row, cursor_col, 'playtime')

if args.show_last_played:
	cursor_col+=1
	sheet.write(cursor_row, cursor_col, 'last played')

sheet.write(cursor_row, cursor_col+1, f"main story")
sheet.write(cursor_row, cursor_col+2, f"main + extras")
sheet.write(cursor_row, cursor_col+3, f"Completionist")

cursor_row += 1
cursor_col = 0

for game in steam_library['response']['games']:

	print(game['name'])
	try:
		results_list = HowLongToBeat().search(game['name'])
		print(results_list[0].json_content['comp_main'])

		cursor_col = 0

		sheet.write(cursor_row, cursor_col, game['name'])
		cursor_col+=1


		if args.show_play_time:
			sheet.write(cursor_row, cursor_col, f"{int(game['playtime_forever']/60)} hrs")
			cursor_col+=1

		if args.show_last_played:
			dt_object = datetime.fromtimestamp(game['rtime_last_played'])
			dt_object = dt_object.strftime("%m/%d/%Y, %H:%M:%S")

			sheet.write(cursor_row, cursor_col, f"{dt_object}")
			cursor_col+=1

		sheet.write(cursor_row, cursor_col, f"{round(int(results_list[0].json_content['comp_main'])/3600)} hours")
		sheet.write(cursor_row, cursor_col+1, f"{round(int(results_list[0].json_content['comp_plus'])/3600)} hours")
		sheet.write(cursor_row, cursor_col+2, f"{round(int(results_list[0].json_content['comp_100'])/3600)} hours")
		cursor_row += 1

	except Exception as err:
		print(f"Failed to retreive information about {game['name']}")


xlsxWorkBook.close()