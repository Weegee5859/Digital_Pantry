from bs4 import BeautifulSoup
import os
import pickle
import requests
from difflib import SequenceMatcher, get_close_matches

dessert_page = "https://en.wikipedia.org/wiki/List_of_desserts"
breakfast_page = "https://en.wikipedia.org/wiki/List_of_breakfast_foods"
appetizer_page = 'https://en.wikipedia.org/wiki/List_of_hors_d'+"%"+'27oeuvre'


def returnAllRecipeData(url):
	def formatRecipeUrls(finalList):
		formattedList = []
		for index, value in enumerate(finalList):
			finalList[index] = " ".join(finalList[index].split())
			cleanTitle(finalList[index])
			if len(finalList[index].split())>7:
				finalList.pop(index)
				continue
			if finalList[index] in formattedList:
				continue
		[formattedList.append(x) for x in finalList if x not in formattedList]
		return formattedList
	def returnScrapedAllRecipeUrl(url):
		finalList = []
		soup = BeautifulSoup( requests.get(url).content, 'html.parser' )
		for recipe_type in soup.findAll('a', {'class': 'carouselNav__link recipeCarousel__link'}):
			soup = BeautifulSoup( requests.get(recipe_type['href']).content, 'html.parser' )
			recipe_sub_types = soup.findAll('a', {'class': 'carouselNav__link recipeCarousel__link'})
			for recipe_sub_type in recipe_sub_types:
				soup = BeautifulSoup( requests.get(recipe_sub_type['href']).content, 'html.parser' )
				recipe_list = soup.findAll('div', {'class': 'card__imageContainer'})
				for recipe_title in recipe_list:
					title = recipe_title.find('a')['title']
					if title in finalList:
						continue
					finalList.append(title)
					print(title)
		return finalList
	finalList = returnScrapedAllRecipeUrl(url)
	finalList = formatRecipeUrls(finalList)
	return finalList
def getDessertData(webpage):
	myList = []
	page = requests.get(webpage)
	soup = BeautifulSoup(page.text, 'html.parser')
	container = soup.find_all('div',{'class','div-col'})
	for category in container:
		for link in category.find_all("li"):
			myList.append(link.get_text())
	return myList
def getBreakfastData(webpage):
	myList = []
	page = requests.get(webpage)
	soup = BeautifulSoup(page.text, 'html.parser')
	container = soup.find('div',{'class','mw-parser-output'})
	for category in container.find_all("ul"):
		for link in category.find_all("li"):
			try:
				item = link.find("a").get_text()
			except:
				continue
			#Not clean way to end scrape but it works... (history for breakfast comes right after the last needed food item)
			if item == "History of breakfast": return myList
			if len(item)<4: continue
			if any(ext in item for ext in ["[","]"]): continue
			myList.append(item)
			continue	
	return myList
def getAppetizerData(webpage):
	myList = []
	page = requests.get(webpage)
	soup = BeautifulSoup(page.text, 'html.parser')
	table = soup.find('table')
	for row in table.find_all('tr')[1:]:
		symbol_cell = row.find_all('td')[0]
		#replace any "\n" in text
		final_string = symbol_cell.get_text().replace("\n","")
		#remove any bracket or numbers
		for text in "[]!?_}{)(!@#$%^&*-1234567890":
			final_string = final_string.replace(text,"")
		myList.append(final_string)
	return myList
def pickleFoodData(debug=True):
	food_list ={}
	food_list['dessert'] = getDessertData(dessert_page)
	food_list['breakfast'] = getBreakfastData(breakfast_page)
	food_list['appetizer'] = getAppetizerData(appetizer_page)
	food_list['meal'] = getMealData()
	food_list['drink'] = getDrinkData() + ["beverage","beverages","drink","drinks"]
	pickle.dump( food_list, open( "food_list.p", "wb" ) )
	if not debug: return True
	print(len(food_list['dessert']))
	print(len(food_list['breakfast']))
	print(len(food_list['appetizer']))
	print(len(food_list['drink']))
def returnpickledFoodData():
	return pickle.load( open( "food_list.p", "rb" ) )
def returnFoodTypes():
	types = []
	for index, value in enumerate(food_list):
		types.append(value)
	return sorted(types)
