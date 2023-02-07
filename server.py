from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import RecipeMaker as rm
import json
import base64
import os
import find_foods as find_food

database_path = os.path.abspath(os.getcwd())+"/database/test.db"

# Define Flask and SocketIO Server
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+database_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
#socketio = SocketIO(app)

class MyRecipe(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(200), nullable=False, unique=True)
	pdf_location = db.Column(db.String(300), nullable=False)
	avatar = db.Column(db.String, nullable=True)
	food_type = db.Column(db.String(50), nullable=True)
	favorite = db.Column(db.Boolean, default=False)

	def __init__(self,title,pdf_location,avatar,food_type):
		self.title = title
		self.pdf_location = pdf_location
		self.avatar = avatar
		self.food_type = food_type
		#self.favorite = False

#Takes the recipe data from (RecipeMaker)createTemporaryRecipe and adds everything to the database
def addToDatabase(recipe_data=None):
	if not recipe_data: return None
	#Auto Add
	for recipe in recipe_data['success']:
		try:
			pdf_directory = "{}/{}.pdf".format(rm.RECIPE_DIRECTORY,recipe['title'])
			#Save PDF as file in recipe folder
			f = open(pdf_directory, 'wb')
			f.write( base64.b64decode( recipe['pdf'].replace('data:application/pdf;base64,', '') ) )
			f.close()
			#Add to Database
			db_recipe = MyRecipe(title=recipe['title'],pdf_location=pdf_directory,avatar=recipe['image'],food_type=recipe['food_type'])
			db.session.add(db_recipe)
			db.session.commit()
		except Exception as e:
			print("ERROR IN ADD TO DATABASE ERRORR ERROR")
			print(e)
			recipe_data['error'].append({
				"error": "Database: Error adding to the database",
				"name": recipe['title']
			})
			recipe_data['success'].remove(recipe)
			#Delete PDF from file path if exists
			pdf_file_path = "{}/{}.pdf".format(rm.RECIPE_DIRECTORY,recipe['title'])
			if os.path.exists(pdf_file_path):
				os.remove(pdf_file_path)
				print("Found PDF of {} Deleting...".format(recipe['title']))

# Flask Functions
@app.route('/')
def home():
	return render_template('home.html')

@app.route('/return_food_types', methods=['GET'])
def return_food_types():
	return {"types": find_food.returnFoodTypes()}

@app.route('/return_recipe_image', methods=['GET','POST'])
def returnImages():
	recipe = request.get_json()
	print("------------------------------------")
	print(recipe)
	recipe_title = recipe['recipe_name']
	recipe_exists = db.session.query(MyRecipe).filter_by(title=recipe_title).all()[0]
	print(recipe_title)
	if recipe_exists:
		print("(returnImages): Recipe found...")
		print(recipe_exists)
		print(recipe_exists.pdf_location)
		current_pdf_directory = "{}/{}.pdf".format(rm.RECIPE_DIRECTORY,recipe_exists.title)
		print(current_pdf_directory)
		#temp_dir=rm.createTemporaryDirectory(output_directory=rm.TEMP_RECIPE_DIRECTORY)
		images=rm.extractImagesFromPDF(pdf_path=current_pdf_directory,automatic=False)
		#rm.deleteTemporaryDirectory(directory=temp_dir)
		print(images)
		#print(len(images))
		return {'result': images}
	print("Couldn't find it")
	return {'result': False}


@app.route('/return_database', methods=['GET'])
def database():
	print("returning database...")
	data_to_return = []
	for value in db.session.query(MyRecipe).order_by(func.lower(MyRecipe.title)).all():
		final_value = value.__dict__
		final_value.pop('_sa_instance_state')
		data_to_return.append(final_value)
	return jsonify(data_to_return)

@app.route('/update_recipe_image', methods=['GET','POST'])
def updateRecipeImage():
	recipe = request.get_json()
	recipe_exists = db.session.query(MyRecipe).filter_by(title=recipe['name']).all()[0]
	if recipe_exists:
		print("(updateRecipeImage): Recipe found...")
		print(recipe_exists)
		recipe_exists.avatar = recipe['image']
		db.session.commit()
		return {'result': True}
	return {'result': False}

