#digi-recipe
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import fitz
import glob
import io
import json
import os
from pathlib import Path
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image
import re
import requests
from selenium import webdriver
import sys
import time
import imagehash
import random
import shutil
import math
import find_foods as find_food

import base64
from io import BytesIO
# Required
# pip install PyMuPDF Pillow
# pip install pdf2image
# pip install requests
ROOT_DIRECTORY = os.getcwd().replace("\\", "/")
RECIPE_DIRECTORY = ROOT_DIRECTORY+'/recipe'
TEMP_RECIPE_DIRECTORY = ROOT_DIRECTORY+'/temp_recipe'
DIRECTORY_NAME = 'temp_recipe_'
website = 'https://www.allrecipes.com/recipe/165384/bananas-foster-belgian-waffles/'
website2 = 'https://www.foodnetwork.com/recipes/food-network-kitchen/basic-vanilla-cake-recipe-2043654'


def convertPilToB64(pil):
	im_file = BytesIO()
	pil.save(im_file, format="JPEG")
	im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
	im_b64 = base64.b64encode(im_bytes)
	return im_b64.decode()

def convertPilToAscii(pil):
	im_file = BytesIO()
	pil.save(im_file, format="JPEG")
	im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
	im_b64 = base64.b64encode(im_bytes)
	ascii_image = base64.b64encode(im_b64).decode('ascii')
	return ascii_image

# Temporarily renames folders and deletes any empty folders
# folders will be renamed to the parameter directory_name
# followed by a number in order of file creation (directory_name_1,directory_name_2,...)
def cleanTemporaryDirectory(temp_directory=TEMP_RECIPE_DIRECTORY,directory_name=DIRECTORY_NAME):
	if temp_directory==None: return None
	if not os.path.exists(temp_directory): return None
	folder_count = random.randint(1, 9999)
	for folder in os.listdir(temp_directory):
		folder_directory = "{0}/{1}".format(temp_directory,folder)
		if os.path.exists(folder_directory) and not os.path.isfile(folder_directory):
			print(folder)
			if not os.listdir(folder_directory):
				print("empty file, deleting...")
				os.rmdir(folder_directory)
				continue
			os.rename(folder_directory,"{0}/{1}".format(temp_directory,"temp"+str(folder_count)))
			folder_count+=1
	# Renames folders to finalalized name(s)
	folder_count = 1
	for folder in os.listdir(temp_directory):
		folder_directory = "{0}/{1}".format(temp_directory,folder)
		new_folder_directory = "{0}/{1}{2}/".format(temp_directory,directory_name,str(folder_count))
		os.rename(folder_directory, new_folder_directory)
		folder_count+=1
	#return False

def createTemporaryDirectory(max_directories=10,directory_name=DIRECTORY_NAME,output_directory=False):
	# Create temp directory when user is creating a recipe on the website.
	# This directory will be deleted once the program compiles the recipe data
	# into a dictionary
	# int (max_directories) temporarily directories are allowed at a time.
	# Function returns the correctly formatted directory as a string.

	# These two for loops will make sure all files are not empty
	# and ensure they have the correct file names to avoid any
	# conflictng errors

	#Output Directory creation
	if output_directory==False:
		print("createTemporaryDirectory: Output directory not given")
	formatted_output_directory = ""
	for directory_amount in range(1,max_directories+1):
		formatted_output_directory = "{0}/{1}{2}/".format(output_directory,directory_name,str(directory_amount))
		print(directory_amount)
		if not os.path.exists(formatted_output_directory):
			print("path not found, creating...")
			os.makedirs(formatted_output_directory)
			print(formatted_output_directory)
			return formatted_output_directory
		if directory_amount>=max_directories:
			print("createTemporaryDirectory: Server has too many files loaded, please wait...")
			return False