def cleanTitle(title):
	final = ""
	for word in title.split():
		#Remove all symbols
		word = ''.join(e for e in word if e.isalnum())
		#remove any word thats in that list
		if word.lower() in ["a","and","are","do","for","how","it","its","is","make","of","on","or","to","with","you","chef","best"]: continue
		if "'s" in word.lower(): continue
		if word == "": continue
		final += word+" "
	return final
def returnRecipeType(title):
	highest_single_match = 0.65
	highest_double_match = 0.65
	double_found = False
	final_type = "Other"
	title = cleanTitle(title)
	title_split = title.split()
	print("============================")
	print(title)
	print(title_split)
	for food_type, value in food_list.items():
		#print(food_type)
		for food in value:
			#when iterate list of foods, split each food item
			food_split = food.split()
			#Check every word in title split with every word in food split, if any word matches at or above 0.65%, continue the process
			for word_index, word in enumerate(title_split):
				for food_index,inner_food in enumerate(food_split):
					if SequenceMatcher( None, word, inner_food ).ratio()>highest_single_match:
						#print(food)
						#print("matched as {}:{}[{}]/{}".format(food_type,word,word_index,food))
						#print(SequenceMatcher( None, word, food_split ).ratio())
						#The program will now take two words, one before and after the matching word
						#e.g. if the matching words title[3] then it will make before:"title[2] title[3]" and after "title[3] title[4]"
						#these combined words will be compared, if it's above 0.66 match
						#the match rate is saved for both single word matches and doulble word matches,
						#the program will continue and until it finds the highest match possible
						if not double_found:
							highest_single_match = SequenceMatcher( None, word, inner_food ).ratio()
							final_type = food_type
							print("SINGLE MATCH "+str(highest_single_match))
							print(inner_food)
							if SequenceMatcher( None, food.lower(), title.lower() ).ratio()>0.9: return final_type
						before = title_split[word_index-1] if word_index-1 < len(title_split) else None
						before_text = "{} {}".format(before,word)
						after = title_split[word_index+1] if word_index+1 < len(title_split) else None
						after_text = "{} {}".format(word,after)
						#print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
						double_first = "{} {}".format(food_split[food_index],food_split[food_index+1] if food_index+1 < len(food_split) else None)
						#double_second = "{} {}".format(food_split[food_index+1],food_split[food_index] if food_index+1 < len(food_split) else None)
						if "None" in double_first:
							continue
						#print(double_first)
						#print(before_text)
						#print(after_text)
						if before:
							before_result = SequenceMatcher( None, before_text, double_first ).ratio()
							print("#####")
							print(before_result)
							print(double_first)
							if before_result>highest_double_match:
								highest_double_match = before_result
								double_found = True
								final_type = food_type
								print(double_first)
								print("{}:{}".format(before_result,before_text))
								print("ABSOLUTE MATCH - BEFORE")
								#return final_type
						if after:
							after_result = SequenceMatcher( None, after_text, double_first ).ratio()
							print("#####")
							print(after_result)	
							print(double_first)
							if after_result>highest_double_match:
								highest_double_match = after_result
								double_found = True
								final_type = food_type
								print(double_first)
								print("{}:{}".format(after_result,after_text))
								print("ABSOLUTE MATCH - AFTER")
								#return final_type
							#return final_type
						
							#return final_type
						#print("----------------------")
	return final_type
def getMealData():
	lunch_url = "https://www.allrecipes.com/recipes/17561/lunch/"
	dinner_url = "https://www.allrecipes.com/recipes/17562/dinner/"

	lunch_list = returnAllRecipeData(lunch_url)
	dinner_list = returnAllRecipeData(dinner_url)
	allrecipe_urls = lunch_list + dinner_list
	return allrecipe_urls

def getDrinkData():
	drink_url = "https://www.allrecipes.com/recipes/77/drinks/"
	allrecipe_urls = []

	allrecipe_urls = returnAllRecipeData(drink_url)
	del allrecipe_urls[-34:]
	return allrecipe_urls


food_list = returnpickledFoodData()
'''
def test():
	import RecipeMaker as rm
	food_list = returnpickledFoodData()
	for folder in os.listdir(rm.RECIPE_DIRECTORY):
		#print(folder.replace(".pdf",""))
		#print(cleanTitle(folder.replace(".pdf","")))
		print("Type: "+returnRecipeType(folder.replace(".pdf","")))
'''



