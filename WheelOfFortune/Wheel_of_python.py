import random
import json
import random
import time

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
VOWELS = "AEIOU"
VOWEL_COST = 250

class WOFPlayer():
    prizeMoney = 0
    prizes = []
    def __init__(self,name):
        self.name = name

    def addMoney(self,amt):
        self.prizeMoney += amt

    def goBankrupt(self):
        self.prizeMoney = 0

    def addPrize(self,prize):
        self.prizes.append(prize)

    def __str__(self):
        return "{} (${})".format(self.name,self.prizeMoney)
        
class WOFHumanPlayer(WOFPlayer):

    def getMove(self,category,obscuredPhrase, guessed):
        base_promt = """
                     {my.name} has ${my.prizeMoney}

                     Category: {cat}
                     Phrase:  {obs}
                     Guessed: {gues}

                     Guess a letter, phrase, or type 'exit' or 'pass':
                     """.format(my=self, cat = category, obs = obscuredPhrase , gues = guessed )
        move = input(base_promt)
        return move

   
class WOFComputerPlayer(WOFPlayer):

    #list of english characters sorted from least frequent to most frequent
    SORTED_FREQUENCIES = "ZQXJKVBPYGFWMUCLDRHSNIOATE"

    def __init__(self, name,  difficulty = 0):
        super().__init__(name)
        self.difficulty = difficulty

    def smartCoinFlip(self):
        randnum = random.randint(1, 10)
        if  randnum > self.difficulty :
             return True
        elif randnum <= self.difficulty :
             return False
            
    def getPossibleLetters(self, guessed):
        Letters_all = [letter for letter in LETTERS]
        Letters_to_guess = Letters_all.copy()
        for L in Letters_all :
            if ((L in VOWELS and self.prizeMoney < VOWEL_COST) or (L in guessed)) :
                Letters_to_guess.remove(L)
        return Letters_to_guess

    def getMove(self, category, obscureedPhrase, guessed):
        possibilities = self.getPossibleLetters(guessed)
        Freq_updated = []
        if not possibilities :
            pass
        else:
            for L in self.SORTED_FREQUENCIES:
                if L in possibilities:
                    Freq_updated.append(L)
            if self.smartCoinFlip(): #making a good move - the most likely character
                return Freq_updated[-1]
            else:                    #making a bad move - the least likely character
                return Freq_updated[0]

# Reapeatedly asks the user for a number between min & max (inclusive)
def getNumberBetween(prompt, min, max):
    userinp = input(prompt) # ask the first time

    while True:
        try:
            n = int(userinp) # try casting to an integer
            if n < min:
                errmessage = "Must be at least {}".format(min)
            elif n > max:
                errmessage = "Must be the most {}".format(max)
            else:
                return n
        except ValueError: # The user dint enter a number
            errmessage = "{} is not a number.".format(userinp)

        # if we haven't gotten a number yet, add the error message
        # and ask again
        userinp = input("{}\n{}".format(errmessage,prompt))

# Spins the wheel of fortune wheel to give a random prize
# Examples:
#    { "type": "cash", "text": "$950", "value": 950, "prize": "A trip to Ann Arbor!" },
#    { "type": "bankrupt", "text": "Bankrupt", "prize": false },
#    { "type": "loseturn", "text": "Lose a turn", "prize": false }

def spinWheel():
    with open("wheel.json","r") as f:
        wheel = json.loads(f.read())
        return random.choice(wheel)

# Returns a category & phrase (as a tuple) to guess
# Example:
#     ("Artist & Song", "Whitney Houston's I Will Always Love You")

def getRandomCategoryAndPhrase():
    with open("phrases.json","r") as f:
        phrases = json.loads(f.read())

        category = random.choice(list(phrases.keys()))
        phrase = random.choice(phrases[category])
        return (category, phrase.upper())
        
# Given a phrase and a list of guessed letters, returns an obscured version
# Example:
#     guessed: ['L', 'B', 'E', 'R', 'N', 'P', 'K', 'X', 'Z']
#     phrase:  "GLACIER NATIONAL PARK"
#     returns> "_L___ER N____N_L P_RK"

def obscurePhrase(phrase, guessed):
    rv = ""
    for s in phrase:
        if ( s in LETTERS) and ( s not in guessed ):
            rv += "_"
        else :
            rv += s
    return rv

# Returns a string representing the current state of the game
def showBoard(category, obscuredPhrase, guesed):
    return """
Category : {}
Phrase:    {}
Guessed:   {}""".format(category, obscuredPhrase, ", ".join(sorted(guessed)))

# Game LOGIC CODE
print("="*15)
print("Wheel OF PYTHON")
print("="*15)
print("")

