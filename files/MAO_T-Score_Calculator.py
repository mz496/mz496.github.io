# T-Score Calculator, modified from S-Score Calculator, June 7, 2014, Matthew Zhu

import math
import numpy as np
import urllib.request
from bs4 import BeautifulSoup

###################################################
    
# the list of people removed from consideration for states
# need title case
middleSchoolers = ["Max Ranis", "Azzara Nincevic", "Nithya Kasarla", "Kishan Patel"]

# for output of all s-scores at the end "as of ..."
date = "March Regional, 3/1/2014"

# decimal places to calculate to throughout output+program
decimalPlaces = 4

# number of people (top X) to analyze for latex output; usually limited by the number of rows that can fit in the table
# 45 works well
numRows = 45

# "Real Tie System" (True) is when the output says "same score means same rank"
# "Default Tie System" (False) is when the output says "regardless of score, everybody gets a unique rank number"
# RTS is identical to famat's system, DTS is useful for latex output when you don't want points overlapping
realTieSystem = True

# format: use any of the URLs for a comp, e.g. Sweepstakes, and remove e.g. "Sweeps.html" and leave the /
# http:// required
baseURLs = [
"http://famat.org/Downloadable/Results/Hagerty%20Student%20Delegate%20March%20Statewide/",
"http://famat.org/Downloadable/Results/Combined03022013/",
"http://famat.org/Downloadable/Results/Tampa%20Bay%20Tech%20Statewide%20Feb%20%202013/",
"http://famat.org/Downloadable/Results/Combined02012013/",
"http://famat.org/Downloadable/Results/Combined01182013/",
"http://famat.org/Downloadable/Results/Vero%20Beach%20January%202013/"]

###################################################

def roundList(iterable, ndigits):
    resultList = []
    for l in range(len(iterable)):
        resultList.append(round(iterable[l], ndigits))
    return resultList

def fillZeroes(num, desiredPlaces):
    # takes in a vanilla number and puts out a string with zeroes filled up to desiredPlaces with zeroes
    numstr = str(num)
    # if too few decimal places, fill up the rest with 0s
    while (len(numstr) - 1 - numstr.find(".") < desiredPlaces):
        numstr += "0"
    return numstr

masterlist = {}
divisions = {}
corrections = {}
tableData = ""
plotData = ""

