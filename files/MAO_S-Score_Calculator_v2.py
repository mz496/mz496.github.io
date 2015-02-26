# S-Score Calculator for AHS MAO
# Version 1: March 01, 2014
# Version 2: May 23, 2014
# Matthew Zhu

import math
import numpy as np
import urllib.request
from bs4 import BeautifulSoup

###################################################
# this searches for specified spelling errors and merges the wrong name's s-scores under the correct name
# format: CORRECT spelling : INCORRECT spelling
# need title case
corrections = {"Barath Tirumala":"Barath Triumala", "Couper Leo":"Cooper Leo", "Zheng Zhao":"Zhang Zhao"}
    
# the list of people removed from consideration for states
# need title case
middleSchoolers = ["Max Ranis", "Azzara Nincevic", "Nithya Kasarla", "Kishan Patel"]

# change the school name if desired, for funsies
# name must be exactly as appears on famat.org
school = "American Heritage (Plantation)"

# for output of all s-scores at the end "as of ..."
date = "March Regional, 3/1/2014"

# decimal places to calculate to throughout output+program
decimalPlaces = 4

# number of people (top X) to analyze for latex output; usually limited by the number of rows that can fit in the table
# 45 works well
numRows = 45

# format: use any of the URLs for a comp, e.g. Sweepstakes, and remove e.g. "Sweeps.html" and leave the /
# http:// required
baseURLs = [
"http://floridamao.org/Downloadable/Results/Tampa%20Bay%20Tech%20January%20Statewide%202014/",
"http://floridamao.org/Downloadable/Results/Combined01182014/",
"http://floridamao.org/Downloadable/Results/Combined02012014/",
"http://floridamao.org/Downloadable/Results/February%20Statewide%20at%20Coral%20Glades%20HS/",
"http://floridamao.org/Downloadable/Results/Combined03012014/"]

###################################################

''' DEFUNCT: because built-in python functions stole my thunder
# some cute functions for parsing output
def hangingIndent(string, space):
    # string is a str, space is an int, how many characters of space there are
    tabs = math.ceil((space-len(string))/8)
    result = string
    for k in range(tabs):
        result = result + "\t"
    return result
'''

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

''' DEFUNCT: because it's just easier to add the URLs into the code and run
# in case you ever want to add your urls custom-ly
baseURLs = []
sweepsURL = input("Enter the URL of the Sweepstakes results for a (statewide or combined regional) competition to analyze: ")
while sweepsURL == "": # if some derp decides to leave it blank the first time
    sweepsURL = input("Enter the URL: ")

while sweepsURL != "": # once we have something
    # all division URLs have the form http://floridamao.org/Downloadable/Results/(competition name)/(division name)_Indv.html
    slashes = [slashInd for slashInd in range(len(sweepsURL)) if sweepsURL[slashInd] == "/"]
    # cut the URL after the 6th slash (similar technique used later), append division+"_Indv.html"
    baseURL = sweepsURL[:slashes[5]+1]
    baseURLs.append(baseURL)
    sweepsURL = input("Any more competition URLs? Leave blank and press enter if the answer is \"no.\" ")
'''

masterlist = {}
divisions = {}
tableData = ""
plotData = ""

