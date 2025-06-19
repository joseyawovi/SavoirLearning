
"""
Management command to create a comprehensive Data Science Fundamentals roadmap.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from lms.models import Roadmap, Room, Section, Question, Enrollment

User = get_user_model()


class Command(BaseCommand):
    help = 'Create Data Science Fundamentals roadmap with 5 rooms and comprehensive content'

    def handle(self, *args, **options):
        self.stdout.write('Creating Data Science Fundamentals roadmap...')
        
        # Create the roadmap
        roadmap, created = Roadmap.objects.get_or_create(
            title='Data Science Fundamentals',
            defaults={
                'title_fr': 'Fondamentaux de la Science des Données',
                'description': 'Master the essential skills for data science including Python, statistics, machine learning, and data visualization.',
                'description_fr': 'Maîtrisez les compétences essentielles pour la science des données incluant Python, les statistiques, l\'apprentissage automatique et la visualisation de données.',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'Created roadmap: {roadmap.title}')
        
        # Room 1: Python for Data Science
        python_room = self.create_room(
            roadmap, "Python for Data Science", "Python pour la Science des Données",
            "Learn Python programming fundamentals specifically for data science applications.",
            "Apprenez les fondamentaux de la programmation Python spécifiquement pour les applications de science des données.",
            order=1
        )
        
        # Room 2: Data Manipulation and Analysis
        data_room = self.create_room(
            roadmap, "Data Manipulation and Analysis", "Manipulation et Analyse de Données",
            "Master pandas, NumPy, and data preprocessing techniques.",
            "Maîtrisez pandas, NumPy et les techniques de préprocessing des données.",
            order=2, prerequisite=python_room
        )
        
        # Room 3: Statistics and Probability
        stats_room = self.create_room(
            roadmap, "Statistics and Probability", "Statistiques et Probabilités",
            "Understand statistical concepts essential for data science.",
            "Comprenez les concepts statistiques essentiels pour la science des données.",
            order=3, prerequisite=data_room
        )
        
        # Room 4: Data Visualization
        viz_room = self.create_room(
            roadmap, "Data Visualization", "Visualisation de Données",
            "Create compelling visualizations using matplotlib, seaborn, and plotly.",
            "Créez des visualisations convaincantes en utilisant matplotlib, seaborn et plotly.",
            order=4, prerequisite=stats_room
        )
        
        # Room 5: Machine Learning Basics
        ml_room = self.create_room(
            roadmap, "Machine Learning Basics", "Bases de l'Apprentissage Automatique",
            "Introduction to machine learning algorithms and implementation.",
            "Introduction aux algorithmes d'apprentissage automatique et à leur implémentation.",
            order=5, prerequisite=viz_room
        )
        
        # Create content for each room
        self.create_python_content(python_room)
        self.create_data_content(data_room)
        self.create_stats_content(stats_room)
        self.create_viz_content(viz_room)
        self.create_ml_content(ml_room)
        
        # Auto-enroll admin user if exists
        try:
            admin_user = User.objects.get(username='admin')
            Enrollment.objects.get_or_create(
                user=admin_user,
                roadmap=roadmap,
                defaults={'is_active': True}
            )
            self.stdout.write(f'Enrolled admin user in {roadmap.title}')
        except User.DoesNotExist:
            pass
        
        self.stdout.write(self.style.SUCCESS('Data Science Fundamentals roadmap created successfully!'))
    
    def create_room(self, roadmap, title, title_fr, description, description_fr, order, prerequisite=None):
        """Create a room with given details."""
        room, created = Room.objects.get_or_create(
            title=title,
            roadmap=roadmap,
            defaults={
                'title_fr': title_fr,
                'description': description,
                'description_fr': description_fr,
                'prerequisite_room': prerequisite,
                'order': order,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'  Created room: {title}')
        return room
    
    def create_section(self, room, title, title_fr, content, content_fr, order):
        """Create a section with given details."""
        section, created = Section.objects.get_or_create(
            room=room,
            title=title,
            defaults={
                'title_fr': title_fr,
                'content': content,
                'content_fr': content_fr,
                'order': order,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'    Created section: {title}')
        return section
    
    def create_question(self, section, prompt, prompt_fr, correct_answer, placeholder_hint, order):
        """Create a section quiz question."""
        Question.objects.get_or_create(
            section=section,
            question_type='section',
            prompt=prompt,
            defaults={
                'prompt_fr': prompt_fr,
                'correct_answer': correct_answer,
                'placeholder_hint': placeholder_hint,
                'order': order,
                'is_active': True
            }
        )
    
    def create_final_question(self, room, prompt, prompt_fr, correct_answer, placeholder_hint, order):
        """Create a final exam question."""
        Question.objects.get_or_create(
            room=room,
            question_type='final',
            prompt=prompt,
            defaults={
                'prompt_fr': prompt_fr,
                'correct_answer': correct_answer,
                'placeholder_hint': placeholder_hint,
                'order': order,
                'is_active': True
            }
        )
    
    def create_python_content(self, room):
        """Create content for Python for Data Science room."""
        
        # Section 1: Python Basics
        section1 = self.create_section(
            room, "Python Basics", "Bases de Python",
            """Python is a powerful programming language widely used in data science due to its simplicity and extensive libraries.

