#update requirements.txt
pip freeze>requirements.txt

$update Procfile
echo "">Procfile

#start up git
git init

#committing app files to git
git add .
git commit -m "<comments>"

#heroku login
heroku login

#if heroku app not created, use this.
heroku create fyp-testrun --buildpack heroku/python

#if heroku app created, use this instead.
heroku git:remote -a fyp-app-deployment 

https://fyp-testrun.herokuapp.com/

https://git.heroku.com/fyp-testrun.git

#pushing git & deploy application on heroku
git push heroku master

#to make application go live (to go offline, web = 0)
heroku ps:scale web=1

heroku ps:scale web=0