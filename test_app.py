import unittest
from app import app, db, Recipe
import os

class RecipeViewerTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.Config')
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        self.populate_db()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def populate_db(self):
        recipe1 = Recipe(title="Spaghetti Carbonara", description="A classic Italian pasta dish.",
                         ingredients="Spaghetti, Pancetta, Eggs, Parmesan, Black pepper", 
                         instructions="Cook spaghetti. Fry pancetta. Mix eggs and cheese. Combine everything.", 
                         cost=15, difficulty="Medium")
        db.session.add(recipe1)
        db.session.commit()

    def test_home_page(self):
        response = self.app.get('/home')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Spaghetti Carbonara', response.data)

    def test_recipe_detail_page(self):
        recipe = Recipe.query.first()
        response = self.app.get(f'/dishes/{recipe.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Spaghetti Carbonara', response.data)

    def test_search_functionality(self):
        response = self.app.get('/search?query=Spaghetti')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Spaghetti Carbonara', response.data)

    def test_upload_recipe(self):
        response = self.app.post('/uploads', data=dict(
            title="Chicken Teriyaki",
            description="A sweet and savory Japanese dish.",
            ingredients="Chicken, Soy Sauce, Mirin, Sugar, Garlic",
            instructions="Marinate chicken. Cook in a pan. Serve with sauce.",
            difficulty="Easy",
            cost=10
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Success', response.data)
        recipe = Recipe.query.filter_by(title="Chicken Teriyaki").first()
        self.assertIsNotNone(recipe)

if __name__ == '__main__':
    unittest.main()