Key concepts covered:
- Variables and data types
- Control structures (if/else, loops)
- Functions and modules
- Lists, dictionaries, and tuples
- File handling

Python's syntax is clean and readable, making it ideal for data analysis tasks. Understanding these fundamentals is crucial for data science work.

Example:
```python
# Variables and data types
name = "Data Scientist"
age = 30
salary = 75000.50
is_employed = True

# Lists for data storage
temperatures = [23.5, 24.1, 22.8, 25.3]
print(f"Average temperature: {sum(temperatures)/len(temperatures)}")
```""",
            """Python est un langage de programmation puissant largement utilisé en science des données en raison de sa simplicité et de ses bibliothèques étendues.

Concepts clés couverts:
- Variables et types de données
- Structures de contrôle (if/else, boucles)
- Fonctions et modules
- Listes, dictionnaires et tuples
- Gestion des fichiers

La syntaxe de Python est claire et lisible, ce qui le rend idéal pour les tâches d'analyse de données.""",
            order=1
        )
        
        # Section 1 questions
        self.create_question(
            section1, "What is the correct way to create a list in Python?",
            "Quelle est la bonne façon de créer une liste en Python?",
            "[]", "[ ]", 1
        )
        
        self.create_question(
            section1, "Which keyword is used to define a function in Python?",
            "Quel mot-clé est utilisé pour définir une fonction en Python?",
            "def", "___", 2
        )
        
        # Section 2: Libraries and Packages
        section2 = self.create_section(
            room, "Essential Libraries", "Bibliothèques Essentielles",
            """Python's strength in data science comes from its rich ecosystem of libraries and packages.

Essential libraries for data science:
- **NumPy**: Numerical computing with arrays
- **Pandas**: Data manipulation and analysis
- **Matplotlib**: Basic plotting and visualization
- **Seaborn**: Statistical data visualization
- **Scikit-learn**: Machine learning algorithms
- **Jupyter**: Interactive development environment

Installing packages:
```bash
pip install numpy pandas matplotlib seaborn scikit-learn jupyter
```

Importing libraries:
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import datasets
```

These libraries form the foundation of the Python data science stack and will be used throughout your data science journey.""",
            """La force de Python en science des données provient de son riche écosystème de bibliothèques et de packages.

Bibliothèques essentielles pour la science des données:
- **NumPy**: Calcul numérique avec des tableaux
- **Pandas**: Manipulation et analyse de données
- **Matplotlib**: Tracé de base et visualisation
- **Seaborn**: Visualisation de données statistiques
- **Scikit-learn**: Algorithmes d'apprentissage automatique
- **Jupyter**: Environnement de développement interactif""",
            order=2
        )
        
        # Section 2 questions
        self.create_question(
            section2, "Which library is primarily used for numerical computing in Python?",
            "Quelle bibliothèque est principalement utilisée pour le calcul numérique en Python?",
            "NumPy", "Nu___", 1
        )
        
        self.create_question(
            section2, "What command is used to install Python packages?",
            "Quelle commande est utilisée pour installer les packages Python?",
            "pip install", "pip ______", 2
        )
        
        # Section 3: Development Environment
        section3 = self.create_section(
            room, "Development Environment", "Environnement de Développement",
            """Setting up an effective development environment is crucial for productive data science work.

Popular development environments:
- **Jupyter Notebook**: Interactive web-based environment
- **JupyterLab**: Next-generation interface for Jupyter
- **VS Code**: Versatile code editor with Python extensions
- **PyCharm**: Professional Python IDE
- **Google Colab**: Cloud-based Jupyter environment

Jupyter Notebook basics:
- Cells can contain code or markdown
- Execute cells with Shift+Enter
- Variables persist between cells
- Great for exploratory data analysis

Virtual environments:
```bash
# Create virtual environment
python -m venv data_science_env

# Activate (Windows)
data_science_env\Scripts\activate

# Activate (Mac/Linux)
source data_science_env/bin/activate
```

Best practices:
- Use virtual environments for projects
- Document your code with comments
- Follow PEP 8 style guidelines
- Version control with Git""",
            """La configuration d'un environnement de développement efficace est cruciale pour un travail productif en science des données.

Environnements de développement populaires:
- **Jupyter Notebook**: Environnement interactif basé sur le web
- **JupyterLab**: Interface de nouvelle génération pour Jupyter
- **VS Code**: Éditeur de code polyvalent avec extensions Python
- **PyCharm**: IDE Python professionnel
- **Google Colab**: Environnement Jupyter basé sur le cloud""",
            order=3
        )
        
        # Section 3 questions
        self.create_question(
            section3, "Which keyboard shortcut executes a cell in Jupyter Notebook?",
            "Quel raccourci clavier exécute une cellule dans Jupyter Notebook?",
            "Shift+Enter", "Shift+_____", 1
        )
        
        self.create_question(
            section3, "What is the purpose of virtual environments in Python?",
            "Quel est le but des environnements virtuels en Python?",
            "isolate project dependencies", "isolate project ____________", 2
        )
        
        # Final exam questions
        self.create_final_question(
            room, "Write the Python code to import pandas with the alias 'pd'",
            "Écrivez le code Python pour importer pandas avec l'alias 'pd'",
            "import pandas as pd", "import ______ as __", 1
        )
        
        self.create_final_question(
            room, "What data type would you use to store a collection of key-value pairs in Python?",
            "Quel type de données utiliseriez-vous pour stocker une collection de paires clé-valeur en Python?",
            "dictionary", "__________", 2
        )
        
        self.create_final_question(
            room, "Which command creates a new virtual environment named 'myenv'?",
            "Quelle commande crée un nouvel environnement virtuel nommé 'myenv'?",
            "python -m venv myenv", "python -m ____ myenv", 3
        )
    
    def create_data_content(self, room):
        """Create content for Data Manipulation and Analysis room."""
        
        # Section 1: Introduction to Pandas
        section1 = self.create_section(
            room, "Introduction to Pandas", "Introduction à Pandas",
            """Pandas is the most important library for data manipulation and analysis in Python. It provides data structures and operations for manipulating numerical tables and time series.

Key data structures:
- **Series**: 1-dimensional labeled array
- **DataFrame**: 2-dimensional labeled data structure

Creating DataFrames:
```python
import pandas as pd

# From dictionary
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'City': ['New York', 'London', 'Tokyo']
}
df = pd.DataFrame(data)

# From CSV file
df = pd.read_csv('data.csv')

# Basic info
print(df.head())      # First 5 rows
print(df.info())      # Data types and non-null counts
print(df.describe())  # Statistical summary
```

Essential operations:
- Selecting columns: `df['column_name']` or `df.column_name`
- Filtering rows: `df[df['Age'] > 25]`
- Basic statistics: `df.mean()`, `df.sum()`, `df.count()`""",
            """Pandas est la bibliothèque la plus importante pour la manipulation et l'analyse de données en Python. Elle fournit des structures de données et des opérations pour manipuler des tableaux numériques et des séries temporelles.

Structures de données clés:
- **Series**: Tableau étiqueté à 1 dimension
- **DataFrame**: Structure de données étiquetée à 2 dimensions""",
            order=1
        )
        
        # Section 1 questions
        self.create_question(
            section1, "What is the main 2-dimensional data structure in pandas?",
            "Quelle est la principale structure de données à 2 dimensions dans pandas?",
            "DataFrame", "Data_____", 1
        )
        
        self.create_question(
            section1, "Which method displays the first 5 rows of a DataFrame?",
            "Quelle méthode affiche les 5 premières lignes d'un DataFrame?",
            "head()", "______()", 2
        )
        
        # Section 2: Data Cleaning
        section2 = self.create_section(
            room, "Data Cleaning", "Nettoyage des Données",
            """Data cleaning is often the most time-consuming part of data analysis. Real-world data is messy and requires preprocessing before analysis.

Common data quality issues:
- Missing values (NaN, null)
- Duplicate records
- Inconsistent formatting
- Outliers and errors
- Wrong data types

Handling missing values:
```python
# Check for missing values
print(df.isnull().sum())
print(df.info())

# Remove rows with missing values
df_clean = df.dropna()

# Fill missing values
df['Age'].fillna(df['Age'].mean(), inplace=True)
df['Category'].fillna('Unknown', inplace=True)

# Forward fill or backward fill
df['Price'].fillna(method='ffill', inplace=True)
```

Removing duplicates:
```python
# Check for duplicates
print(df.duplicated().sum())

# Remove duplicates
df = df.drop_duplicates()

# Remove duplicates based on specific columns
df = df.drop_duplicates(subset=['Name', 'Email'])
```

Data type conversion:
```python
# Convert data types
df['Date'] = pd.to_datetime(df['Date'])
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
df['Category'] = df['Category'].astype('category')
```""",
            """Le nettoyage des données est souvent la partie la plus chronophage de l'analyse de données. Les données du monde réel sont désordonnées et nécessitent un préprocessing avant l'analyse.

Problèmes de qualité des données courants:
- Valeurs manquantes (NaN, null)
- Enregistrements dupliqués
- Formatage incohérent
- Valeurs aberrantes et erreurs
- Types de données incorrects""",
            order=2
        )
        
        # Section 2 questions
        self.create_question(
            section2, "Which method removes rows with missing values?",
            "Quelle méthode supprime les lignes avec des valeurs manquantes?",
            "dropna()", "____na()", 1
        )
        
        self.create_question(
            section2, "What function converts a column to datetime format?",
            "Quelle fonction convertit une colonne au format datetime?",
            "pd.to_datetime()", "pd.to________()", 2
        )
        
        # Section 3: Data Transformation
        section3 = self.create_section(
            room, "Data Transformation", "Transformation des Données",
            """Data transformation involves restructuring and modifying data to make it suitable for analysis.

Common transformations:
- Filtering and selecting data
- Grouping and aggregation
- Merging and joining datasets
- Reshaping data (pivot, melt)
- Creating new columns

Filtering and selection:
```python
# Filter rows
young_people = df[df['Age'] < 30]
high_salary = df[df['Salary'] > 50000]

# Multiple conditions
filtered = df[(df['Age'] > 25) & (df['City'] == 'New York')]

# Select specific columns
subset = df[['Name', 'Age', 'Salary']]
```

Grouping and aggregation:
```python
# Group by category
grouped = df.groupby('Department')

# Aggregation functions
result = grouped.agg({
    'Salary': ['mean', 'max', 'min'],
    'Age': 'mean',
    'Employee_ID': 'count'
})

# Simple groupby operations
avg_salary_by_dept = df.groupby('Department')['Salary'].mean()
```

Creating new columns:
```python
# Simple calculations
df['Age_Category'] = df['Age'].apply(lambda x: 'Young' if x < 30 else 'Senior')
df['Salary_Per_Year'] = df['Monthly_Salary'] * 12

# Conditional logic
df['Performance'] = np.where(df['Score'] >= 80, 'High', 'Low')
```""",
            """La transformation des données implique la restructuration et la modification des données pour les rendre adaptées à l'analyse.

Transformations courantes:
- Filtrage et sélection de données
- Regroupement et agrégation
- Fusion et jointure de jeux de données
- Remaniement des données (pivot, melt)
- Création de nouvelles colonnes""",
            order=3
        )
        
        # Section 3 questions
        self.create_question(
            section3, "Which method is used to group data by a specific column?",
            "Quelle méthode est utilisée pour regrouper les données par une colonne spécifique?",
            "groupby()", "______by()", 1
        )
        
        self.create_question(
            section3, "What operator is used for logical AND in pandas filtering?",
            "Quel opérateur est utilisé pour le ET logique dans le filtrage pandas?",
            "&", "_", 2
        )
        
        # Final exam questions
        self.create_final_question(
            room, "Write pandas code to read a CSV file named 'data.csv'",
            "Écrivez le code pandas pour lire un fichier CSV nommé 'data.csv'",
            "pd.read_csv('data.csv')", "pd.______('data.csv')", 1
        )
        
        self.create_final_question(
            room, "Which method fills missing values with a specified value?",
            "Quelle méthode remplit les valeurs manquantes avec une valeur spécifiée?",
            "fillna()", "____na()", 2
        )
        
        self.create_final_question(
            room, "What function calculates the mean of a numeric column?",
            "Quelle fonction calcule la moyenne d'une colonne numérique?",
            "mean()", "______()", 3
        )
    
    def create_stats_content(self, room):
        """Create content for Statistics and Probability room."""
        
        # Section 1: Descriptive Statistics
        section1 = self.create_section(
            room, "Descriptive Statistics", "Statistiques Descriptives",
            """Descriptive statistics summarize and describe the features of a dataset. They provide simple summaries about the sample and measures.

Key measures of central tendency:
- **Mean**: Average value (sum of all values / number of values)
- **Median**: Middle value when data is sorted
- **Mode**: Most frequently occurring value

Measures of variability:
- **Range**: Difference between max and min values
- **Variance**: Average of squared differences from mean
- **Standard Deviation**: Square root of variance
- **Interquartile Range (IQR)**: Difference between 75th and 25th percentiles

Python implementation:
```python
import numpy as np
import pandas as pd
from scipy import stats

data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Central tendency
mean = np.mean(data)
median = np.median(data)
mode = stats.mode(data)

# Variability
variance = np.var(data)
std_dev = np.std(data)
range_val = np.max(data) - np.min(data)

# Using pandas
df = pd.DataFrame({'values': data})
print(df.describe())  # Complete statistical summary
```

Understanding distributions:
- Normal distribution (bell curve)
- Skewed distributions
- Outlier detection using IQR method""",
            """Les statistiques descriptives résument et décrivent les caractéristiques d'un jeu de données. Elles fournissent des résumés simples sur l'échantillon et les mesures.

Mesures clés de tendance centrale:
- **Moyenne**: Valeur moyenne (somme de toutes les valeurs / nombre de valeurs)
- **Médiane**: Valeur du milieu quand les données sont triées
- **Mode**: Valeur qui apparaît le plus fréquemment""",
            order=1
        )
        
        # Section 1 questions
        self.create_question(
            section1, "What is the middle value in a sorted dataset called?",
            "Comment appelle-t-on la valeur du milieu dans un jeu de données trié?",
            "median", "______", 1
        )
        
        self.create_question(
            section1, "Which function calculates the standard deviation in NumPy?",
            "Quelle fonction calcule l'écart-type dans NumPy?",
            "np.std()", "np._____()", 2
        )
        
        # Section 2: Probability Theory
        section2 = self.create_section(
            room, "Probability Theory", "Théorie des Probabilités",
            """Probability theory is the mathematical framework for quantifying uncertainty and randomness in data science.

Basic probability concepts:
- **Event**: A specific outcome or set of outcomes
- **Sample Space**: All possible outcomes
- **Probability**: Likelihood of an event (0 to 1)
- **Independence**: Events that don't affect each other
- **Conditional Probability**: P(A|B) - probability of A given B

Probability rules:
```python
# Basic probability calculations
total_outcomes = 100
favorable_outcomes = 25
probability = favorable_outcomes / total_outcomes

# Addition rule: P(A or B) = P(A) + P(B) - P(A and B)
# Multiplication rule: P(A and B) = P(A) × P(B) for independent events
```

Common probability distributions:
- **Binomial**: Success/failure trials
- **Normal**: Bell-shaped, continuous
- **Poisson**: Rare events over time
- **Uniform**: All outcomes equally likely

Using scipy.stats:
```python
from scipy import stats

# Normal distribution
normal_dist = stats.norm(loc=0, scale=1)  # mean=0, std=1
probability = normal_dist.cdf(1.96)  # P(X <= 1.96)

# Binomial distribution
binomial_dist = stats.binom(n=10, p=0.3)
prob_success = binomial_dist.pmf(3)  # P(X = 3 successes)
```

Applications in data science:
- Hypothesis testing
- Confidence intervals
- A/B testing
- Risk assessment""",
            """La théorie des probabilités est le cadre mathématique pour quantifier l'incertitude et le caractère aléatoire en science des données.

Concepts de base de probabilité:
- **Événement**: Un résultat spécifique ou un ensemble de résultats
- **Espace d'échantillonnage**: Tous les résultats possibles
- **Probabilité**: Probabilité d'un événement (0 à 1)
- **Indépendance**: Événements qui ne s'affectent pas mutuellement""",
            order=2
        )
        
        # Section 2 questions
        self.create_question(
            section2, "What is the range of probability values?",
            "Quelle est la plage des valeurs de probabilité?",
            "0 to 1", "_ to _", 1
        )
        
        self.create_question(
            section2, "Which distribution is bell-shaped and continuous?",
            "Quelle distribution a la forme d'une cloche et est continue?",
            "normal", "______", 2
        )
        
        # Section 3: Hypothesis Testing
        section3 = self.create_section(
            room, "Hypothesis Testing", "Test d'Hypothèses",
            """Hypothesis testing is a statistical method for making decisions about population parameters based on sample data.

Key concepts:
- **Null Hypothesis (H₀)**: Default assumption (no effect/difference)
- **Alternative Hypothesis (H₁)**: What we want to prove
- **Significance Level (α)**: Threshold for rejecting H₀ (usually 0.05)
- **P-value**: Probability of observing data given H₀ is true
- **Test Statistic**: Calculated value used for decision

Common hypothesis tests:
1. **One-sample t-test**: Compare sample mean to known value
2. **Two-sample t-test**: Compare means of two groups
3. **Chi-square test**: Test independence of categorical variables
4. **ANOVA**: Compare means of multiple groups

Python implementation:
```python
from scipy import stats
import numpy as np

# One-sample t-test
sample_data = [2.3, 1.9, 2.1, 2.5, 2.0, 2.2, 2.4]
population_mean = 2.0

t_statistic, p_value = stats.ttest_1samp(sample_data, population_mean)

# Decision making
alpha = 0.05
if p_value < alpha:
    print("Reject null hypothesis")
else:
    print("Fail to reject null hypothesis")

# Two-sample t-test
group1 = [1.2, 1.4, 1.1, 1.3, 1.5]
group2 = [1.8, 1.9, 1.7, 2.0, 1.6]

t_stat, p_val = stats.ttest_ind(group1, group2)
```

Interpretation:
- p < α: Reject H₀ (statistically significant result)
- p ≥ α: Fail to reject H₀ (insufficient evidence)
- Effect size matters beyond statistical significance""",
            """Le test d'hypothèses est une méthode statistique pour prendre des décisions sur les paramètres de population basées sur des données d'échantillon.

Concepts clés:
- **Hypothèse nulle (H₀)**: Supposition par défaut (pas d'effet/différence)
- **Hypothèse alternative (H₁)**: Ce que nous voulons prouver
- **Niveau de signification (α)**: Seuil pour rejeter H₀ (généralement 0,05)""",
            order=3
        )
        
        # Section 3 questions
        self.create_question(
            section3, "What is the typical significance level (alpha) used in hypothesis testing?",
            "Quel est le niveau de signification (alpha) typique utilisé dans les tests d'hypothèses?",
            "0.05", "0.__", 1
        )
        
        self.create_question(
            section3, "Which test compares the means of two independent groups?",
            "Quel test compare les moyennes de deux groupes indépendants?",
            "two-sample t-test", "two-sample _-test", 2
        )
        
        # Final exam questions
        self.create_final_question(
            room, "What measure indicates the spread of data around the mean?",
            "Quelle mesure indique la dispersion des données autour de la moyenne?",
            "standard deviation", "standard _________", 1
        )
        
        self.create_final_question(
            room, "In hypothesis testing, what does a p-value less than alpha indicate?",
            "Dans les tests d'hypothèses, qu'indique une p-value inférieure à alpha?",
            "reject null hypothesis", "reject ____ hypothesis", 2
        )
        
        self.create_final_question(
            room, "Which Python library is commonly used for statistical tests?",
            "Quelle bibliothèque Python est couramment utilisée pour les tests statistiques?",
            "scipy.stats", "_____.stats", 3
        )
    
    def create_viz_content(self, room):
        """Create content for Data Visualization room."""
        
        # Section 1: Matplotlib Basics
        section1 = self.create_section(
            room, "Matplotlib Basics", "Bases de Matplotlib",
            """Matplotlib is the foundational plotting library in Python, providing a MATLAB-like interface for creating static visualizations.

Basic plotting concepts:
- **Figure**: The entire window or page
- **Axes**: The actual plot area with data
- **Artists**: Everything visible (lines, text, ticks)

Creating basic plots:
```python
import matplotlib.pyplot as plt
import numpy as np

# Line plot
x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(10, 6))
plt.plot(x, y, label='sin(x)', color='blue', linewidth=2)
plt.xlabel('X values')
plt.ylabel('Y values')
plt.title('Sine Wave')
plt.legend()
plt.grid(True)
plt.show()

# Scatter plot
x = np.random.randn(100)
y = np.random.randn(100)

plt.figure(figsize=(8, 6))
plt.scatter(x, y, alpha=0.6, c='red', s=50)
plt.xlabel('X values')
plt.ylabel('Y values')
plt.title('Random Scatter Plot')
plt.show()
```

Common plot types:
- Line plots: Trends over time
- Scatter plots: Relationships between variables
- Bar plots: Categorical comparisons
- Histograms: Distribution of values
- Box plots: Statistical summaries

Customization options:
- Colors, markers, line styles
- Labels, titles, legends
- Grid, axis limits
- Multiple subplots""",
            """Matplotlib est la bibliothèque de traçage fondamentale en Python, fournissant une interface similaire à MATLAB pour créer des visualisations statiques.

Concepts de base du tracé:
- **Figure**: La fenêtre ou page entière
- **Axes**: La zone de tracé réelle avec les données
- **Artists**: Tout ce qui est visible (lignes, texte, graduations)""",
            order=1
        )
        
        # Section 1 questions
        self.create_question(
            section1, "Which function creates a line plot in matplotlib?",
            "Quelle fonction crée un graphique linéaire dans matplotlib?",
            "plt.plot()", "plt._____()", 1
        )
        
        self.create_question(
            section1, "What does the 'figsize' parameter control?",
            "Que contrôle le paramètre 'figsize'?",
            "figure dimensions", "figure __________", 2
        )
        
        # Section 2: Seaborn for Statistical Plots
        section2 = self.create_section(
            room, "Seaborn for Statistical Plots", "Seaborn pour les Graphiques Statistiques",
            """Seaborn is built on top of matplotlib and provides a high-level interface for creating attractive statistical visualizations.

Key advantages of seaborn:
- Beautiful default styles
- Built-in statistical functions
- Easy handling of DataFrames
- Complex plots with simple syntax

Essential seaborn plots:
```python
import seaborn as sns
import pandas as pd

# Set style
sns.set_style("whitegrid")

# Distribution plots
sns.histplot(data=df, x='age', bins=20)
sns.boxplot(data=df, x='category', y='value')
sns.violinplot(data=df, x='group', y='score')

# Relationship plots
sns.scatterplot(data=df, x='height', y='weight', hue='gender')
sns.lineplot(data=df, x='year', y='sales', hue='product')

# Categorical plots
sns.barplot(data=df, x='category', y='average_score')
sns.countplot(data=df, x='status')

# Matrix plots
correlation_matrix = df.corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')

# Pair plots
sns.pairplot(df, hue='species')
```

Advanced features:
- Faceting (FacetGrid)
- Statistical estimation
- Color palettes
- Themes and contexts

Best practices:
- Choose appropriate plot types
- Use color effectively
- Avoid chart junk
- Make titles and labels clear""",
            """Seaborn est construit sur matplotlib et fournit une interface de haut niveau pour créer des visualisations statistiques attrayantes.

Avantages clés de seaborn:
- Styles par défaut beaux
- Fonctions statistiques intégrées
- Gestion facile des DataFrames
- Graphiques complexes avec syntaxe simple""",
            order=2
        )
        
        # Section 2 questions
        self.create_question(
            section2, "Which seaborn function creates a correlation heatmap?",
            "Quelle fonction seaborn crée une carte de chaleur de corrélation?",
            "sns.heatmap()", "sns._______()", 1
        )
        
        self.create_question(
            section2, "What parameter in seaborn plots is used to separate data by categories using color?",
            "Quel paramètre dans les graphiques seaborn est utilisé pour séparer les données par catégories en utilisant la couleur?",
            "hue", "___", 2
        )
        
        # Section 3: Interactive Visualizations
        section3 = self.create_section(
            room, "Interactive Visualizations", "Visualisations Interactives",
            """Interactive visualizations allow users to explore data dynamically through hover effects, zooming, filtering, and other interactions.

Popular libraries for interactive plots:
- **Plotly**: Web-based interactive visualizations
- **Bokeh**: Interactive visualization library
- **Altair**: Declarative visualization based on Vega-Lite

Plotly basics:
```python
import plotly.express as px
import plotly.graph_objects as go

# Interactive scatter plot
fig = px.scatter(df, x='gdp_per_capita', y='life_expectancy', 
                 size='population', color='continent',
                 hover_name='country',
                 title='GDP vs Life Expectancy')
fig.show()

# Interactive line plot
fig = px.line(df, x='year', y='sales', color='product',
              title='Sales Over Time')
fig.update_layout(hovermode='x unified')
fig.show()

# 3D scatter plot
fig = px.scatter_3d(df, x='x', y='y', z='z', color='category')
fig.show()

# Dashboard with subplots
from plotly.subplots import make_subplots

fig = make_subplots(rows=2, cols=2,
                    subplot_titles=['Plot 1', 'Plot 2', 'Plot 3', 'Plot 4'])

fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6]), row=1, col=1)
fig.add_trace(go.Bar(x=['A', 'B', 'C'], y=[1, 3, 2]), row=1, col=2)
```

Interactive features:
- Hover tooltips with detailed information
- Zoom and pan capabilities
- Click events and selections
- Animations and transitions
- Responsive layouts

Use cases:
- Exploratory data analysis
- Dashboards and reports
- Web applications
- Presentations""",
            """Les visualisations interactives permettent aux utilisateurs d'explorer les données dynamiquement grâce aux effets de survol, au zoom, au filtrage et à d'autres interactions.

Bibliothèques populaires pour les graphiques interactifs:
- **Plotly**: Visualisations interactives basées sur le web
- **Bokeh**: Bibliothèque de visualisation interactive
- **Altair**: Visualisation déclarative basée sur Vega-Lite""",
            order=3
        )
        
        # Section 3 questions
        self.create_question(
            section3, "Which library is commonly used for web-based interactive visualizations?",
            "Quelle bibliothèque est couramment utilisée pour les visualisations interactives basées sur le web?",
            "Plotly", "______", 1
        )
        
        self.create_question(
            section3, "What Plotly feature allows users to see detailed information when hovering over data points?",
            "Quelle fonctionnalité Plotly permet aux utilisateurs de voir des informations détaillées en survolant les points de données?",
            "hover tooltips", "hover ________", 2
        )
        
        # Final exam questions
        self.create_final_question(
            room, "Which matplotlib function creates a scatter plot?",
            "Quelle fonction matplotlib crée un nuage de points?",
            "plt.scatter()", "plt._______()", 1
        )
        
        self.create_final_question(
            room, "What seaborn function creates a pair plot showing relationships between all numerical variables?",
            "Quelle fonction seaborn crée un graphique de paires montrant les relations entre toutes les variables numériques?",
            "sns.pairplot()", "sns._______()", 2
        )
        
        self.create_final_question(
            room, "Which parameter in plotly plots controls the size of markers based on a variable?",
            "Quel paramètre dans les graphiques plotly contrôle la taille des marqueurs basée sur une variable?",
            "size", "____", 3
        )
    
    def create_ml_content(self, room):
        """Create content for Machine Learning Basics room."""
        
        # Section 1: Introduction to Machine Learning
        section1 = self.create_section(
            room, "Introduction to Machine Learning", "Introduction à l'Apprentissage Automatique",
            """Machine Learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed.

Types of machine learning:
1. **Supervised Learning**: Learning with labeled examples
   - Classification: Predicting categories (email spam/not spam)
   - Regression: Predicting continuous values (house prices)

2. **Unsupervised Learning**: Finding patterns in unlabeled data
   - Clustering: Grouping similar data points
   - Dimensionality reduction: Simplifying data

3. **Reinforcement Learning**: Learning through rewards and penalties

Machine learning workflow:
1. **Problem Definition**: What are we trying to predict?
2. **Data Collection**: Gathering relevant data
3. **Data Preprocessing**: Cleaning and preparing data
4. **Feature Engineering**: Creating useful input variables
5. **Model Selection**: Choosing appropriate algorithms
6. **Training**: Teaching the model with data
7. **Evaluation**: Measuring model performance
8. **Deployment**: Putting the model into production

Key concepts:
- **Features**: Input variables (X)
- **Target**: What we're predicting (y)
- **Training set**: Data used to train the model
- **Test set**: Data used to evaluate the model
- **Overfitting**: Model memorizes training data but fails on new data
- **Underfitting**: Model is too simple to capture patterns

Python libraries for ML:
- **Scikit-learn**: General-purpose ML library
- **TensorFlow**: Deep learning framework
- **PyTorch**: Research-oriented deep learning
- **XGBoost**: Gradient boosting algorithms""",
            """L'apprentissage automatique est un sous-ensemble de l'intelligence artificielle qui permet aux ordinateurs d'apprendre et de prendre des décisions à partir de données sans être explicitement programmés.

Types d'apprentissage automatique:
1. **Apprentissage supervisé**: Apprentissage avec des exemples étiquetés
2. **Apprentissage non supervisé**: Trouver des motifs dans des données non étiquetées
3. **Apprentissage par renforcement**: Apprentissage par récompenses et pénalités""",
            order=1
        )
        
        # Section 1 questions
        self.create_question(
            section1, "Which type of machine learning uses labeled data for training?",
            "Quel type d'apprentissage automatique utilise des données étiquetées pour l'entraînement?",
            "supervised learning", "________ learning", 1
        )
        
        self.create_question(
            section1, "What is the term for input variables in machine learning?",
            "Quel est le terme pour les variables d'entrée dans l'apprentissage automatique?",
            "features", "________", 2
        )
        
        # Section 2: Classification Algorithms
        section2 = self.create_section(
            room, "Classification Algorithms", "Algorithmes de Classification",
            """Classification algorithms predict categorical outcomes. They assign input data to predefined categories or classes.

Common classification algorithms:
1. **Logistic Regression**: Linear model for binary/multiclass classification
2. **Decision Trees**: Tree-like model making decisions based on features
3. **Random Forest**: Ensemble of decision trees
4. **Support Vector Machines (SVM)**: Finds optimal decision boundary
5. **K-Nearest Neighbors (KNN)**: Classifies based on nearest neighbors
6. **Naive Bayes**: Probabilistic classifier based on Bayes' theorem

Implementing classification with scikit-learn:
```python
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd

# Load and prepare data
df = pd.read_csv('dataset.csv')
X = df[['feature1', 'feature2', 'feature3']]  # Features
y = df['target']  # Target variable

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

# Train logistic regression
log_reg = LogisticRegression()
log_reg.fit(X_train, y_train)

# Make predictions
y_pred = log_reg.predict(X_test)

# Evaluate model
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy}")
print(classification_report(y_test, y_pred))

# Train random forest
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)
```

Evaluation metrics:
- **Accuracy**: Percentage of correct predictions
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **F1-score**: Harmonic mean of precision and recall
- **Confusion Matrix**: Detailed breakdown of predictions""",
            """Les algorithmes de classification prédisent des résultats catégoriels. Ils assignent des données d'entrée à des catégories ou classes prédéfinies.

Algorithmes de classification courants:
1. **Régression logistique**: Modèle linéaire pour classification binaire/multiclasse
2. **Arbres de décision**: Modèle arborescent prenant des décisions basées sur les caractéristiques
3. **Forêt aléatoire**: Ensemble d'arbres de décision""",
            order=2
        )
        
        # Section 2 questions
        self.create_question(
            section2, "Which algorithm combines multiple decision trees to improve accuracy?",
            "Quel algorithme combine plusieurs arbres de décision pour améliorer la précision?",
            "Random Forest", "Random ______", 1
        )
        
        self.create_question(
            section2, "What metric measures the percentage of correct predictions?",
            "Quelle métrique mesure le pourcentage de prédictions correctes?",
            "accuracy", "_______", 2
        )
        
        # Section 3: Regression and Model Evaluation
        section3 = self.create_section(
            room, "Regression and Model Evaluation", "Régression et Évaluation de Modèle",
            """Regression algorithms predict continuous numerical values. They model the relationship between input features and a continuous target variable.

Common regression algorithms:
1. **Linear Regression**: Models linear relationship between features and target
2. **Polynomial Regression**: Captures non-linear relationships
3. **Ridge Regression**: Linear regression with L2 regularization
4. **Lasso Regression**: Linear regression with L1 regularization
5. **Decision Tree Regression**: Tree-based regression
6. **Random Forest Regression**: Ensemble of regression trees

Implementing regression:
```python
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import numpy as np

# Linear regression
linear_reg = LinearRegression()
linear_reg.fit(X_train, y_train)
y_pred_linear = linear_reg.predict(X_test)

# Ridge regression (with regularization)
ridge_reg = Ridge(alpha=1.0)
ridge_reg.fit(X_train, y_train)
y_pred_ridge = ridge_reg.predict(X_test)

# Random forest regression
rf_reg = RandomForestRegressor(n_estimators=100, random_state=42)
rf_reg.fit(X_train, y_train)
y_pred_rf = rf_reg.predict(X_test)

# Evaluation metrics
mse = mean_squared_error(y_test, y_pred_linear)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_test, y_pred_linear)
r2 = r2_score(y_test, y_pred_linear)

print(f"MSE: {mse}")
print(f"RMSE: {rmse}")
print(f"MAE: {mae}")
print(f"R²: {r2}")
```

Cross-validation for robust evaluation:
```python
from sklearn.model_selection import cross_val_score, KFold

# K-fold cross-validation
kfold = KFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(linear_reg, X, y, cv=kfold, scoring='r2')

print(f"CV R² scores: {cv_scores}")
print(f"Mean CV R²: {cv_scores.mean()}")
print(f"Std CV R²: {cv_scores.std()}")
```

Model evaluation best practices:
- Use train/validation/test splits
- Apply cross-validation
- Check for overfitting/underfitting
- Compare multiple models
- Consider feature importance""",
            """Les algorithmes de régression prédisent des valeurs numériques continues. Ils modélisent la relation entre les caractéristiques d'entrée et une variable cible continue.

Algorithmes de régression courants:
1. **Régression linéaire**: Modélise une relation linéaire entre caractéristiques et cible
2. **Régression polynomiale**: Capture les relations non-linéaires
3. **Régression Ridge**: Régression linéaire avec régularisation L2""",
            order=3
        )
        
        # Section 3 questions
        self.create_question(
            section3, "Which metric measures the square root of the average squared differences between predicted and actual values?",
            "Quelle métrique mesure la racine carrée des différences quadratiques moyennes entre les valeurs prédites et réelles?",
            "RMSE", "____", 1
        )
        
        self.create_question(
            section3, "What validation technique splits data into k subsets for robust model evaluation?",
            "Quelle technique de validation divise les données en k sous-ensembles pour une évaluation robuste du modèle?",
            "k-fold cross-validation", "k-fold cross-__________", 2
        )
        
        # Final exam questions
        self.create_final_question(
            room, "Which scikit-learn function splits data into training and testing sets?",
            "Quelle fonction scikit-learn divise les données en ensembles d'entraînement et de test?",
            "train_test_split", "train_test_____", 1
        )
        
        self.create_final_question(
            room, "What type of machine learning algorithm is Random Forest?",
            "Quel type d'algorithme d'apprentissage automatique est Random Forest?",
            "ensemble", "________", 2
        )
        
        self.create_final_question(
            room, "Which regression metric indicates the proportion of variance in the target variable explained by the model?",
            "Quelle métrique de régression indique la proportion de variance dans la variable cible expliquée par le modèle?",
            "R-squared", "R-_______", 3
        )
