
# Créez une API sécurisée RESTful en utilisant Django REST Framework (Projet No.10)

Dans ce projet, l'objectif est de se consacrer à la création de la partie backend d'un site web, à travers l'élaboration d'une API sécurisée qu'il nous est demandé de concevoir par le biais de l'utilisation de l'application Python Django Rest Framework. Pour se faire, les premières étapes d'installation de l'application en question se déroulent, pour ensuite laisser place aux étapes de configuration dans un second temps, afin que l'on puisse aboutir à la mise en place pour terminer. Ci-dessous les étapes permettant d'accéder à cette mise en place.

#### Première étape : téléchargement
Télécharger le répertoire Github à partir le lien ci-dessous :
https://github.com/o0nekov0o/OpenClassrooms_P10/archive/refs/heads/master.zip

#### Deuxième étape : installation
A l'aide de votre invite de commandes, placez-vous à la racine du répertoire téléchargé.
Lancez-y ensuite la commande suivante afin de créer votre environnement virtuel :
```bash
  python -m venv env
```
Depuis Windows, exécutez la commande suivante pour activer votre environnement virtuel :
```bash
  call env/Scripts/activate.bat
```
Si jamais cela ne fonctionne pas, exécutez Powershell en tant qu'administrateur. Une fois que la nouvelle invite de commandes est alors ouverte, exécutez-y le code suivant :
```bash
  Set-ExecutionPolicy RemoteSigned
```
Une fois que cela est fait, revenez à votre première invite de commandes puis entrez-y : 
```bash
  env/Scripts/activate
```
Depuis un autre OS, vous n'aurez qu'à rentrer ceci à l'intérieur de votre invite de commandes afin de pouvoir activer votre environnement virtuel (Mac/Linux/Autres systèmes) :
```bash
  source env/bin/activate
```
Enfin, pour installer les paquets requis, rentrez ensuite le code ci-dessous :
```bash
  pip install -r requirements.txt
```

#### Troisième étape : utilisation
Toujours depuis l'invite de commandes, rentrez enfin les deux commandes suivantes :
```bash
  cd backend/SoftDeskAPI
  python manage.py runserver
```
Une fois le serveur démarré, il ne vous restera plus qu'à cliquer sur le rien renvoyé par le terminal afin d'accéder au site et utiliser l'application Web qui a été développée.