def createTemporaryRecipe(recipeFormData=None,websites=None,pdfs=None,automatic=True,temp_recipe_directory=TEMP_RECIPE_DIRECTORY,directory_name=DIRECTORY_NAME):
	#The primary function when creating a recipe
	# Will return a dictionary with 2 keys "success" and "error", each key is a list
	# Success is a list of dicts, each dict contains successfully compile recipe data (title, pdf(base64), images(base64), preview_images(base64))
	# error contains a list of dicts with all the failed formatted recipes, will contain the error encountered as "error" and the website title or pdf title as "title"
	# automatic set to True will disable images and preview_images from being generated
	# Variables
	data_to_return = {}
	data_to_return['success'] = []
	data_to_return['error'] = []
	#If Website and PDF is submitted, then cancel, only one can be used at a time
	if not websites and not pdfs and not recipeFormData:
		print("Website and PDF (and recipeFormData) can't both be empty, exiting...")
		return False
	# Define output directory
	output_directory = createTemporaryDirectory(output_directory=temp_recipe_directory)
	#data['directory'] = output_directory
	if output_directory==False: return False
	# Website Input site
	# The Website link is a string, it will be scanned with selenium and
	# create pdf_data, the images/previews will be scraped from pdf_data
	if not isinstance(recipeFormData, list):
		print("Invalid recipeFormData Format")
		deleteTemporaryDirectory(directory=output_directory)
		return False
	for recipeData in recipeFormData:
		deletePdfsInDirectory(output_directory)
		print("*****Starting...*****")
		#print(recipeFormData)
		compiledRecipeData = {}
		# PDF Process
		if recipeData['type'] == 'pdf':
			print("PDF Found")
			print(recipeData['title'])
			print(recipeData['type'])
			#Check if pdf exists
			if os.path.exists(RECIPE_DIRECTORY+"/"+recipeData['title']):
				print("PDF: Already exist skipping")
				data_to_return['error'].append({
					"error": "PDF: Already exist skipping",
					"name": recipeData['title']
				})
				continue
			compiledRecipeData['pdf'] = recipeData['pdf']
			compiledRecipeData['title'] = recipeData['title'].replace(".pdf","")
			#Save PDF as file temporarily 
			f = open(output_directory+recipeData['title'], 'wb')
			f.write( base64.b64decode( recipeData['pdf'].replace('data:application/pdf;base64,', '') ) )
			f.close()
			print("******PDF INITIALIZATION DONE*****")
		# Website Process
		if recipeData['type'] == 'website':
			print("WEBSITE FOUND")
			print(recipeData['site'])
			#Convert Website to PDF and if theres an error delete directory and move to next recipe
			if not convertWebsiteToPDF(website=recipeData['site'],pdf_output_directory=output_directory):
				deletePdfsInDirectory(output_directory)
				continue
			pdfDataFromWebsite = convertPDFToBase64(pdf_directory=output_directory)
			if not pdfDataFromWebsite:
				print("Website: Could not process Website to PDF")
				data_to_return['error'].append({
					"error": "Website: Could not process Website to PDF",
					"name": recipeData['site']
				})
				continue
			compiledRecipeData['pdf'] = pdfDataFromWebsite['pdf']
			compiledRecipeData['title'] = pdfDataFromWebsite['title'].replace(".pdf","")
			#Check if Recipe PDF Already exists
			if os.path.exists(RECIPE_DIRECTORY+"/"+pdfDataFromWebsite['title']):
				print("website: already exist skipping")
				data_to_return['error'].append({
					"error": "Website: Recipe Already Exist",
					"name": recipeData['site']
				})
				continue
			print("******WEBSITE INITIALIZATION DONE*****")
		compiledRecipeData['food_type'] = find_food.returnRecipeType(compiledRecipeData['title'])
		if automatic:
			print("******EXTRACTING IMAGES*****")
			compiledRecipeData['image'] = extractImagesFromPDF( pdf_path="{}{}.pdf".format(output_directory,compiledRecipeData['title']),image_output_directory=output_directory)
			print("******DONE EXTRACTING IMAGES*****")
		if not automatic:
			compiledRecipeData['previews'] = generatePreviewImages(pdf_path="{}{}".format(output_directory,compiledRecipeData['title']),preview_output_directory=output_directory)
			compiledRecipeData['image'] = extractImagesFromPDF( pdf_path="{}{}".format(output_directory,compiledRecipeData['title']),image_output_directory=output_directory)
		data_to_return['success'].append(compiledRecipeData)
		print("*-*-*-*-*Completed {}!*-*-*-*-*-*".format(compiledRecipeData['title']))
	print("=+Recipe Creation Finished+=")
	deleteTemporaryDirectory(directory=output_directory)
	return data_to_return
	

