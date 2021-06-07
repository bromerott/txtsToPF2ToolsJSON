#json library helps us take a python class and turn it into a json instantly
import json
#custom class inside pf2entry.py
from pf2entry import PF2Entry
#regex so we can match dynamically some text
import re
#os so we can iterate through all files in a directory
import os

#Simple function that removes \n and \ts from a string
def removeTabsAndNLC(x):
    return x.replace('\n','').replace('\t','')

#Function that takes an array of strings, and concatenates them with commas
#The function removes \t and \n characters, and stops concatenating after finding an element
#without any text on it
def makeTraitString(arr):
    result=""
    for e in arr:
        if len(removeTabsAndNLC(e))==0:
            break
        else:
            result += removeTabsAndNLC(e) + ","
    return result

#Variable: folder where the .txt files we need to convert to json are
inputPath = "C:/Users/P028097/Documents/The Great Conversion/playground/detail"

count = 0
#For every file in the folder
for inputFile in os.listdir(inputPath):
    #Only for .txt files:
    if inputFile.endswith(".txt"):
        print(count+1,") ",inputFile)
        #File opening
        file = open(inputPath+"/"+inputFile, "r",encoding='utf-8')
        #reading all line contents
        contents = file.readlines()
        #print(contents[1])
        #If its a hazard, lets just skip it for now. I only have like 4 traps! better done manually
        if (removeTabsAndNLC(contents[1])=="HAZARD"):
            continue
        #print(contents)
        #We instantiate a new PF2Entry class (imported above)
        e = PF2Entry()
        #Easy, non-variable stuff
        #We use type - so the creature type is taken from the traits line in the .txt file
        e.type="-"
        #name, level, alignment, size and traits are all static positions
        e.name=removeTabsAndNLC(contents[0])
        e.level=int(removeTabsAndNLC(contents[2]))
        e.alignment=removeTabsAndNLC(contents[3])
        e.size=removeTabsAndNLC(contents[4])
        e.traits=makeTraitString(contents[5:13])
        #Perception Tuple (file has 1 string, gotta divide it into value and note - we use the ';' separator)
        perceptionTuple = contents[contents.index('\tPerception\n')+1].replace(',',';').split(";")
        #The value is whatever is after the ';' separator
        e.perception['value']=removeTabsAndNLC(perceptionTuple[0])
        #If theres notes
        if len(perceptionTuple)>1:
            e.perception['note']=removeTabsAndNLC(perceptionTuple[1])
        #print(e.perception)
        #Skills pending, probably wil do them manually

        #AScores
        #The position is not static, but we can do a .index function to search the contents array
        #for "STR" or "DEX", and just assign the contents of the next line
        e.strength['value']=removeTabsAndNLC(contents[contents.index('\tSTR\n')+1])
        e.dexterity['value']=removeTabsAndNLC(contents[contents.index('\tDEX\n')+1])
        e.constitution['value']=removeTabsAndNLC(contents[contents.index('\tCON\n')+1])
        e.intelligence['value']=removeTabsAndNLC(contents[contents.index('\tINT\n')+1])
        e.wisdom['value']=removeTabsAndNLC(contents[contents.index('\tWIS\n')+1])
        e.charisma['value']=removeTabsAndNLC(contents[contents.index('\tCHA\n')+1])
        #Same for AC, Saves, speed
        e.ac['value']=removeTabsAndNLC(contents[contents.index('\tAC\n')+1])
        e.fortitude['value']=removeTabsAndNLC(contents[contents.index('\tFort\n')+1])
        e.reflex['value']=removeTabsAndNLC(contents[contents.index('\tRef\n')+1])
        e.will['value']=removeTabsAndNLC(contents[contents.index('\tWill\n')+1])
        e.speed=removeTabsAndNLC(contents[contents.index('\tSpeed\n')+1])

        #Dealing with hp, resistances and weaknesses
        #We split the HP line into HP and everything after the ";" character
        substrHPAndMore = removeTabsAndNLC(contents[contents.index('\tHP\n')+1]).split(';')
        e.hp['value']=substrHPAndMore[0]
        #Everything after the HP is concatenated with ";"
        defenseStrings = ';'.join(substrHPAndMore[1:])
        #If theres Immunities/Resistances/Weakness entries:
        if len(substrHPAndMore)>1:
            #Find where Immunities are
            immunoStart = defenseStrings.find('Immunities')
            #when immunoStart = -1, it means theres no Immunities in the string
            if (immunoStart>0):
                #Find where the immunities end
                nextStop = defenseStrings.find(';')
                #if theres no end, just take everything remaining
                if nextStop==-1:
                    e.immunity['value'] = defenseStrings[defenseStrings.find('Immunities')+10:].strip()
                else:
                    e.immunity['value'] = defenseStrings[defenseStrings.find('Immunities')+10:nextStop].strip()
                #Reduce the string, taking out the Immunities entry
                defenseStrings = defenseStrings[nextStop:]
            
            #We apply the same logic to Resistances and Weaknesses - first finding if theres any, and then finding the next ";"
            resistoStart = defenseStrings.find('Resistances')
            if (resistoStart>0):
                nextStop = defenseStrings.find(';')
                if nextStop==-1:
                    e.resistance['value'] = defenseStrings[resistoStart+11:].strip()
                else:
                    e.resistance['value'] = defenseStrings[resistoStart+11:nextStop].strip()
                defenseStrings = defenseStrings[nextStop:]
            weakStart = defenseStrings.find('Weaknesses')
            if (weakStart>0):
                nextStop = defenseStrings.find(';')
                e.weakness['value'] = defenseStrings[weakStart+10:].strip()

        #Melee Strikes always have "Melee", Ranged always have "Ranged"
        meleeEntries = [i for i, x in enumerate(contents) if x == "\tMelee\n"]
        rangedEntries = [i for i, x in enumerate(contents) if x == "\tRanged\n"]

        #For each "Melee" found:
        for strikeIndex in meleeEntries:
            #The strike string (which contains the name, bonus and dmg entry) is after the word "Melee" and after the Action line
            strikeString = removeTabsAndNLC(contents[strikeIndex+2]).replace(',','').strip()
            #Name of attack is right before the next space (split defaults to the whitespace character)
            nameOfAttack = strikeString.split()[0]
            #Att Bonus is right after the first space
            attBonus = strikeString.split()[1]
            #If theres traits:
            traits=""
            #traits are always in parenthesis - we use regex to catch whats inside the parenthesis in the strkeString
            if (re.search("\(([^)]+)", strikeString)):
                traits = re.search("\(([^)]+)", strikeString).group(1)
            #Get damage
            #print(strikeString)
            #We use regex to find whatever is after Damage
            damageString = re.search("Damage (.*)",strikeString).group(1)
            e.strikes.append({"name":nameOfAttack,"traits":traits,"attack":attBonus,"damage":damageString,"type":"Melee"})

        #We use the same logic but apply it to ranged strikes
        for strikeIndex in rangedEntries:
            strikeString = removeTabsAndNLC(contents[strikeIndex+2])
            nameOfAttack = strikeString.split()[0]
            attBonus = strikeString.split()[1]
            #If theres traits:
            traits=""
            if (re.search("\(([^)]+)", strikeString)):
                traits = re.search("\(([^)]+)", strikeString).group(1)
            #Get damage
            #print(strikeString)
            damageString = re.search("Damage (.*)",strikeString).group(1)
            e.strikes.append({"name":nameOfAttack,"traits":traits,"attack":attBonus,"damage":damageString,"type":"Ranged"})

        #Finally, special abilities - the meat of the problem
        #I am not going to bother with spells, thats a pain and better done manually

        #Let us first search for Special abilities with (A) on them (so they do not have Melee or Ranged lines, just a generic name)
        #this function takes ALL lines that have an (A), including Melee or Ranged strikes
        potentialSpecial1AIndexes = [i for i, x in enumerate(contents) if x == "\t(A)\n"]
        special1AIndexes=[]
        #We filter all "(A)" entries so as not to include "Melee" or "ranged", since those are already done
        for index in potentialSpecial1AIndexes:
            if (contents[index-1]!="\tMelee\n" and contents[index-1]!="\Ranged\n"):
                #its a match!
                special1AIndexes.append(index)

        #Now with those filtered out, we just append to the specials array a dict:
        #the name of the special action is right before the (A) line, and the description is right after it
        for index in special1AIndexes:
            e.specials.append({"name":removeTabsAndNLC(contents[index-1]),
                                "actions":"one",
                                "type":"offense",
                                "description":removeTabsAndNLC(contents[index+1])})

        #then lets look for (AA)
        #We do not need to filter out the strikes, since theres no (AA) strikes in my doc
        special2AIndexes = [i for i, x in enumerate(contents) if x == "\t(AA)\n"]
        for index in special2AIndexes:
            e.specials.append({"name":removeTabsAndNLC(contents[index-1]),
                                "actions":"two",
                                "type":"offense",
                                "description":removeTabsAndNLC(contents[index+1])})

        #then lets look for (AAA)
        special3AIndexes = [i for i, x in enumerate(contents) if x == "\t(AAA)\n"]
        for index in special3AIndexes:
            e.specials.append({"name":removeTabsAndNLC(contents[index-1]),
                                "actions":"three",
                                "type":"offense",
                                "description":removeTabsAndNLC(contents[index+1])})

        #Finally Finally, let us look for passive special abilities
        #Strategy: Find lone words on the entry that do not match the "default" expressions
        #1st haystack:
        #Right after Immunities+Resistances+Weaknesses but before Speed (defensive passive specials)
        defenseHaystack = contents[contents.index('\tHP\n')+2:contents.index('\tSpeed\n')]

        #Heuristic: If a content line is less than 20 characters long, and its between HP and Speed, it probably is an ability name
        for i in range(0,len(defenseHaystack)):
            try:
                if len(removeTabsAndNLC(defenseHaystack[i]))<20:
                    e.specials.append({"name":removeTabsAndNLC(defenseHaystack[i]),
                                        "actions":"",
                                        "type":"defense",
                                        "description":removeTabsAndNLC(defenseHaystack[i+1])})
            except:
                print("Error getting Defense non-action Special")

        #print(e.specials)

        #2nd haystack:
        #Right after Speed
        offenseHaystack = contents[contents.index('\tSpeed\n')+2:]
        #Heuristic: If a content line is less than 20 characters long, its after Speed, and it is not Melee/Ranged/A/AA/AAA it probably is an ability name
        actionRelatedTerms = ["\tMelee\n","\Ranged\n","\t(A)\n","\t(AA)\n","\t(AAA)\n"]
        actionTerms = ["\t(A)\n","\t(AA)\n","\t(AAA)\n"]
        #'\tSpeed\n'
        for i in range(0,len(offenseHaystack)-1):
            try:
                if len(removeTabsAndNLC(offenseHaystack[i]))<20:
                    if offenseHaystack[i] not in actionRelatedTerms:
                        if offenseHaystack[i+1] not in actionTerms:
                            e.specials.append({"name":removeTabsAndNLC(offenseHaystack[i]),
                                        "actions":"",
                                        "type":"offense",
                                        "description":removeTabsAndNLC(offenseHaystack[i+1])})
            except:
                print("Error getting Offense non-action Special")

        #We then take the "e" object, and use the json library to dump the dict conversion of that object
        jsonString = json.dumps(e.__dict__)
        #We just print the jsonString to a file - in this case, the directory will be
        #the input directory + a jsons folder
        #and the filename will be kept the same (with the exception of the extension, which will now be .json)
        jsonfile = open(inputPath+"/jsons/"+inputFile.split('.')[0]+".json", "w",encoding='utf-8')
        jsonfile.writelines(jsonString)
        jsonfile.close()
        file.close()
        count+=1