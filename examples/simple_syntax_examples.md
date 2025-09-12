# Simple Syntax Examples for Tree Creator

This file contains examples of the simple syntax format using > and | operators.

## Basic Examples

### Simple file structure
root > file1.py file2.py file3.py

### Basic directory with files  
project > README.md main.py utils.py

### Nested directories
project > src > main.py utils.py

### Mixed structure with pipe operator
project > README.md src > main.py | tests > test_main.py

## Web Application Examples

### Flask/FastAPI Project
web_app > app.py requirements.txt config.py models > user.py product.py | routes > auth.py api.py | tests > test_models.py test_routes.py | static > css > style.css | js > app.js | templates > index.html base.html

### Django Project  
django_project > manage.py requirements.txt myapp > __init__.py admin.py apps.py models.py views.py urls.py | migrations > __init__.py | templates > myapp > index.html | static > myapp > css > style.css | js > main.js

## Data Science Examples

### ML Project Structure
ml_project > README.md requirements.txt config.yml data > raw > dataset.csv | processed > clean_data.csv | notebooks > exploration.ipynb modeling.ipynb | src > data_processing.py feature_engineering.py models > model.py | tests > test_processing.py | models > trained_model.pkl

### Data Analysis Project
data_analysis > data > raw_data.csv processed_data.csv | scripts > clean_data.py analyze.py visualize.py | notebooks > analysis.ipynb | reports > figures > plot1.png plot2.png | report.md

## Mobile App Examples

### React Native Project
mobile_app > package.json App.js src > components > Header.js Footer.js Button.js | screens > HomeScreen.js ProfileScreen.js | navigation > AppNavigator.js | utils > api.js constants.js | assets > images > logo.png | fonts > custom.ttf

### Flutter Project
flutter_app > pubspec.yaml lib > main.dart models > user.dart product.dart | screens > home_screen.dart profile_screen.dart | widgets > custom_button.dart loading_widget.dart | services > api_service.dart auth_service.dart | utils > constants.dart helpers.dart | test > widget_test.dart

## Backend API Examples

### Node.js Express API
api_server > package.json server.js src > controllers > userController.js productController.js | middleware > auth.js logging.js | models > User.js Product.js | routes > users.js products.js | utils > database.js validation.js | tests > user.test.js product.test.js | config > database.js

### Python FastAPI
fastapi_app > main.py requirements.txt app > models > user.py product.py | routers > users.py products.py auth.py | database > connection.py | middleware > cors.py auth.py | utils > security.py validation.py | tests > test_users.py test_products.py | alembic > versions > init.py

## DevOps Examples

### Docker Setup
containerized_app > Dockerfile docker-compose.yml .dockerignore src > app.py requirements.txt | config > production.yml development.yml | scripts > deploy.sh backup.sh | tests > integration_tests.py

### Kubernetes Configuration  
k8s_app > deployment.yaml service.yaml configmap.yaml | manifests > namespace.yaml ingress.yaml | scripts > deploy.sh rollback.sh | monitoring > alerts.yaml dashboard.json

## Complex Project Examples

### Full-Stack Application
fullstack_app > README.md docker-compose.yml frontend > package.json src > components > App.js Header.js | pages > Home.js About.js | utils > api.js | public > index.html | backend > requirements.txt main.py app > models > user.py | routes > api.py auth.py | database > connection.py migrations > init.sql | tests > test_api.py | nginx > nginx.conf | scripts > setup.sh deploy.sh

### Microservices Architecture
microservices > docker-compose.yml .env user_service > Dockerfile requirements.txt app > main.py models.py routes.py | tests > test_user.py | product_service > Dockerfile go.mod main.go handlers > product.go | models > product.go | tests > product_test.go | api_gateway > package.json src > index.js routes > proxy.js | middleware > auth.js | shared > configs > database.yml redis.yml | scripts > deploy.sh migrate.sh

## Game Development Examples  

### Unity Game Project
unity_game > Assets > Scripts > Player.cs Enemy.cs GameManager.cs | Scenes > MainMenu.unity GameScene.unity | Prefabs > Player.prefab Enemy.prefab | Materials > PlayerMaterial.mat | Textures > player.png background.png | Audio > music.mp3 sound_effects.wav | ProjectSettings > ProjectSettings.asset

### Godot Game Project
godot_game > project.godot scenes > Main.tscn Player.tscn Enemy.tscn | scripts > Player.gd Enemy.gd GameManager.gd | assets > sprites > player.png enemy.png | sounds > jump.wav shoot.wav | fonts > game_font.ttf

## Documentation Examples

### Documentation Site
docs_site > mkdocs.yml requirements.txt docs > index.md getting_started.md api_reference.md | tutorials > basic_usage.md advanced_features.md | examples > code_samples.py | images > architecture.png screenshot.png | stylesheets > custom.css

### Technical Writing Project  
tech_docs > README.md content > introduction.md user_guide.md developer_guide.md | api > endpoints.md authentication.md | tutorials > getting_started.md best_practices.md | assets > diagrams > architecture.svg workflow.png | templates > document_template.md