def convertWebsiteToPDF(website=None,pdf_output_directory=None):
	#Chrome Options Setup
	chrome_options = webdriver.ChromeOptions()
	settings = {
		   "recentDestinations": [{
				"id": "Save as PDF",
				"origin": "local",
				"account": "",
			}],
			"selectedDestinationId": "Save as PDF",
			"version": 2
		}
	prefs = {
		'printing.print_preview_sticky_settings.appState': json.dumps(settings),
		'savefile.default_directory': pdf_output_directory
	}
	#Chrome driver options
	chrome_options.add_argument("user-data-dir="+ROOT_DIRECTORY+'/chromeOptions/profile')
	chrome_options.add_experimental_option('prefs', prefs)
	chrome_options.add_argument('--kiosk-printing')
	chrome_options.add_argument('--enable-print-browser')
	chrome_options.add_argument('load-extension='+ROOT_DIRECTORY+'/chromeOptions/3.11_0')

	CHROMEDRIVER_PATH = ROOT_DIRECTORY+'/chromedriver.exe'
	#chrome_options.add_argument('binary_location ='+CHROMEDRIVER_PATH)
	#chrome_options.setBinary(CHROMEDRIVER_PATH)
	#MANUAL_CHROMEDRIVER_PATH = 'C:\\Users\\marshall\\Desktop\\Recipe Journal'
	#os.environ["webdriver.chrome.driver"] = CHROMEDRIVER_PATH
	print(CHROMEDRIVER_PATH)
	#Set Chrome Driver Setting
	driver = webdriver.Chrome(options=chrome_options, executable_path=CHROMEDRIVER_PATH)
	#Run Chrome Driver
	driver.get(website)
	print(driver.title)
	# Scroll through page slowly to properly load
	# any unloaded images before rendering to PDF
	#Slight delay for page to fully load
	time.sleep(2)
	total_height = int(driver.execute_script("return document.body.scrollHeight"))
	scroll_speed = 45
	if total_height>=15000: scroll_speed=90
	for i in range(1, total_height, scroll_speed):
		driver.execute_script("window.scrollTo(0, {});".format(i))
	#Create PDF of Website
	driver.execute_script('window.print();')
	#Exit Selenium
	driver.quit()
	print("Completed Website to PDF Conversion!")
	return True

def convertPDFToBase64(pdf_directory=None):
	if pdf_directory==None:
		print("no pdf dir")
		return 1
	print("================")
	print(pdf_directory)
	for file in os.listdir(pdf_directory):
		print(pdf_directory+"/"+file)
		if file.endswith(".pdf"):
			print("(convertPDFToBase64): found pdf!!!!!!!!!!!")
			with open(pdf_directory+"/"+file, "rb") as pdf_file:
				encoded_string = base64.b64encode(pdf_file.read())
				return {'pdf': encoded_string.decode(),'title': str(file)}
	print("couldnt base64 it")
	return 0

def deleteTemporaryDirectory(directory=None,override=True):
	if not directory: return False
	if os.path.exists(directory):
		if override:
			shutil.rmtree(directory)
			print(directory+" deleted with override...")
			return True
		os.rmdir(directory)
		print(directory+" deleted...")
		return True
		
def deletePdfsInDirectory(directory):
	for f in os.listdir(directory):
		if f.endswith(".pdf"):
			os.remove(os.path.join(directory, f))

def extractImagesFromWebsite(website=None,image_output_directory=None):
	# Variables
	image_count = 1
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
	#Website Response
	response = requests.get(website, headers=headers)
	#Soup Parse Reponse
	soup = BeautifulSoup(response.text, 'html.parser')
	# Get all Images Sources on the page
	img_tags = soup.find_all('img')
	#print(img_tags)
	#urls = [img['src'] for img in img_tags]
	for img in img_tags:
		if not 'src' in img:
			continue
		url = img['src']
		#filename = re.search(r'/([\w_-]+[.](jpg|gif|png))$', url)
		if not re.search(r'/([\w_-]+[.](jpg|gif|png))$', url):
			 print("Regex didn't match with the url: {}".format(url))
			 continue
		#with open("{}/image_{}.png".format(image_output_directory,image_count), 'wb') as file:
		if 'http' not in url:
			url = '{}{}'.format(website, url)
		response = requests.get(url, headers=headers)
		print("================================")
		#print(str(image_count))
		print(url)
		#print(base64.b64encode(response.content))
		print("================================")
		break
		#file.write(response.content)
		image_count+=1

def generatePreviewImages(pdf_path=None,preview_output_directory=None,name='preview',poppler_path=ROOT_DIRECTORY+'/poppler-0.68.0/bin'):
	if pdf_path==None or preview_output_directory==None:
		print("generatePreviewImages: pdf_path or output_path are invalid")
		return False
	print(preview_output_directory)
	print(pdf_path)
	images = convert_from_path(pdf_path=pdf_path,poppler_path=poppler_path)
	print(images)
	data = []
	for index,image in enumerate(images):
		print(index)
		# TO BE REMOVED MAYBE
		data.append(convertPilToB64(image))
		#if os.path.exists(preview_output_directory): image.save(preview_output_directory+str(name)+"_"+str(index)+'.png','PNG')
	# TO BE REMOVED MAYBE
	print(len(data))
	return data
	# Check if images were successfully made
	preview_file_count = 1
	# Iterate through all files and find all preview png files
	for file in os.listdir(preview_output_directory):
		print(file)
		if file.endswith(".png") and 'preview' in str(file): preview_file_count+=1
	# Check if the amount of preview png files found is equal to the amount of pdf_images made
	if not preview_file_count == len(images):
		print("generatePreviewImages: Error with Preview Image Creation, data does not match what's found")
		return False
	return True

