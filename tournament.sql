-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Make sure there is no database already with the name tournament
Drop Database If Exists tournament ;
-- Create tournament database
Create database tournament;

-- CREATE Tournaments table
-- time field is included to record the
-- tournament registration time
Create table tournaments
(
id SERIAL PRIMARY KEY,
name Text NOT NULL,
time timestamp DEFAULT now()
);

-- Create a default tournament
INSERT INTO tournaments (name)
VALUES ('English Premier League');

-- Create Players table
-- time field is included to record the
-- player registration time
CREATE TABLE players
( id SERIAL PRIMARY KEY ,
 name Text NOT NULL,
time timestamp DEFAULT now() );

-- registration  table shows players registered in tournament
-- it also capture player performance so far

CREATE TABLE registration ( tournament_id INTEGER REFERENCES tournaments(id),
                        player_id     INTEGER REFERENCES players(id),
                        wins          INTEGER DEFAULT 0 NOT NULL,
                        points        INTEGER DEFAULT 0 NOT NULL,
                        byes          INTEGER DEFAULT 0 NOT NULL,
                        PRIMARY KEY(tournament_id, player_id)
                     );


  -- Create matches table
  -- winner and loser columns always represent opponents in case of
  -- tie false they will also represent winner and loser as well
  -- time field is included to record the
  -- player registration time
  CREATE TABLE matches (  id  SERIAL PRIMARY KEY,
                              tournament_id INTEGER REFERENCES tournaments(id),
                              winner_id INTEGER REFERENCES players(id) NOT NULL,
                              loser_id INTEGER REFERENCES players(id) NOT NULL,
                              tie  BOOLEAN DEFAULT false,
                              time timestamp DEFAULT now()
                              );



CREATE VIEW playerstanding
 AS
SELECT registration.player_id as id,players.name as name,
        registration.wins as wins,count(matches) as matches,
        registration.byes as byes,
        registration.tournament_id as tournament_id

 FROM registration
 JOIN players ON
      registration.player_id = players.id
 LEFT JOIN matches ON
       (registration.tournament_id= matches.tournament_id) AND
       ( registration.player_id = matches.winner_id OR
         registration.player_id = matches.loser_id
       )
 GROUP BY  registration.player_id,players.name,registration.tournament_id
 ORDER BY points desc;
