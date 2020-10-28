# Users CSV registering

This little script allows to register multiple users from a given CSV file.
It parses the CSV to extract users and send a POST request to the endpoint which
is responsible of creating users.

# Install

This need script needs few dependencies. To install these dependencies
juste run `pip install -r requirements.txt`.

# Usage

```
Usage: register-users.py [options]

Options:
  -h, --help            show this help message and exit
  -f FILE, --file=FILE  file to get users from (required)
  -t TOKEN, --token=TOKEN
                        A valid token to authenticate to web service
                        (required)
  --bde=BDE             BDE UUID to register users to (required)
  --api=API             API url where to POST data [default: https://bde-
                        polytech-mtp.herokuapp.com/users/unregistered]
  --email=EMAIL_COLUMN  name of the email column [default: email]
  --firstname=FIRSTNAME_COLUMN
                        name of the firstname column [default: firstname]
  --lastname=LASTNAME_COLUMN
                        name of the lastname column [default: lastname]
  --member=MEMBER_COLUMN
                        name of the member column [default: member]
  --skip=N              Skip the N first lines of the CSV file
  -d DELIMITER, --delimiter=DELIMITER
                        columns delimiter [default: ,]
  -w WAIT, --wait=WAIT  Minimum time, in milliseconds, between two requests
  --dry                 Execute as a dry-run (does not really call API)
  --member-default      Indicates if users should be members by default

```