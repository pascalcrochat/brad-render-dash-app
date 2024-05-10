# -*- coding: utf-8 -*-
import sys
from dash import Dash, html, dcc, Input, Output, State
from embedchain import App
from translate import Translator
from langdetect import detect
from flask import Flask, request
from dotenv import load_dotenv
import os
import random
# pip install -r requirements.txt

# Créer une instance du bot
load_dotenv()
ai_bot = App.from_config(config_path="config.yaml")

# Initialiser le serveur Flask
server = Flask(__name__)

# Initialiser l'application Dash
app = Dash(__name__, server=server, suppress_callback_exceptions=True)

server = app.server

# Liste pour stocker les noms de fichiers
txt_files = []

# Fonction pour mettre à jour le bot avec de nouveaux fichiers texte


def add_txt_files():
    """Ajoute les fichiers texte à l'instance du bot."""
    for file in txt_files:
        ai_bot.add(file)


# Fonction pour rechercher les fichiers texte à la racine du programme et les ajouter à la liste
def load_txt_files():
    """Charge les fichiers texte à la racine du programme."""
    for file in os.listdir(os.getcwd()):
        if file.endswith(".txt"):
            txt_files.append(os.path.join(os.getcwd(), file))


load_txt_files()  # Chargement initial des fichiers texte

add_txt_files()  # Mise à jour initiale du bot avec les fichiers texte

# Définir la mise en page de l'application

# Liste de noms aléatoires
noms = [
    'Jean', 'Marie', 'Claire', 'Pierre', 'Sophie', 'Muhammad', 'Olivia', 'William', 'Emma', 'Noah',
    'Ava', 'James', 'Isabella', 'Liam', 'Sophia', 'Michael', 'Mia', 'Alexander', 'Charlotte', 'Benjamin',
    'Amelia', 'Elijah', 'Harper', 'Daniel', 'Evelyn', 'Matthew', 'Abigail', 'Jackson', 'Emily', 'David',
    'Elizabeth', 'Joseph', 'Sofia', 'Lucas', 'Ella', 'Logan', 'Madison', 'John', 'Avery', 'Ryan', 'Scarlett',
    'Caleb', 'Grace', 'Henry', 'Chloe', 'Sebastian', 'Victoria', 'Gabriel', 'Riley', 'Owen', 'Aria', 'Carter',
    'Lily', 'Jayden', 'Samantha', 'Dylan', 'Zoe', 'Luke', 'Audrey', 'Anthony', 'Layla', 'Isaac', 'Penelope',
    'Isaiah', 'Nora', 'Josiah', 'Addison', 'Christian', 'Hannah', 'Hunter', 'Aurora', 'Connor', 'Leah',
    'Eli', 'Bella', 'Levi', 'Natalie', 'Jonathan', 'Skylar', 'Aaron', 'Brooklyn', 'Nathan', 'Claire',
    'Charles', 'Lillian', 'Thomas', 'Ellie', 'Joshua', 'Savannah', 'Brayden', 'Kylie', 'Cameron', 'Aubrey',
    'Jack', 'Stella', 'Jordan', 'Maya', 'Nicholas', 'Kimberly', 'Theodore', 'Elliana'
]

# Choisir un nom aléatoire
prenom_aleatoire = random.choice(noms)

