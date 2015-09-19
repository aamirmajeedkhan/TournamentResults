-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Make sure there is no database already with the name tournament
DROP DATABASE If Exists tournament ;
-- Create tournament database
CREATE DATABASE tournament;

-- connect to database

\c tournament;

--Global constanst for points. 3 for Win and 1 for Draw
--This points are used to rank player

CREATE FUNCTION win_point() RETURNS INTEGER
 AS 'SELECT 3;'
 LANGUAGE SQL IMMUTABLE;

CREATE FUNCTION tie_point() RETURNS INTEGER
 AS 'SELECT 1;'
 LANGUAGE SQL IMMUTABLE;

-- CREATE Tournaments table
-- time field is included to record the
-- tournament registration time
CREATE TABLE tournaments
(
  id SERIAL PRIMARY KEY,
  name Text NOT NULL,
  time TIMESTAMP DEFAULT now()
);

-- Create a default tournament
INSERT INTO tournaments (name)
VALUES ('English Premier League');

-- Create Players table
-- time field is included to record the
-- player registration time
CREATE TABLE players
(
  id SERIAL PRIMARY KEY ,
  name Text NOT NULL,
  time TIMESTAMP DEFAULT now()
);
-- This table resolve many to many relationship between
-- tournaments and players tables.
CREATE TABLE tournamentplayers
( tournament_id INTEGER REFERENCES tournaments(id) ON DELETE CASCADE,
  player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
  time TIMESTAMP DEFAULT now(),
  PRIMARY KEY (tournament_id,player_id)
);
  -- Create matches table
  -- Along with capturing table this tables shows match result as well.
  -- player1_id and player2_id are playerids with player1 represents a winner
  -- where as player2 represents loser in case of a win. In a bye sitaution both player1id and playerid are same.
  -- For a tie match tied=TRUE otherwise it always be FALSE even if its a bye
  -- time field is included to record the
  -- time represents match registation time
CREATE TABLE matches (
  id  SERIAL PRIMARY KEY,
  tournament_id INTEGER REFERENCES tournaments(id),
  player1_id INTEGER REFERENCES players(id) NOT NULL,
  player2_id INTEGER REFERENCES players(id) NOT NULL,
  tied  BOOLEAN DEFAULT false,
  time TIMESTAMP DEFAULT now()
  );

--FUNCTION RETURNS number of wins player have so far
CREATE FUNCTION wins(player_id INTEGER) RETURNS INTEGER
AS $$
SELECT count(id)::INTEGER FROM matches WHERE
matches.player1_id=player_id AND matches.tied=FALSE
$$
LANGUAGE SQL;

--FUNCTION RETURNS number of byes player have so far
CREATE FUNCTION byes(player_id INTEGER) RETURNS INTEGER
AS $$
SELECT count(id)::INTEGER FROM matches WHERE
matches.player1_id = player_id AND matches.player2_id = player_id
$$
 LANGUAGE SQL;

--FUNCTION RETURNS number of matches player played so far
CREATE FUNCTION matches(player_id INTEGER) RETURNS INTEGER
AS $$
SELECT count(id)::INTEGER FROM matches WHERE
matches.player1_id=player_id OR  matches.player2_id = player_id
$$
LANGUAGE SQL;

--FUNCTION RETURNS number of ties player have so far
CREATE FUNCTION ties(player_id INTEGER) RETURNS INTEGER
AS $$
 SELECT count(id)::INTEGER FROM matches WHERE
 (matches.player1_id = player_id OR matches.player2_id = player_id) AND
  matches.tied=TRUE
$$
 LANGUAGE SQL;

--View depicts player performance order by points
CREATE VIEW playerstanding
 AS
SELECT players.id AS id,players.name AS name, matches(players.id) AS matches,
wins(players.id) AS wins,byes(players.id) AS byes,ties(player_id) AS tie,
wins(players.id) * win_point() + ties(players.id) * tie_point() AS points,
tournamentplayers.tournament_id AS tournament_id
FROM players
JOIN tournamentplayers ON
tournamentplayers.player_id=players.id
ORDER BY points DESC;

--View depcits opponent of each player
 CREATE VIEW opponents
 AS
 SELECT players.id AS player_id,matches.player2_id AS opponent_id,
        matches.tournament_id AS tournament_id
 FROM    players
 JOIN    matches ON
        (players.id = matches.player1_id
         )
 UNION
 SELECT players.id AS player_id,matches.player1_id AS opponent_id,
        matches.tournament_id AS tournament_id
 FROM    players
 JOIN    matches ON
        (players.id = matches.player2_id
       );
