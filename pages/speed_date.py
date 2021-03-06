from __future__ import print_function
import csv, re
from datetime import datetime

#
# Usage...
#   1. Export a csv file from the Google spreadsheet backing up the SME selection form.
#   2. Name the exported file `sme_choices.csv`
#   3. Edit `maxSlots = XXX` line in this python file for the number of slots (meeting times) you want
#   4. Run the command python speed_date.py > foo.md to produce a markdown file
#   5. Examine the markdown file for errors that you may need to patch up manually
#   6. Publish the markdown file as the schedule and include the starting times of each slot.
#
  
#
# Read the exported csv file named 'sme_choices.csv' from the Google
# form submission data
#
requests = []
with open('sme_choices.csv', mode ='r')as file:
    csvFile = csv.reader(file)
    for line in csvFile:
        if line[0] == 'Timestamp': # skip header line
           header = [re.sub('Select Priorities \[(.*) \((.*)\)\]',r'\1',x) for x in line]
           header_counts = [0] * len(header)
           continue
        line_time = datetime.strptime(line[0], '%m/%d/%Y %H:%M:%S')
        # time stamp ensures first-come, first served ordering
        time_id = abs((line_time - datetime(2021,8,10)).total_seconds())
        student_id = line[1]
        request = [time_id, student_id]
        for i in range(2,len(line)-2):
            if line[i]:
                request += [header[i]]
                header_counts[i] += 1
        requests += [request]

#
# Setup empty assignments
#
maxSlots = 4
assignments = {}
for req in requests:
    assignments[req[1]] = [True] * maxSlots

print('### Errors')

#
# Create empty schedule.
# Any SME's not at all selected?
#
schedule = {}
for i in range(2,len(header)-2):
    if header_counts[i] == 0:
        print('* ', header[i], 'has no selections')
    else:
        schedule[header[i]] = [''] * maxSlots

#
# Ensure requests are sorted by time of arrival
#
def requestTime(e):
    return e[0]
requests.sort(key=requestTime)

#
# Iterate over requests assigning first, then second
# and finally third priorities
#
for i in range(1,4):
    for req in requests:
        if len(req)-2 < i:
            continue
        student = req[1]
        sme = req[2+i-1]
        slot = 0
        while slot < maxSlots and \
            (assignments[student][slot] == False or \
            schedule[sme][slot] != ''):
            slot += 1
        if slot == maxSlots:
            print('* Unable to schedule student "%s" choice %d of "%s"'%(student,i,sme))
            continue
        if assignments[student][slot]:
            schedule[sme][slot] = student
            assignments[student][slot] = False
        else:
            print('* Slot not available for student "%s" choice %d of "%s"'%(student,i,sme))

#
# Output markdown for the schedule
#
print('\n\n### Schedule')
mdhdr = '|**SME**|' + ''.join(['**Slot %d**|'%i for i in range(maxSlots)])
mdhdr1 = '|:---|' + ''.join([':---:|' for i in range(maxSlots)])
print(mdhdr)
print(mdhdr1)
for item in schedule:
    print('|%s|'%item, end=' ')
    for student in schedule[item]:
       print('%s|'%student, end='')
    print('\n', end='')