num_human = getNumberBetween("How many human players? ", 0 , 4)

# Create the human player instances
human_players = [WOFHumanPlayer(input("Enter the name for human player #{} ".format(i+1))) for i in range(num_human)]

num_computer = getNumberBetween("How many computer players ? ", 0 , 4)

# If there are computer players, ask how difficult they should be
if num_computer >= 1:
    difficulty = getNumberBetween("What difficulty for the computers ? (1-10) ",1,10)

# Create the computer player instances
computer_players = [WOFComputerPlayer("Computer {}".format(i+1), difficulty) for i in range (num_computer)]

players = human_players + computer_players

# No players , no game
if len(players) == 0:
    print("We need players to play!")
    raise Exception("Not enough players")

# category and phrase are strings
category, phrase = getRandomCategoryAndPhrase()

#guessed is a list of the letters that have been guessed
guessed = []

# playerIndex keeps track of the index (0 to len(players)-1 ) of the player whose turn it is
playerIndex = 0

# will be set to the player instance when/if someon wins
winner = False

def requestPlayerMove(player,category,guessed):
    while True: # we're going to keep asking the player for a move until they give a valid one
        time.sleep(0.1) # added so that any feedback is printed out before the next prompt

        move = player.getMove(category,obscurePhrase(phrase, guessed), guessed)
        move = move.upper() # convert whatever the player entered to UPPERCASE

        if move == "EXIT" or move == "PASS":
            return move
        elif len(move) == 1: # they have guessed a character
            if move not in LETTERS : # the user entered an invalid letter (such as @ or $)
                print("Guesses should be letters. Try again.")
                continue
            elif move in guessed : # this letter has already been guessed
                print("{} has already been guessed. Try again.".format(move))
                continue
            elif move in VOWELS and player.prizeMoney < VOWEL_COST:
                # if it's a vowel, we need to be sure the player has enough money
                print("Need ${} to guess a vowel. Try again.".format(VOWEL_COST))
                continue
            else:
                return move
        else: # they guessed the phrase
            return move

while True:
    player = players[playerIndex]
    wheelPrize = spinWheel()

    print("")
    print("-"*15)
    print(showBoard(category, obscurePhrase(phrase,guessed),guessed))
    print("")
    print("{} spins...".format(player.name))
    time.sleep(2) # pause for dramatic effect!
    print("{}!".format(wheelPrize["text"]))
    if(wheelPrize["prize"]):
        print("{}!".format(wheelPrize["prize"]))
    time.sleep(1) # pause again for more dramatic effect!

    if wheelPrize["type"] == "bankrupt":
        player.goBankrupt()
    elif wheelPrize["type"] == "loseturn":
        pass # do nothing; just move on to the next player
    elif wheelPrize["type"] == "cash":
        move = requestPlayerMove(player,category,guessed)
        if move == "EXIT" : #leave the game
            print("Until next time!")
            break
        elif move == "PASS": # will just move on to next player
            print("{} passes".format(player.name))
        elif len(move) == 1 : #they guessed a letter
            guessed.append(move)

            print("{} guesses '{}'".format(player.name,move))

            if move in VOWELS:
                player.prizeMoney -= VOWEL_COST

            count = phrase.count(move) #returns an integer with how many times this letter appears
            if count > 0:
                if count == 1:
                    print("There is one {}".format(move))
                else:
                    print("There are {} {}'s".format(count,move))

                # Give them te money and the prizes
                player.addMoney(count * wheelPrize["value"])
                if wheelPrize["prize"]:
                    player.addPrize(wheelPrize["prize"])

                # all of the letters have been guessed
                if obscurePhrase(phrase,guessed) == phrase:
                    winner = player
                    break

                continue # this player gets to go again

            elif count == 0:
                print("There is no {}".format(move))
        else: #they guessed the whole phrase
            if move == phrase: #they guessed the full phrase correctly
                winner = player

                # Give them the money and the prizes
                player.addMoney(wheelPrize["value"])
                if wheelPrize["prize"]:
                    player.addPrize(wheelPrize["prize"])

                break
            else:
                print("{} was not the phrase".format(move))
    # Move on to the next player (or go back to player [0] if we reached the end)
    playerIndex = (playerIndex + 1) % len(players)

if winner:
    # in  your head you should hear this as being announced by a game show host
    print("{} wins! The phrase was {}".format(winner.name,phrase))
    print("{} won ${}".format(winner.name,winner.prizeMoney))
    if len(winner.prizes) > 0:
        print("{} also won:".format(winner.name))
        for prize in winner.prizes :
            print("     - {}".format(prize))
    time.sleep(6)
else:
    print("Nobody won. The phrase was {}".format(phrase))
    time.sleep(6)
    
