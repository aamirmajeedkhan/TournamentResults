# Introduction
This is a second project of udaity full stack developer course.
This project implements a tournament using swiss pairing method.
The project uses postgresql as a database and python 2.7 as programming
language.
# Project Files
*  **tournament.sql** This file create database schema needed for tournament.This
includes table creation and view creation scripts.
*  **tournament.py** This file contain python code.
*  **tournament_test.py** This file contain python test cases.
# Tournament Database
Tournament database consist of following table. 
* **tournaments** store id aand name of tournament.
* **players** store id and name of player.
* **tournamentplayers** resolve many to many relationship between above two tables.
* **matches** records player, opponent and tie.
Couple of views are also created.
* **playerstanding** This view shows list of player ranked by their points.
* **opponents** This view shows player with thier opponent in each tournament.

**Note:** *tournaments, players, tournamentplayers and matches contain time field for audit purpose.*
# Extra Credit Feature implemented
   Following features are implemented beyond the baseline requirement.
* Prevent rematches between players. This feature is implemented by a view called 
  opponent which helps avoiding rematch with old opponent.
* Don't assume an even number of player. This feature is implemented by a method called 
  **findByeIndex** in **tournament.py** .This feature is tested using a unit test called **testByes**
  in **tournament_test.py** .
* Support games where a draw (tied game) is possible. This feature is implemented by extending 
  **reportMatch(winner, loser, tied=False, tournament_id=1)** method in **tournament.py**. By default
  tied is false.
* Support more than one tournament in the database, so matches do not have to be deleted between tournaments.
  tournaments is provided for the purpose also most of the function have an argument of tournament_id to 
  accomodate the same. e.g. **playerStandings(tournament_id=1)** .
* A point system is maintain to helps decide the winner . This is implemented by keeping two global constant 
  in database for win and tie points. These constants then later used in playerstanding view to help rank 
  player. 
# Setup
* Download and install [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/) .
* Setup the environment following [instructions](https://www.udacity.com/wiki/ud197/install-vagrant).
* Create the database by running command **\psql -f tournament.sql** on command line.
* Run testcase by running **python tournament_test.py**. Make sure all 11 unit cases are successfully passed 
  with final message should be **Success!  All tests pass!**