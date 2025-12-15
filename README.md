- This project was completed over the course of four days using Python 3.11.10 and PostgreSQL.<br>

- It's purpose is to demonstrate several concepts I am familiar with. It consumes trivia API to import a database with questions and answers, with one-off sync.<br>
  
- The app contains a list of questions with filters, a detail page for every question with the option to choose the correct answer and a game I designed.<br> 

-For a complete build run the following command in the directory of your choice. It builds the project one-take:<br>
    cd trivia-app<br>
    pyenv local 3.11.10 (optional, I prefer to use pyenv for versions management)
    )<br>
    make build_app<br>

- I have included docker files for a quick build, too: (cd trivia-app && docker-compose build && docker-compose up)

- You will find useful tasks in Makefile, with descriptions of what each task does, in comments.

- I have included .pgpass and sudo commands in Makefile to make it easier to setup, they shouldn't be included in production repo.

- To sync local settings use:
    make sync_local (The generated file from symlink should never be included in the production repo, too)

- In the files of apps there are several detailed comments that should be helpful when diving deeper to the code.

- The increased complexity of import_data.py is explained in the file's comments, along with several details on how and why things were done this way.

-I decided to increase complexity of the task by designing a simple game, conceptually related to the task, 
    to demonstrate some more features of django and web development that I am familiar with.

-You will find instructions on how to play the game in the project/game/README file.