def extractImagesFromPDF(pdf_path=None,image_output_directory=None,automatic=True):
	data = []
	if pdf_path==None:
		print("extractImagesFromPDF: No pdf_path  inputted")
		return False
	#MIGHT REMOVE CHANGE "AND" BACK TO "OR" MAYBE
	if not os.path.exists(str(pdf_path)):
		print("extractImagesFromPDF: pdf_path not found!")
		return False
	# Functions
	'''
	def findImageDuplicate(image=None,image_output_directory=image_output_directory):
		image_hash = imagehash.average_hash(image)
		for file in os.listdir(image_output_directory):
			if "pdfimage" in file:
				try:	
					file_hash = imagehash.average_hash(Image.open(image_output_directory+file))
					match = SequenceMatcher( None, str(image_hash), str(file_hash) ).ratio()
					print("----------------------")
					print(image_output_directory+file)
					print(image_hash)
					print(file_hash)
					print(match)
					if match>=0.9:
						return True
				except Exception as e:
					print("----------------------")
					print(e)
					print("Could not find anything to compare")
					print("----------------------")
		return False
	'''
	def imageDuplicate():
		pass
	###########################################
	#test
	image_data = []
	###########################################
	# TEMPORARY COUNT REMOVE PROLLY NOT BEST IDEA
	count = 1
	# open the file
	pdf_file = fitz.open(pdf_path)
	# iterate over PDF pages
	for page_index in range(len(pdf_file)):
		# get the page itself
		page = pdf_file[page_index]
		image_list = page.getImageList()
		# printing number of images found in this page
		if not image_list:
			print("[!] No images found on page", page_index)
			continue
		print(f"[+] Found a total of {len(image_list)} images in page {page_index}")
		for image_index, img in enumerate(image_list, start=1):
			# get the XREF of the image
			xref = img[0]
			# base image
			base_image = pdf_file.extractImage(xref)
			# extract the image bytes
			image_bytes = base_image["image"]
			# Image extension
			image_extension = base_image["ext"]
			# load Image w/ PIL
			#print(base_image['image'])
			image = Image.open(io.BytesIO(image_bytes))
			# get image width and height, if less than 48 continue
			width, height = image.size
			if width<48 or height<48:
				continue
			# save it to local disk
			print("{}/image_{}.{}".format(image_output_directory,count,image_extension))
			# PREVIOUS IMAGE SAVE: image.save(open(f"{image_output_directory}image_{image_index}.{image_extension}", "wb"))
			#image.save(open(f"{image_output_directory}pdfimage_{count}.{image_extension}", "wb"))
			final_image = convertPilToB64(image)
			if final_image in data:
				continue
			data.append(final_image)
			image_data.append( {"image":image,"width":width,"height":height,"total":width+height,"ext":image_extension} )
			count=count+1
	if not automatic:
		return data
	if automatic:
		for my_img in image_data:
			print("start========================start")
			print(len(image_data))
			print(my_img['width'])
			print(my_img['height'])
			print(my_img['total'])
			#Only one image
			if len(image_data)==1:
				#my_img['image'].save(open(f"{image_output_directory}chosen_one.{my_img['ext']}", "wb"))
				converted_image = convertPilToB64(my_img['image']) ##########################################
				#print(converted_image)
				return converted_image
			# More than one image, square Image
			my_img['squared'] = abs(my_img['width']-my_img['height'])
			print(my_img['squared'])
		print("end=========================end")
		if len(image_data)>0:
			#Sort by how square the image is (smallest being the most square)
			image_data = sorted(image_data, key=lambda k: k['squared'])
			#Cut the image list in half if there are more than 5 images
			if len(image_data)>5:
				image_data = image_data[:len(image_data)-math.floor(len(image_data)/2)]
			#Pick the image in the middle of the currently sorted list
			chosen_img = image_data[math.ceil(len(image_data)/2)]
			print(image_data)
			print(len(image_data))
			print("chosen one {}".format(chosen_img['image']))
			#chosen_img['image'].save(open(f"{image_output_directory}chosen_one.{chosen_img['ext']}", "wb"))
			converted_image = convertPilToB64(chosen_img['image']) #################################################
			#print(converted_image)
			return converted_image
		return None

#temp_dir=createTemporaryDirectory(output_directory=TEMP_RECIPE_DIRECTORY)
#x=extractImagesFromPDF(pdf_path=PDF_LOCATION,image_output_directory=temp_dir)
#print(x)
#extractImagesFromWebsite("https://www.delish.com/cooking/recipe-ideas/a24892843/how-to-make-omelet/")