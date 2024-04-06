import csv, random, datetime
from time import sleep

import smtplib, ssl
from email.message import EmailMessage


THIS_YEAR = str(datetime.date.today().year) # Current year for storing

participant_fname = 'j_names.txt' # Participant info
last_year_matches_fname = 'j_last_year_matches.txt' # Exclude last year's matches
all_year_matches_fname = 'j_all_year_matches.txt' # Log all years' matches

TEST_RUN = True # Performs a test when true and does not send to all users
SEND_TEST = True # Send a test email if TEST_RUN is True

email_username = '' # Your sending email username here
email_password = '' # Your sending email password here
email_smtp = 'smtp.mail.yahoo.com'
test_email_address = '' # Your test email address here
tester_name = '' # Name of tester here (to insert into test email)

##Participants file is comma-delimited, in following format:
## Name,full_email_address,exclusion1|exclusion2|exclusion3,<repeat for person2>

## If there are no exclusions, can be left blank (comma is still needed) 

## Class for participant
## Includes name, email, and exclusions (cannot be matched with participant)
class person:
    def __init__(self, name, email, exclude):
        self.name = name
        self.email = email
        self.exclude = exclude

    def out(self):
        print(f'Name: {self.name}\nEmail: {self.email}\nExclude: {self.exclude}\n')
        

## Read in people
people = []

with open(participant_fname) as f:
    reader = list(csv.reader(f, delimiter=','))[0]
    i = 0
    while i < len(reader):
        people.append(person(reader[i], reader[i+1], reader[i+2].split('|')))
        i += 3

## Randomize the matching        
random.shuffle(people)


## Set up dict to exclude last year's matches
last_year_matches = {}

with open(last_year_matches_fname) as f:
    reader = list(csv.reader(f, delimiter=','))[0]
    i = 0
    while i < len(reader):
        last_year_matches[reader[i]] = reader[i+1]
        i += 2


## Match up participants
matches = []
## Keep list of names matched
given = []

i = 0
j = 1
while len(matches) < len(people) and i < len(people):
    ## Break if cannot complete
    broken = False
    skip = False
    while (people[i].name in people[j].exclude or
           people[i].name == people[j].name or
           people[j].name in given or
           last_year_matches[people[i].name] == people[j].name): ## Last year exclusions
        
        if j < len(people) - 1:
            j += 1
            
        else:
            if not broken:
                broken = True
                j = 0
            else:
                skip = True
                break

    if not skip:
        matches.append((people[i], people[j])) # append tuple of (recipient,match)
        given.append(people[j].name) # append matched name

    
    if len(matches) < len(people):
        if i < (len(people) - 1):
            i += 1
        else:
            print('Matching failed. Reshuffling...')
            random.shuffle(people)
            matches = []
            given = []
            i = 0
            j = 1
        

## Function to email matches
def email(match):
    port = 465  # For SSL
    smtp_server = email_smtp
    username = email_username
    password = email_password
    receiver_name = match[0].name
    receiver_email = match[0].email
    gift_recipient = match[1].name

    message = op_message(receiver_name, gift_recipient) #or k_message

    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = f'{receiver_name}\'s Secret Santa Name'
    msg['From'] = username
    msg['To'] = receiver_email

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(username, password)
        server.send_message(msg)

## Message text
def op_message(receiver_name, gift_recipient):
    return f"""Greetings {receiver_name}!

Come all come one,
it's time for fun,
'cuz Secret Santa's here!

So draw your name --
that is the game --
and give the gift of cheer (or beer)!

You will be {gift_recipient}'s Secret Santa this year.

Have a merry Christmas!
    
-Kris
"""


## Alternate kids' Secret Santa text
def k_message(receiver_name, gift_recipient):
    return f"""Greetings {receiver_name}!


C'mon, you Christmas Hooligan
it's time to spread some cheer!
So draw your name to do again
that thing we do each year!


You are {gift_recipient}'s Secret Santa this Christmas -- make it a good one!


-Kris"""


def test_email(match=None, matches=None):
    port = 465  # For SSL
    smtp_server = email_smtp
    username = email_username
    password = email_password
    receiver_name = tester_name
    receiver_email = test_email_address
    gift_recipient = 'All'

    message = test_email_message(matches)

    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = 'Your Secret Santa Test List'
    msg['From'] = username
    msg['To'] = receiver_email

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(username, password)
        server.send_message(msg)


def test(match):
    print(f'Emailing {match[0].name} at {match[0].email} {match[1].name}\'s name')


def test_email_message(matches):
    message = ""
    i = 1
    for match in matches:
        message += f'{i}) Emailing {match[0].name} at {match[0].email} {match[1].name}\'s name\n'
        i += 1
    return message


def run(test_run=True, send_test=True, matches=matches):

    ## If not a test, send email to each participant
    if test_run == False:
        matches_str = ''
        
        for m in matches:
            email(m)
            sleep(2)
            matches_str += m[0].name + ',' + m[1].name + ','

        matches_str = matches_str[:-1] + '\n' ## Trim unnecessary trailing comma
                                              ## Assumes at least one pair

        with open(last_year_matches_fname, "w") as f:
            f.write(matches_str)

        with open(all_year_matches_fname, "a") as f:
            f.write(THIS_YEAR + '\n' + matches_str)

    ## If it's a test, create a string of all matches instead        
    else:
        matches_str = ''
        
        for m in matches:
            test(m)
            matches_str += m[0].name + ',' + m[1].name + ','

        matches_str = matches_str[:-1] + '\n' ## Trim unnecessary trailing comma
                                              ## Assumes at least one pair

        with open(last_year_matches_fname, "w") as f:
            f.write(matches_str)

        with open(all_year_matches_fname, "a") as f:
            f.write(THIS_YEAR + '\n' + matches_str)
            
        if send_test == True:
            test_email(None, matches)

run(test_run=TEST_RUN, send_test=SEND_TEST)

