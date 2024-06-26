import pytest
from server import app  # Import SQLAlchemy db and Flask app

from models import Recipe, db

@pytest.fixture(scope='module')
def setup_db():
    """Fixture to set up and tear down database for tests."""
    db.create_all()  # Create all tables
    yield db  # Pass the db object to tests
    db.session.remove()  # Clean up session
    db.drop_all()  # Drop all tables

def test_create_recipe(setup_db):
    """Test creating and retrieving a recipe."""
    # Create a new recipe object
    new_recipe = Recipe(
        title='Spaghetti Carbonara',
        description='Classic Italian pasta dish',
        ingredients='Pasta, eggs, bacon, Parmesan cheese',
        instructions='Cook pasta, fry bacon, mix with eggs and cheese',
        difficulty='Medium',
        cost=15  # Example cost in units
    )

    # Add and commit the new recipe to the database
    db.session.add(new_recipe)
    db.session.commit()

    # Retrieve the recipe from the database
    retrieved_recipe = Recipe.query.filter_by(title='Spaghetti Carbonara').first()
    print(retrieved_recipe)
    # Assert that the retrieved recipe matches the one added
    assert retrieved_recipe.title == 'Spaghetti Carbonara'
    assert retrieved_recipe.description == 'Classic Italian pasta dish'
    assert retrieved_recipe.ingredients == 'Pasta, eggs, bacon, Parmesan cheese'
    assert retrieved_recipe.instructions == 'Cook pasta, fry bacon, mix with eggs and cheese'
    assert retrieved_recipe.difficulty == 'Medium'
    assert retrieved_recipe.cost == 15
test_create_recipe(db)