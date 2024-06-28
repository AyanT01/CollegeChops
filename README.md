# CollegeChops

CollegeChops is a web application designed to help students discover, search, and share recipes that are easy to make and budget-friendly. Users can search for recipes in the database, upload their own recipes, and browse through a variety of dishes.

## Features

- **Recipe Search**: Search for recipes by name. If a recipe is not found in the database, the app fetches it from an external API.
- **Dynamic Database**: The app fetches new results from the OpenAI API, ensuring a constantly evolving collection of recipes.
- **Recipe Upload**: Users can upload new recipes, including details such as ingredients, instructions, difficulty, and cost.
- **Browse Recipes**: Display recipes from the database on the home page, arranged in a user-friendly layout.

## Getting Started

### Prerequisites

- Python 3.x
- Flask
- SQLAlchemy
- Requests
- OpenAI API Key

### Installation and Execution

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/CollegeChops.git
   cd CollegeChops

### Installation and Execution

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/RecipeViewer.git
   cd RecipeViewer
1. Set up a virtual environment:
   ```bash
   python3 -m venv env
   source env/bin/activate
1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
1. Set the OpenAI API Key as an environment variable (Please make sure you replace `your_openai_api_key` with your actual OpenAI API key):
   ```bash
   export OPENAI_API_KEY=`your_openai_api_key`
   
1. Run the app on your computer
   ```bash
   python flask-server/app.py
1. Running Tests
   ```bash
   python -m unittest test_app.py