# Mise en page de l'application
app.layout = html.Div([
    html.Div([
        html.Img(src='assets/logoPeephole.png',
                 style={'width': '90px', 'margin-bottom': '10px'}),
        html.H1('LePeepHole-Chatbot',
                style={'color': '#f5d10b', 'text-align': 'center', 'margin-bottom': '0'}),
        html.H3(f"Bonjour, je suis {prenom_aleatoire}! Comment puis-je vous aider aujourd'hui?",
                style={'color': '#f5d10b', 'text-align': 'center'}),
        html.Br(),

        # Div pour afficher la conversation avec une barre de défilement
        html.Div(id='conversation-area',
                 style={'width': '50%', 'margin-bottom': '0', 'display': 'block', 'padding': '10px',
                        'background-color': 'white', 'border-radius': '5px', 'height': '300px',
                        'overflow-y': 'auto'}),

        # Zone de saisie de la question
        dcc.Textarea(id='question-area',
                     placeholder='Poser votre question...',
                     style={'width': '50%', 'margin-top': '10px', 'display': 'block', 'padding': '10px',
                            'border': '1px solid #ccc', 'border-radius': '5px'}),

        # Bouton de soumission
        html.Button(id='submit-btn', children='Soumettre la question',
                    style={'background-color': '#f5d10b', 'color': 'black', 'border': 'none', 'margin-top': '10px', 'display': 'block', 'padding': '6px 50px',
                           'border-radius': '5px', 'cursor': 'pointer'}),

        # Formulaire pour enregistrer du texte dans un fichier .txt
        html.Div([
            html.H1('Enregistrer du texte dans un fichier',
                    style={'color': 'white'}),
            html.Label('Nom du fichier:', style={'color': 'white'}),
            dcc.Input(id='filename', type='text', style={'display': 'block'}),
            html.Br(),
            html.Label('Contenu du fichier:', style={'color': 'white'}),
            dcc.Textarea(id='content', rows='4', cols='50',
                         style={'display': 'block'}),
            html.Br(),
            html.Button('Enregistrer', id='save-btn',
                        style={'display': 'block'}),
            html.Div(id='output-message',
                     style={'color': 'white', 'margin-top': '10px'})
        ]),

        # Liste des fichiers texte ajoutés
        html.Div([
            html.H1('Fichiers texte ajoutés', style={'color': 'white'}),
            html.Ul(id='txt-files-list', style={'color': 'white'})
        ])

    ], style={'display': 'flex', 'flex-direction': 'column', 'justify-content': 'flex-start',
              'align-items': 'center', 'margin-top': '3%', 'background-color': '#333333'}),

], style={'font-family': 'Arial, Helvetica, sans-serif', 'margin': '0', 'padding': '0',
          'height': '500vh', 'overflow': 'hidden', 'box-sizing': 'border-box', 'background-color': '#333333'})


# Callback pour créer une réponse à partir de la question
@app.callback(
    Output('conversation-area', 'children'),
    [Input('submit-btn', 'n_clicks')],
    [State('question-area', 'value'), State('conversation-area', 'children')],
    prevent_initial_call=True
)
def create_response(n_clicks, question, conversation):
    """Crée une réponse à partir de la question de l'utilisateur."""
    
    # Détecter la langue de la question de l'utilisateur
    detected_language = detect(question)

    # Créer une instance du traducteur en fonction de la langue détectée
    translator = Translator(
        to_lang='fr') if detected_language != 'fr' else Translator(to_lang='en')

    # Obtenir la réponse du bot en utilisant la langue de la question
    answer = ai_bot.query(question)

    # Traduire la réponse dans la langue de la question si nécessaire
    if detected_language != 'fr':
        answer = translator.translate(answer)

    # Ajouter la nouvelle question et réponse en haut de la conversation
    conversation_update = html.Div([
        html.P([html.Strong("Question: "), f"{question}"], style={
               'margin-bottom': '13px', 'margin-top': '13px'}),
        html.P([html.Strong("Réponse: "), f"{answer}"], style={
               'margin-top': '0', 'margin-bottom': '0', 'line-height': '1.5'}),
        html.Div(conversation)
    ])

    return conversation_update


