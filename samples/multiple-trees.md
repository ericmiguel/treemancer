# Project Structure Examples

This file contains various project structure examples that can be used with tree-creator.

## Python Web Project

```
web_project/
├── README.md
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── product.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── auth.py
│   └── utils/
│       ├── __init__.py
│       ├── database.py
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   ├── test_models.py
│   └── test_api.py
├── migrations/
│   └── init.sql
└── docs/
    ├── api.md
    └── deployment.md
```

## React Frontend Project

```
frontend/
├── package.json
├── package-lock.json
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── index.js
│   ├── App.js
│   ├── components/
│   │   ├── Header.js
│   │   ├── Footer.js
│   │   └── Navigation.js
│   ├── pages/
│   │   ├── Home.js
│   │   ├── About.js
│   │   └── Contact.js
│   ├── hooks/
│   │   ├── useAuth.js
│   │   └── useApi.js
│   └── utils/
│       ├── api.js
│       └── constants.js
├── tests/
│   ├── components/
│   │   └── Header.test.js
│   └── pages/
│       └── Home.test.js
└── build/
```

## Machine Learning Project

* ml_project
  * README.md
  * requirements.txt
  * config.yml
  * data
    * raw
      * dataset.csv
    * processed
      * clean_data.csv
    * external
      * reference.json
  * notebooks
    * 01_exploration.ipynb
    * 02_preprocessing.ipynb
    * 03_modeling.ipynb
  * src
    * __init__.py
    * data_processing.py
    * feature_engineering.py
    * models
      * __init__.py
      * base_model.py
      * neural_network.py
    * utils
      * __init__.py
      * visualization.py
      * metrics.py
  * tests
    * test_data_processing.py
    * test_models.py
  * models
    * model_v1.pkl
    * model_v2.pkl
  * reports
    * figures
      * correlation_matrix.png
    * final_report.md

## Microservices Architecture

```
microservices/
├── docker-compose.yml
├── .env
├── api-gateway/
│   ├── Dockerfile
│   ├── package.json
│   ├── src/
│   │   ├── index.js
│   │   ├── routes/
│   │   │   └── proxy.js
│   │   └── middleware/
│   │       ├── auth.js
│   │       └── logging.js
│   └── tests/
│       └── gateway.test.js
├── user-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   └── database.py
│   └── tests/
│       └── test_user_service.py
├── product-service/
│   ├── Dockerfile
│   ├── go.mod
│   ├── main.go
│   ├── handlers/
│   │   └── product.go
│   ├── models/
│   │   └── product.go
│   └── tests/
│       └── product_test.go
└── shared/
    ├── configs/
    │   ├── database.yml
    │   └── redis.yml
    └── scripts/
        ├── deploy.sh
        └── migrate.sh
```

## Usage Examples

### Create first tree only
```bash
tree-creator from-file examples/project_structures.md
```

### Create all trees with numbered directories  
```bash
tree-creator from-file examples/project_structures.md --all-trees --output ./generated
```

### Preview before creating
```bash
tree-creator from-file examples/project_structures.md --preview --dry-run
```

### Create without files (directories only)
```bash
tree-creator from-file examples/project_structures.md --no-files
```