# we wrap the divisions on the outside because we want to do each competition for one division at a time
for division in ["Geometry", "Algebra 2", "Precalculus", "Calculus", "Statistics"]:
    students = {}
    IDs = {}
    
    for cutURL in baseURLs:
        URL = cutURL + urllib.request.quote(division + "_Indv.html")
        # ^idk how this works but some part of it has to be quoted, and some cutURLs break when quoted

        page = urllib.request.urlopen(URL).read()
        soup = BeautifulSoup(page)
        cells = soup.find_all("td") # get a list of all <td> tags (table cells)
        cellText = []
        for tag in cells:
            cellText.append(str(tag)) # convert to string for manipulation

        # order of the 9 tags is (place), (school), (name), (score), (famat ID), (right), (wrong), (blank), (tscore)
        # grab every student's t-score
        for i in range(0, len(cellText), 9):
            if i==0:
                continue # this is the header row that names all the columns
            # i+2 is the position of the student's name, i+8 is t-score
            studentName = cellText[i+2][4:-5].title() # cut tags, standardize to title case
            tScore = float(cellText[i+8][4:-5])
            ID = cellText[i+4][4:-5]
            
            # most top performers will have a 4th-highest t-score at least 60, so cut off these for a little buffer
            # however also an optimization to weed out noobs
            if tScore < 50:
                break
            if studentName in students:
                students[studentName].append(tScore)
            else:
                students.update({studentName:[]}) # create a list for scores and append a new one at each comp
                students[studentName].append(tScore)

            # the last two digits of a famat ID are mutable, e.g. for students in two divisions or who are on/off the team
            ID = ID[:-2]
            
            # construct the corrections dictionary
            # follows format CORRECT(str) : INCORRECT(list) (in case famat fails that hard)
            if ID in IDs:
                # check to see that the name we encountered for this ID matches what we have stored
                if IDs[ID] != studentName:
                    # then add/update a dictionary entry where IDs[ID] is assumed correct and studentName is assumed rogue
                    if IDs[ID] in corrections:
                        corrections[IDs[ID]].append(studentName)
                    else:
                        corrections.update({IDs[ID]:[studentName]})
            else:
                # we're going to have to assume that one spelling is correct... if we store the wrong one first, well, sucks
                # all we really need is a unique index/key to store all of a student's data
                IDs.update({ID:studentName})        

    # at this point we have students={name:[s-scores...],name:[s-scores...]...}

    # correct for spelling errors
    # locate the correct version and add the s-score list of the incorrect version to the correct version
    for correctVer in corrections:
        for incorrectVer in corrections[correctVer]: # (corrections[correctVer] is a list)
            if incorrectVer not in students:
                continue # if there is no error
            else:
                if correctVer in students: # if a known correct version exists
                    students[correctVer] += students[incorrectVer] # merge the s-score lists
                    del students[incorrectVer] # delete the incorrect one
                else:
                    # if we know a spelling is wrong, even though no correct one exists
                    # then we make a correct entry just in case later correct entries come along
                    students.update({correctVer:students[incorrectVer]})
                    # add a new dict entry named correctly using the incorrect version's value(s)
                    del students[incorrectVer] # delete the incorrect one
    
    # re-sort each s-score list once at the end, when everything is added in
    for st in students:
        descending = sorted(students[st], reverse=True) # students[st] contains the s-scores
        students[st] = descending

    # begin parsing output for each division
    compCount = ""
    if len(baseURLs) == 1:
        compCount = "1 Competition"
    else:
        compCount = str(len(baseURLs)) + " Competitions"
    print("===== " + division + " Sums of Top 4 T-Scores After " + compCount + " =====")
    print("Rank\t" + "Name".ljust(24) + "Sum of Top 4 T-Scores")

    # there are 2 dicts: students (name:descending s-scores) and studentSums (name:sum of top 3 s-scores)
    # and a list to order the students in

    studentSums = {}
    topThreeRankings = []

    # put the sum of top 3 into the studentSums and into topThreeSum
    for stu in students:
        topThreeSum = sum(students[stu][0:4]) # students[stu] is already sorted descending
        studentSums.update({stu:topThreeSum})
        topThreeRankings.append(topThreeSum)

    # sort students by value of topThreeSum
    topThreeRankings = sorted(list(set(topThreeRankings)), reverse=True)
    # remove duplicates from topThreeRankings

    previousSum, accumulatedTies, tempHangingRank = 0,0,0
    inStreak = False

    # find the student(s) whose topThreeSum is this rank in the topThreeRankings
    # (order the students in the order of topThreeRankings)
    for rank in range(len(topThreeRankings)):
        for stud in students:
            if studentSums[stud] == topThreeRankings[rank]:
                
                # NOTE on ties: the above if stmt. keeps returning true w/o increasing counter as long as there are ppl with the same score
                # (*)this results in multiple ppl w/ same rank, but with no gaps in numbering (1 2 3 3 3 4 5 6 ...)
                # we may want everyone unique (1 2 3 4 5 ...) or we may want a tie rank order (1 2 3 3 3 6 7 8 ...)
                
                if topThreeRankings[rank] == previousSum:
                    # then this is a duplicate of the last one
                    if realTieSystem:
                        if not inStreak:
                            tempHangingRank = studentsSoFar # capture the current i.e. last student's rank throughout streak
                            inStreak = True
                    accumulatedTies += 1 # keeps the count running when "counter" is stuck dealing with tied and same-ranked ppl
                else:
                    # streak is over, update previousSum, reset variables
                    previousSum = topThreeRankings[rank]
                    inStreak = False
                    tempHangingRank = 0

                studentsSoFar = rank + 1 + accumulatedTies
                # combining the zero-indexed counter and the additional counting we do to deal with the tie situation (see comment (*))
                
                if realTieSystem:
                    # tie rank order mode (the rank jumps whenever streaks end, according to where it "should" be)
                    # identical to famat ranking system
                    if inStreak:
                        printedRank = str(tempHangingRank)
                    else:
                        printedRank = str(studentsSoFar)
                else:
                    # default mode (everybody gets a unique rank according to the number of people)
                    # useful for the latex graph since overlapping points look bad
                    printedRank = str(studentsSoFar)
                    
                score = str(round(topThreeRankings[rank], decimalPlaces))
                print(printedRank + "\t" + stud.ljust(24) + score)
        if rank + 1 + accumulatedTies == 30:
            break
    
    print("============================================================")

