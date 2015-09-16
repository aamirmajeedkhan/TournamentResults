#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import sys
from _collections import defaultdict
# Global constanst for points. 3 for Win and 1 for Draw
TIE_POINTS = 1
WIN_POINTS = 3


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches(tournament_id=1):
    """Remove all the match records from the database.
    Arg:
      tournament_id: shows which tournament's match to delete
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM matches WHERE tournament_id= %s",
                   (tournament_id,))
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database.
       This also mean to remove all records carrying this player
       information.
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM matches")
    cursor.execute("DELETE FROM registration")
    cursor.execute("DELETE FROM players")
    conn.commit()
    conn.close()


def countPlayers(tournament_id=1):
    """Returns the number of players currently registered.
    Arg:
      tournament_id: shows which tournament's player to count
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(player_id) FROM registration " +
                    " WHERE tournament_id = %s" ,
                 (tournament_id,))
    result=cursor.fetchall()
    conn.close()
    return  result[0][0]


def registerPlayer(name,tournament_id=1):
    """Adds a player to the tournament database.
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
    Args:
      name: the player's full name (need not be unique).

    Returns :
        id of player
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO players ( name ) VALUES (%s) RETURNING id",
                   (name,))
    conn.commit()
    player_id=cursor.fetchone()
    cursor.execute("INSERT INTO registration (tournament_id,player_id) "
                    "VALUES (%s,%s)",
                   (tournament_id,player_id))
    conn.commit()
    conn.close()
    return player_id


def playerStandings(tournamenet_id=1):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place,
    or a player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches,bye):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
        byes: the number of byes the player has so far
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id,name,wins,matches,byes FROM playerstanding WHERE tournament_id = %s",
                    (tournamenet_id,))
    results = cursor.fetchall()
    conn.close()
    return results


def reportMatch(winner, loser, tied=False, tournament_id=1):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
      tied : TRUE shows a tie match and vicersa
      tournament_id : tournament id where that match belongs
    """
    # winner and loser with same id means a bye
    conn=connect()
    cursor=conn.cursor()
    cursor.execute ("INSERT INTO matches (tournament_id, winner_id, loser_id, tied) " +
                    "VALUES (%s,%s,%s,%s)",(tournament_id,winner,loser,tied))
    if (winner != loser):
        cursor.execute (" UPDATE registration SET " +
                         " wins = wins+1 ," +
                         "points = points + %s " +
                         " WHERE tournament_id  =%s AND player_id = %s",
                         (WIN_POINTS,tournament_id,winner))
        conn.commit()
    else:
        cursor.execute (" UPDATE registration SET " +
                         " byes = byes+1 AND points = points + %s " +
                         " WHERE tournament_id  =%s AND player_id = %s",
                         (TIE_POINTS,tournament_id,winner))
        cursor.commit()
    conn.close()
    

def swissPairings(tournament_id=1):
    """Returns a list of pairs of players for the next round of a match.  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
    Args:
      tournament_id : tournament id where that match belongs

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    swiss_pairings=[]
    player_standings= playerStandings(tournament_id)
    paired_table=[False] * len(player_standings)
    if ( len(player_standings) % 2 != 0) :
        player1_index=findBye(player_standings,paired_table)
        addPairing(swiss_pairings,player_standings,player1,player1)
    opponents_dict=Opponents()
    #for (id,name,wins,matches,byes) in player_standings :
    for index in range(len(player_standings)):
        #Make sure player is not already paired
        if (paired_table[index] == False ) :
            opponent_id=findOpponentIndex(player_standings[index][0],player_standings,
                                     paired_table,opponents_dict)
            addPairing(swiss_pairings,player_standings,index,
                       opponent_id)
    return swiss_pairings

def findOpponentIndex(player_id,player_standings,paired_table,opponents_dict):
    """Returns a likely opponent index in player_standings for a player_id.
    Arg:
      player_id: the player's unique id (assigned by the database)
      player_standings: a list of the players and their win records,
      sorted by wins.
      paired_table : A tuple holds player_id with pair status.
      opponents_dict: A dictionary holds player_id with it's opponent.

    Returns:
      opponent_id which can play with player passed as first paramenter
      the argument.
    """
    for index in range(len(player_standings)):
        #ensure player should not play itself and not already paired
        if ( (player_id != player_standings[index][0]) and
            (paired_table[index] == False ) ):
            #Pass if player already in opponent list
            if player_standings[index][0] in opponents_dict[player_id]:
                continue;
            else :
                paired_table[index] = True
                return index

def Opponents(tournament_id=1):
    """Returns a collection of playersid and opponentsid they played .
    Arg:
      tournament_id: tournament player are registered in
    Returns:
      A list of tuples, each of which contains (player_id, opponent_id):
        player_id: the player's unique id (assigned by the database)
        opponent_id: the id of player who has been an opponent of player_id
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT player_id, opponent_id FROM opponents " +
                     "WHERE tournament_id = (%s)",
                    (tournament_id,))
    results = cursor.fetchall()
    conn.close()
    opponents_dict = defaultdict(list)
    for item in results:
        opponents_dict[item[0]].append(item[1])
    return opponents_dict


def findByeIndex(player_standings, paired_table):
    """Returns a likely index in playerstanding of opponent_id for a player_id.
    Arg:
      player_id: the player's unique id (assigned by the database)
      player_standings: a list of the players and their win records,
      sorted by wins.
      paired_table : A tuple holds player_id with pair status.
      opponents_dict: A dictionary holds player_id with it's opponent.

    Returns:
      opponent_id which can play with player passed as first paramenter
      the argument.
    """
    current_index=len(player_standings)-1
    bye_index=current_index
    min_byes = sys.maxint
    while current_index >=0 :
        if( paired_table[current_index] == False):
            num_byes=player_standings[current_index][4]
            if (num_byes == 0):
                paired_table[current_index] = True
                return current_index
            elif (num_byes < min_byes):
                min_byes=num_byes
                bye_index=current_index
    current_index=current_index-1
    return bye_index

def addPairing(swiss_pairings, player_standings, player1_index, player2_index):
    """ Add a tuple of player and opponent in swisspairing structure.
    Arg:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    swiss_pairings.append(
        (player_standings[player1_index][0],
        player_standings[player1_index][1],
        player_standings[player2_index][0],
        player_standings[player2_index][1]))