# Callback pour enregistrer du texte dans un fichier .txt
@app.callback(
    [Output('output-message', 'children'),
     Output('filename', 'value'),
     Output('content', 'value')],
    [Input('save-btn', 'n_clicks')],
    [State('filename', 'value'), State('content', 'value')],
    prevent_initial_call=True
)
def save_text_to_file(n_clicks, filename, content):
    """Enregistre du texte dans un fichier .txt."""
    
    if filename and content:
        try:
            # Chemin complet du fichier à enregistrer
            file_path = os.path.join(os.getcwd(), filename + ".txt")
            txt_files.append(file_path)
            add_txt_files()  # Mettre à jour le bot avec les nouveaux fichiers texte

            # Enregistrer le texte dans le fichier avec l'encodage UTF-8
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

            # Réinitialiser les valeurs des champs de nom de fichier et de contenu
            return 'Fichier enregistré avec succès !', '', ''
        except Exception as e:
            return f"Erreur lors de l'enregistrement du fichier : {str(e)}", filename, content
    else:
        return 'Nom de fichier ou contenu manquant.', filename, content


# Liste pour stocker les noms uniques de fichiers
unique_file_names = set()

# Callback pour mettre à jour la liste des fichiers texte dans le navigateur


# Liste pour stocker les noms uniques de fichiers
unique_file_names = set()

# Ajouter les noms de fichiers déjà présents dans le répertoire au démarrage du serveur
for file in os.listdir(os.getcwd()):
    if file.endswith('.txt'):
        unique_file_names.add(os.path.splitext(file)[0])

# Callback pour mettre à jour la liste des fichiers texte dans le navigateur


@app.callback(
    Output('txt-files-list', 'children'),
    [Input('save-btn', 'n_clicks')],
    [State('filename', 'value')],
    prevent_initial_call=True
)
def update_txt_files_list(n_clicks, filename):
    if filename:
        txt_files.append(filename)  # Ajouter le nom de fichier à la liste
        unique_file_names.add(os.path.splitext(os.path.basename(filename))[
                              0])  # Ajouter le nom unique sans extension
        # Obtenir la liste des noms uniques
        files_list = [html.Li(file_name) for file_name in unique_file_names]
        # Afficher la liste dans un élément <ul>
        return html.Ul(files_list, style={'color': 'white'})
    else:
        return []

if __name__ == '__main__':
    app.run_server(debug=True)

# LePeepHole-Chatbot

# LePeepHole-Chatbot est une application web construite avec Dash qui utilise un modèle de chatbot pour répondre aux questions des utilisateurs. Les utilisateurs peuvent poser des questions dans la zone de texte prévue à cet effet, et le chatbot fournira des réponses en fonction de son modèle de langage.
# Le principe est simple quand l utilisateur entre des informations sous forme de texte celle-ci sont converties en vecteurs dans une base de donnees

            #===========OPENAI===========
# Questions                                Reponses 
            #==========VECTEURS==========

# Fonctionnalités

# - Chatbot intégré pour répondre aux questions des utilisateurs.
# - Possibilité d'enregistrer du texte dans des fichiers .txt.
# - Interface utilisateur conviviale avec des fonctionnalités de navigation simples.
# - LLM OpenAi https://platform.openai.com/docs/models/embeddings
# - Pour changer de configuration d API ou de LLM aller dans config.yaml

# Bibliothèques utilisées

# - Dash: Framework web pour construire des applications analytiques.
# - Flask: Framework web pour Python.
# - Embedchain: Bibliothèque pour la gestion des chatbots. https://docs.embedchain.ai/api-reference/advanced/configuration
# - Translate: Bibliothèque pour la traduction de texte.
# - Langdetect: Bibliothèque pour la détection automatique de la langue.
# - Dotenv: Bibliothèque pour charger les variables d'environnement à partir d'un fichier .env.
# - OS: Module pour effectuer des opérations sur le système d'exploitation.
# -> pip install -r requirements.txt <-commande pour charger les bibliothèques dans le terminal.

# Comment exécuter l'application

# Pour exécuter l'application, assurez-vous d'avoir installé toutes les bibliothèques nécessaires répertoriées dans le fichier requirements.txt. Ensuite, exécutez le fichier main.py à l'aide de Python.

# Assurez-vous également d'avoir un environnement .env correctement configuré avec les variables nécessaires pour sécuriser la clé d'API. Exemple -> OPENAI_API_KEY = xxxxxxxxxxxxxxxxxxxxxxxxx

# python 3.11.0 64-bit