# we wrap the divisions on the outside because we want to do each competition for one division at a time
for division in ["Geometry", "Algebra 2", "Precalculus", "Calculus", "Statistics"]:
    students = {}
    for cutURL in baseURLs:
        URL = cutURL + urllib.request.quote(division + "_Indv.html")
        # ^idk how this works but some part of it has to be quoted, and some cutURLs break when quoted

        page = urllib.request.urlopen(URL).read()
        soup = BeautifulSoup(page)
        cells = soup.find_all("td") # get a list of all <td> tags (table cells)
        cellText = []
        for tag in cells:
            cellText.append(str(tag)) # convert to string for manipulation

        # order of tags is (place), (school), (name), (score), (famat id), (right), (wrong), (blank), (tscore)
        # 10th place celltext at index 90 (1st place celltext at index 9, 2nd place at 18, ..., "10th" at 90)
        # failsafe against ties where 10th/25th doesn't actually exist in the html
        tenthPlace = cellText[9*10 + 3]
        twentyFifthPlace = cellText[9*25 + 3]
        tenthScore = int(tenthPlace[4:-5]) # cut off the <td>, </td>
        twentyFifthScore = int(twentyFifthPlace[4:-5])

        # list comp to get indices of all occurrences of school name
        indices = [ind for ind in range(len(cellText)) if cellText[ind] == "<td>" + school + "</td>"]

        for i in range(len(indices)):
            # indices[i]+1 is the position of the student's name, +2 is score
            studentName = cellText[indices[i]+1][4:-5].title() # cut tags, standardize to upper
            studentScore = int(cellText[indices[i]+2][4:-5])
            sScore = 5*(studentScore - twentyFifthScore)/(tenthScore - twentyFifthScore + 1) + 70 # formula!!
            if studentName in students:
                students[studentName].append(sScore)
            else:
                students.update({studentName:[]}) # create a list for scores and append a new one at each comp
                students[studentName].append(sScore)

        # people are duplicated when they have the same s-score, so delete one copy
        for s in students:
            students[s]=students[s]
            # magic happens

    # at this point we have students={name:[s-scores...],name:[s-scores...]...}

    # correct for spelling errors
    # locate the correct version and add the s-score list of the incorrect version to the correct version
    for correctVer in corrections:
        if corrections[correctVer] not in students: # corrections[correctVer] is the incorrect name
            continue # if there is no error
        else:
            if correctVer in students: # if a known correct version exists
                students[correctVer] += students[corrections[correctVer]] # merge the s-score lists
                del students[corrections[correctVer]] # delete the incorrect one
            else:
                # if we know a spelling is wrong, even though no correct one exists
                # then we make a correct entry just in case later correct entries come along
                students.update({correctVer:students[corrections[correctVer]]})
                # add a new dict entry named correctly using the incorrect version's value(s)
                del students[corrections[correctVer]] # delete the incorrect one
    
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
    print("===== " + division + " S-score Results After " + compCount + " =====")
    print("Name".ljust(20), "Sum of Top 3 S-Scores".ljust(24), "All S-Scores")

    # there are 2 dicts: students (name:descending s-scores) and studentSums (name:sum of top 3 s-scores)
    # and a list to order the students in

    studentSums = {}
    topThreeRankings = []

    # put the sum of top 3 into the studentSums and into topThreeSum
    for stu in students:
        # can't use the competition count because can't guarantee all students went
        if len(students[stu]) >= 3:
            topThreeSum = students[stu][0] + students[stu][1] + students[stu][2] # already sorted descending
            studentSums.update({stu:topThreeSum})
        else:
            topThreeSum = sum(students[stu])
            studentSums.update({stu:topThreeSum})
        topThreeRankings.append(topThreeSum)

    # sort students by value of topThreeSum
    topThreeRankings = sorted(topThreeRankings, reverse=True)

    # find the student whose topThreeSum is this rank in the topThreeRankings
    # (order the students in the order of topThreeRankings)
    for rank in range(len(topThreeRankings)):
        for stud in students:
            if studentSums[stud] == topThreeRankings[rank]:
                # print name, the sum, then the list
                print(stud.ljust(20), str(round(studentSums[stud], decimalPlaces)).ljust(24), str(roundList(students[stud], decimalPlaces)))
    print("============================================================")

    # finally, append to the master list dictionary
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
    
allSums = sorted(allSums, reverse=True)
data = np.array(allSums[:numRows])

print()
print("===== All S-Scores as of " + date + " =====")
# fix the counter and scan through masterlist
# the student's index in the master rankings
# also the ranking-1 when converting to natural numbers

for counter in range(len(allSums)):
    for student in masterlist:
        # match masterlist[student] value to allSums[counter]
        if allSums[counter] == masterlist[student]:

            rank = str(counter + 1)
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
