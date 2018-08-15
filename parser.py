# import pymysql
import pandas as pd
from haversine import haversine

googleKey = "AIzaSyCGrOM80fJ8wtEO0GDA0a_SFYXfNQGt9VQ"

# Open database connection
# db = pymysql.connect("localhost","root","24sticco","banks" )

# prepare a cursor object using cursor() method
# cursor = db.cursor()

# print(results)

def getAllFromADataframeWithBankingNetwork(aDataFrame, aBankingNetwork):
	return aDataFrame.loc[(aDataFrame.RED==aBankingNetwork)]


def getNearestAtms(aLocation, aBankingNetwork):
	user_lat = aLocation.latitude
	user_lon = aLocation.longitude

	#-----------------------
	# for testing
	
	# user_lat = -34.5702815
	# user_lon = -58.4440812


	# user_lat = -34.6037389
	# user_lon = -58.3837591
	#-----------------------

	user_location = (user_lat, user_lon)

	# query_network = '"' + aBankingNetwork + '"'
	# query = "SELECT * FROM `cajeros-automaticos` where RED ="+query_network
	# cursor.execute(query)

	# results = cursor.fetchall()




	data=pd.read_csv('./data/cajeros-automaticos/cajeros-automaticos.csv', sep='	')

	df = pd.DataFrame(data)
	
	distances = []
	
	for index, row in df.iterrows():
		atm_location = (row.LAT, row.LNG)
		distances.append(haversine(atm_location, user_location)*1000)

	newCol = pd.DataFrame({'DISTANCIA':distances})

	df= df.join(newCol)

	filtered_by_network_df = getAllFromADataframeWithBankingNetwork(df,aBankingNetwork)

	sorted_by_distance_df = filtered_by_network_df.sort_values(by='DISTANCIA', ascending=True)

	final_df = sorted_by_distance_df.head(3)

	final_df = final_df.loc[final_df.DISTANCIA < 500]

	atms_banks = final_df['BANCO'].tolist()

	atms_addresses = final_df['DOM_ORIG'].tolist()

	atms_lats = final_df['LAT'].tolist()

	atms_lons = final_df['LNG'].tolist()

	msg = ""

	urlY= "https://static-maps.yandex.ru/1.x/?lang=en_US&ll="+str(user_lon)+","+str(user_lat)+"&size=650,450&l=map&pt="+str(user_lon)+","+str(user_lat)+",home"


	urlG="https://maps.googleapis.com/maps/api/staticmap?center="+str(user_lat)+","+str(user_lon)+"&size=600x300&maptype=roadmap&markers=color:blue|label:US|"+str(user_lat)+","+str(user_lon)
	for idx in range(0,len(atms_banks)):
		msg = msg + str(idx+1) + ". " + atms_banks[idx] + " - " + atms_addresses[idx] + "\n"
		urlY = urlY +"~"+ str(atms_lons[idx]) + "," + str(atms_lats[idx]) + ",pm2gnl"+ str(idx+1)
		urlG = urlG + "&markers=color:green|label:"+str(idx+1)+"|"+str(atms_lats[idx])+","+str(atms_lons[idx])


	urlG+="&key="+googleKey
	return (msg, urlG)