'''    # finally, append to the master list dictionary
    # if a student is in more than one division and we try to re-add, use the higher s-score and division
    # skip middle schoolers
    for stude in studentSums:
        if stude in middleSchoolers:
            continue
        elif stude in masterlist and masterlist[stude] > studentSums[stude]:
            continue
        else:
            masterlist.update({stude:studentSums[stude]})
            divisions.update({stude:division[0].lower()})
            # for latex purposes: define the division ID (first letter of div.) and create a new dictionary for student:ID
            # if the student's sum is overwritten by a higher one in another division, overwrite the division too

# print out the master list, in order, numbering each student
# to do this, add the anonymous sums to a new list, sort it, and match identities back in the loop
allSums = []
for studen in masterlist:
    allSums.append(masterlist[studen])
    
allSums = sorted(list(set(allSums)), reverse=True)
data = np.array(allSums[:numRows])

print()
print("===== All T-Scores as of " + date + " =====")

# find the student's name ("student") that goes with the scores arranged in order (looping through allSums by index)

previousSum, accumulatedTies, tempHangingRank = 0,0,0
inStreak = False

for counter in range(len(allSums)):
    for student in masterlist:
        if allSums[counter] == masterlist[student]:

            # NOTE on ties: the above if stmt. keeps returning true w/o increasing counter as long as there are ppl with the same score
            # (*)this results in multiple ppl w/ same rank, but with no gaps in numbering (1 2 3 3 3 4 5 6 ...)
            # we may want everyone unique (1 2 3 4 5 ...) or we may want a tie rank order (1 2 3 3 3 6 7 8 ...)
            
            if allSums[counter] == previousSum:
                # then this is a duplicate of the last one
                if realTieSystem:
                    if not inStreak:
                        tempHangingRank = studentsSoFar # capture the current i.e. last student's rank throughout streak
                        inStreak = True
                accumulatedTies += 1 # keeps the count running when "counter" is stuck dealing with tied and same-ranked ppl
            else:
                # streak is over, update previousSum, reset variables
                previousSum = allSums[counter]
                inStreak = False
                tempHangingRank = 0

            studentsSoFar = counter + 1 + accumulatedTies
            # combining the zero-indexed counter and the additional counting we do to deal with the tie situation (see comment (*))
            
            if realTieSystem:
                # tie rank order mode (the rank jumps whenever streaks end, according to where it "should" be)
                # identical to famat ranking system
                if inStreak:
                    rank = str(tempHangingRank)
                else:
                    rank = str(studentsSoFar)
            else:
                # default mode (everybody gets a unique rank according to the number of people)
                # useful for the latex graph since overlapping points look bad
                rank = str(studentsSoFar)
                
            score = str(round(allSums[counter], decimalPlaces))
            print(rank + "\t" + student.ljust(24) + score)
            
            # optional for latex code purposes:
                # table format is "[rank] & [name] & [sum] \\"
                # scatterplot format is "[rank] [sum] {[name]} [division letter]"
            score = fillZeroes(score, decimalPlaces)
            if (counter+1 <= numRows):
                tableData += "\t" + rank + " & " + student + " & " + score + " \\\\\n"
            plotData += "\t" + rank + " " + score + " {" + student + "} " + divisions[student] + "\n"
                
            #if counter+1 == 36:
                #print("===== Anyone below this line is not guaranteed to go to states =====")
            
###################################################

# LATEX code generation time

docHeader = "\
\\documentclass{article}\n\
\\usepackage[utf8]{inputenc}\n\
\\usepackage[margin=0.75in]{geometry}\n\
\\usepackage{pgfplots}\n\
\\usepackage{fancyhdr}\n\
\\pagestyle{fancy}\n\
\\lhead{\\textsc{S-Score Sums for States Qualification}}\n\
\\rhead{\\textsc{Mu Alpha Theta 2013-2014}}\n\
\n\
\\begin{document}"

docFooter = "\\end{document}"

tableHeader = "\
\\begin{table}\\begin{center}\n\
\\begin{tabular}{c l c}\n\
\t\\hline \\\\[-.8em]\n\
\t\\textbf{Rank} & \\textbf{Name} & \\textbf{S-Score Sum} \\\\[.2em]\n\
\t\\hline \\\\[-.8em]\n"

tableFooter = "\
\\hline\n\
\\end{tabular}\n\
\\caption{Sums of S-Scores of Top " + str(numRows) + " Competitors (as of " + date + ")}\n\
\\end{center}\\end{table}"

statsHeader = "\
\\begin{table}\\begin{center}\n\
\\begin{tabular}{c c c c c c c}\n\
    \t\\hline \\\\[-.8em]\n\
    \t\\textbf{Mean} & \\textbf{Std. Dev.} & \\textbf{Min.} & \\textbf{Q1} & \\textbf{Median} & \\textbf{Q3} & \\textbf{Max.} \\\\[.2em]\n\
    \t\\hline \\\\[-.8em]\n"

statsData = \
            "\t" + fillZeroes(round(np.mean(data), decimalPlaces), decimalPlaces) + \
            " & " + fillZeroes(round(np.std(data), decimalPlaces), decimalPlaces) + \
            " & " + fillZeroes(round(np.amin(data), decimalPlaces), decimalPlaces) + \
            " & " + fillZeroes(round(np.percentile(data, 25), decimalPlaces), decimalPlaces) + \
            " & " + fillZeroes(round(np.percentile(data, 50), decimalPlaces), decimalPlaces) + \
            " & " + fillZeroes(round(np.percentile(data, 75), decimalPlaces), decimalPlaces) + \
            " & " + fillZeroes(round(np.amax(data), decimalPlaces), decimalPlaces) + "\n"

statsFooter = "\
\\end{tabular}\n\
\\caption{Summary Statistics of Top " + str(numRows) + " S-Score Sums}\n\
\\end{center}\\end{table}"

plotHeader = "\
\\begin{figure}\\begin{center}\n\
\\begin{tikzpicture}\n\
\\begin{axis}[\n\
\theight=9in,\n\
\twidth=\\textwidth,\n\
\taxis lines=left,\n\
\txlabel={Rank},\n\
\tylabel={Sum of Top Three S-Scores},\n\
\tenlargelimits=false,\n\
\t%ymax=250,\n\
\tymajorgrids=true,\n\
\tgrid style=solid,\n\
\tlegend pos=north east,\n\
\tevery node near coord/.append style={\n\
\t\tfont=\\tiny,\n\
\t\trotate=30,\n\
\t\tanchor=195,},\n\
\tscatter/classes={\n\
\t\tg={red, mark=oplus},\n\
\t\ta={red, mark=*},\n\
\t\tp={blue, mark=*},\n\
\t\ts={green, mark=oplus},\n\
\t\tc={green, mark=*}\n\
\t},\n\
]\n\n\
\\addplot[scatter, only marks, point meta=explicit symbolic,\n\
\tvisualization depends on={value \\thisrow{name} \\as \\myvalue},\n\
\tnodes near coords*={\\myvalue}]\n\
\ttable [x=x, y=y, meta=color] {\n\
\tx y name color\n"

plotFooter = "\
\t};\n\
\t\\legend{Geometry, Algebra II, Precalculus, Statistics, Calculus}\n\
\\end{axis}\n\
\\end{tikzpicture}\n\
\\caption{Scatterplot of S-Score Sums vs. Rank}\n\
\\end{center}\\end{figure}"

print()
print("============================================================")
print("Note that this is a complete LATEX document. It requires the pgfplots and fancyhdr packages.")
print("===== LATEX code below this line =====")
print()
print(docHeader)
print()
print(tableHeader + tableData + tableFooter)
print()
print(statsHeader + statsData + statsFooter)
print()
print(plotHeader + plotData + plotFooter)
print()
print(docFooter)

# HUZZAH! MAY GRAND VICTORY BE IN AHS'S NEAR FUTURE
'''