@app.route('/update_recipe_type', methods=['GET','POST'])
def updateRecipeType():
	recipe = request.get_json()
	recipe_exists = db.session.query(MyRecipe).filter_by(title=recipe['name']).all()[0]
	if recipe_exists:
		print("(updateRecipeImage): Recipe found...")
		print(updateRecipeType)
		recipe_exists.food_type = recipe['type'].lower()
		db.session.commit()
		return {'result': True}
	return {'result': False}

@app.route('/toggle_recipe_favorite', methods=['GET','POST'])
def updateRecipeFavorites():
	recipe = request.get_json()
	recipe_exists = db.session.query(MyRecipe).filter_by(title=recipe['name']).all()[0]
	if recipe_exists:
		print("(updateRecipeFavorites): Recipe found...")
		print(recipe_exists)
		recipe_exists.favorite = not recipe_exists.favorite
		db.session.commit()
		return {'result': True}
	return {'result': False}

@app.route('/update_recipe_title', methods=['GET','POST'])
def updateRecipeName():
	recipe = request.get_json()
	recipe_exists = db.session.query(MyRecipe).filter_by(title=recipe['title']).all()[0]
	if not recipe_exists: return {'result': False}
	# Initalize current pdf directory
	current_pdf_directory = "{}/{}.pdf".format(rm.RECIPE_DIRECTORY,recipe_exists.title)
	# Initalize new_pdf_location
	new_pdf_location = "{}/{}.pdf".format(rm.RECIPE_DIRECTORY,recipe['new_title'])
	if not os.path.exists(current_pdf_directory): return {'result': False}
	# Debug Messages
	print("(updateRecipeName): Recipe and PDF found...")
	print(recipe_exists)
	print(recipe_exists.pdf_location)
	print(new_pdf_location)
	# Rename PDF File
	os.rename(current_pdf_directory,"{}/{}.pdf".format(rm.RECIPE_DIRECTORY,recipe['new_title']))
	# Update recipe title on database
	recipe_exists.title = recipe['new_title']
	# Update pdf_location on database
	recipe_exists.pdf_location = new_pdf_location
	db.session.commit()
	return {'result': True}

# Route will upload all recipe data to the database automatically
# Data will be sent back to the server to show what recipes were
# successfully uploaded and which ones ran into an error
@app.route('/upload_automatic', methods=['GET','POST'])
def download_file():
	if request.method == "POST":
		print("Beginning Automatic Upload...")
		post_data = request.get_json()
		data_to_return = rm.createTemporaryRecipe(recipeFormData=post_data,automatic=True)
		print("FINISHSSSSSSSSSSSSS")
		if data_to_return:
			for item in data_to_return['success']:
				print(item)
		addToDatabase(data_to_return)
		print(data_to_return)
		return json.dumps(data_to_return)
		#data_to_return = rm.createTemporaryRecipe(websites=post_data['websites'],pdfs=post_data['pdfs'],automatic=True)
		
	return json.dumps(data_to_return)

@app.route('/delete_recipe', methods=['POST','GET'])
def deleteRecipe():
	recipe = request.get_json()
	recipe_exists = db.session.query(MyRecipe).filter_by(title=recipe['recipe_name']).all()
	print(recipe['recipe_name'])
	if recipe_exists:
		print("(deleteRecipe): Recipe found deleting...")
		#Delete from database
		db.session.query(MyRecipe).filter_by(title=recipe['recipe_name']).delete()
		db.session.commit()
		#Delete PDF File
		pdf_file_path = "{}/{}.pdf".format(rm.RECIPE_DIRECTORY,recipe['recipe_name'])
		if os.path.exists(pdf_file_path):
			print("found ittttttttttttttttttttttttttttttttttttttttttttttttt")
			os.remove(pdf_file_path)
		return json.dumps(True)
	print("(deleteRecipe): Recipe not found, can't delete...")
	return json.dumps(False)

@app.route('/file', methods=['GET','POST'])
def file():
	files = request.get_json()
	print(files)
	return json.dumps(files)

@app.route('/recipe/<path:filename>')
def base_static(filename):
    return send_from_directory(app.root_path + '/recipe/', filename)

if __name__ == '__main__':
	db.create_all()
	#app.run()
	app.run(host="0.0.0.0",port="5001")