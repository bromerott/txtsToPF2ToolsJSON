#Variables

#What line to start reading the .txt file (so we can ignore the title and trademark message)
monsterStart = 15
#Path to the folder containing the .txt file
inputPath = "C:/Users/P028097/Documents/The Great Conversion/playground"
#Path to the .txt file
inputFile = "original2.txt"

#File opening ignoring the first {monsterStart} lines
file = open(inputPath+"/"+inputFile, "r",encoding='utf-8')
#contents will contain an array with each line read from the file
contents = file.readlines()
file.close()
#We start reading from {monsterStart}
contents = contents[monsterStart:]

#Finding all entry indexes, defined as the index right before CREATURE or HAZARD
entryCount = 0
entryIndexes = []
#For every line in the file
for i in range(0,len(contents)):
    #When the line contains "CREATURE" or "HAZARD"
    if (contents[i]=="\tCREATURE\n" or contents[i]=="\tHAZARD\n"):
        #Add the index position of the line just before it
        entryIndexes.append(i-1)
        entryCount+=1

print("Found ",entryCount," entries (creatures and hazards).")

#For all entries:
for j in range(0,entryCount):
    #On the final entry, just take every line until the end
    if (j==(entryCount-1)):
        entry = contents[entryIndexes[j]:]
    else:
        #on all other entries, we start from index[j] and continue until the next index position (-2)
        entry = contents[entryIndexes[j]:entryIndexes[j+1]-2]

    #We eliminate all trailing \n \t\n in the entry. In the middle \ns will probably be of use later
    for k in range(len(entry)):
        if (entry[len(entry)-1]=="\n" or entry[len(entry)-1]=="\t\n"):
            entry.pop(len(entry)-1)
        else:
            break

    #We then get the name of the entry, defined as the first line of the entry
    name = entry[0].replace('\n','').replace(',','').replace('-','')
    #We use this name to create the filename, applying a camelcase function so its neat
    filename = ''.join(x for x in name.title() if not x.isspace()) + ".txt"
    print(j+1,": ",filename)
    #Then we print all contents of the entry to the filename
    file = open(inputPath+"/detail/"+filename, "w",encoding='utf-8')
    file.writelines(entry)
    file.close()

print("Done!")