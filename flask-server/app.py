import os
import json
import re
from flask import Flask, render_template, request, redirect, url_for
from openai import OpenAI
from models import db, Recipe

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# Ensure the API key is set in the environment variables
key = os.getenv("OPENAI_API_KEY")
if not key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable")

# Configure the OpenAI client
client = OpenAI(api_key=key)

def generate_json(search_term):
    prompt = f"""
    Generate a list of 5 dishes in valid JSON format that have {search_term} as the main ingredient and are easy for college students to make. The JSON should be a well-formed array of objects. Include the following fields for each dish: title, description, ingredients, instructions, cost, and difficulty. Ensure that the JSON is syntactically correct and does not contain any trailing commas or other formatting errors.

    Rules:
    1. Each dish must be enclosed in a single pair of curly braces `{{}}`.
    2. The entire list of dishes must be enclosed in square brackets `[]`.
    3. Each field (title, description, ingredients, instructions, cost, difficulty) must be present and must be enclosed in double quotes `""`.
    4. The ingredients and instructions fields must be arrays and must not have trailing commas.
    5. The cost field must be a string in the format "$x-y" where x and y are integers.
    6. The difficulty field must be one of the following: "Easy", "Medium", or "Hard".
    7. Ensure there are no extra commas, especially at the end of lists or objects.
    8. Provide exactly 5 dishes in the output.
    """
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

def correct_json_format(incorrect_json):
    prompt = f"""
    The following JSON object is incorrectly formatted. Please correct it so that it follows the proper JSON syntax. Ensure that:

    1. Each dish is enclosed in a single pair of curly braces `{{}}`.
    2. The entire list of dishes is enclosed in square brackets `[]`.
    3. Each field (title, description, ingredients, instructions, cost, difficulty) is present and enclosed in double quotes `""`.
    4. The ingredients and instructions fields are arrays and do not have trailing commas.
    5. The cost field is a string in the format "$x-y" where x and y are integers between 10 and 20.
    6. The difficulty field is one of the following: "Easy", "Medium", or "Hard".
    7. There are no extra commas, especially at the end of lists or objects.
    8. Provide exactly 5 dishes in the corrected output.

    Here is the incorrect JSON object:

    ```
    {incorrect_json}
    ```

    Ensure the corrected JSON output follows these rules exactly.
    """
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

def clean_and_parse_json(response_text):
    try:
        start_index = response_text.index('[')
        end_index = response_text.rindex(']') + 1
        json_text = response_text[start_index:end_index]
        
        # Remove trailing commas before parsing
        json_text = re.sub(r',\s*([}\]])', r'\1', json_text)
        
        # Debugging: Print the cleaned JSON text
        print("Cleaned JSON text:", json_text)
        
        # Load the JSON text into a Python object
        recipes = json.loads(json_text)
        return recipes
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Error decoding JSON: {e}")
        return []

def add_recipes_to_db(recipes):
    valid_recipes = []
    
    # Process valid recipes to match the database schema
    for r in recipes:
        try:
            cost_range = r['cost'].replace("$", "").replace("-", "").strip().split("-")
            cost = int(cost_range[-1])  # Pick the upper range as the cost
            valid_recipes.append({
                'title': r['title'],
                'description': r['description'],
                'ingredients': ", ".join(r['ingredients']),
                'instructions': " ".join(r['instructions']),
                'cost': cost,
                'difficulty': r['difficulty']
            })
        except Exception as e:
            print(f"Error parsing recipe: {e}")
            continue
    
    # Debugging: Print valid recipes before adding to database
    print("Valid recipes to be added to the database:", valid_recipes)
    
    # Add valid recipes to the database
    with app.app_context():
        for r in valid_recipes:
            try:
                #if not Recipe.query.filter_by(title=r['title']).first():
                new_recipe = Recipe(
                    title=r['title'],
                    description=r['description'],
                    ingredients=r['ingredients'],
                    instructions=r['instructions'],
                    cost=r['cost'],
                    difficulty=r['difficulty']
                )
                db.session.add(new_recipe)
                db.session.commit()
                print(f"Added recipe to the database: {new_recipe}")
            except Exception as e:
                print(f"Error adding recipe to the database: {e}")

@app.route('/home')
def home():
    dishes = Recipe.query.all()
    return render_template("home.html", dishes=dishes)

@app.route("/uploads", methods=["GET", "POST"])
def uploads():
    if request.method == "POST":
        # Handle form submission
        title = request.form.get('title')
        description = request.form.get('description')
        ingredients = request.form.get('ingredients')
        instructions = request.form.get('instructions')
        difficulty = request.form.get('difficulty')
        cost = request.form.get('cost')
        #image = request.files['image']  # Uploaded file - Tentative
        new_recipe = Recipe(
            title=title, description=description,
            ingredients=ingredients,
            instructions=instructions,
            difficulty=difficulty, cost=cost)
        db.session.add(new_recipe)
        db.session.commit()
        return redirect(url_for('success'))

    return render_template("uploads.html")

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/dishes/<int:dish_id>")
def dish(dish_id):
    recipe = Recipe.query.get_or_404(dish_id)
    print(recipe)
    return render_template("dish.html", recipe=recipe)

@app.route('/search')
def search():
    query = request.args.get('query')
    results = []
    if query:
        search_query = "%{}%".format(query)
        results = Recipe.query.filter(
            (Recipe.title.ilike(search_query)) |
            (Recipe.description.ilike(search_query)) |
            (Recipe.ingredients.ilike(search_query)) |
            (Recipe.instructions.ilike(search_query))
        ).all()
        
        if not results:
            incorrect_json = generate_json(query)
            corrected_json = correct_json_format(incorrect_json)
            parsed_recipes = clean_and_parse_json(corrected_json)
            add_recipes_to_db(parsed_recipes)
            results = Recipe.query.filter(
                (Recipe.title.ilike(search_query)) |
                (Recipe.description.ilike(search_query)) |
                (Recipe.ingredients.ilike(search_query)) |
                (Recipe.instructions.ilike(search_query))
            ).all()
    return render_template('search_results.html', query=query, results=results)

if __name__ == '__main__':
    app.run(debug=True)