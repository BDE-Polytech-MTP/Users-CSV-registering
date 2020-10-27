import csv
import pathlib
import requests
import sys
import time
from optparse import OptionParser


def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def find_headers_indexes(header, firstname_column, lastname_column, email_column, member_column):
    try:
        firstname_index = header.index(firstname_column)
    except ValueError:
        firstname_index = None
        print("Can't find firstname column with name %s. Skipping (not mandatory) ..." % firstname_column)

    try:
        lastname_index = header.index(lastname_column)
    except ValueError:
        lastname_index = None
        print("Can't find lastname column with name %s. Skipping (not mandatory) ..." % lastname_column)

    try:
        member_index = header.index(member_column)
    except ValueError:
        member_index = None
        print("Can't find member column with name %s. Skipping (not mandatory) ..." % member_column)

    try:
        email_index = header.index(email_column)
    except ValueError:
        email_index = None
        print_err("Unable to find email column with name %s. Exiting." % email_column)
        exit(1)

    return firstname_index, lastname_index, email_index, member_index


def send_api_request(opts, email, firstname, lastname, member):
    time.sleep(opts.wait / 1000)
    request_result = requests.post(opts.api, json={
        "email": email,
        "bde": opts.bde,
        "firstname": firstname,
        "lastname": lastname,
        "member": member
    }, headers={
        "Authorization": opts.token
    })

    if request_result.status_code == 201:
        print("User: %s, %s, %s, %s registered with success" % (email, firstname, lastname, member))
    elif request_result.status_code == 500:
        print_err("Server internal error. Canceling script.")
        print_err("Concerned user: %s, %s, %s, %s" % (email, lastname, firstname, member))
        exit(1)
    elif request_result.status_code == 404:
        print_err("Got a 404. Is the API URL correct ? Exiting.")
        exit(1)
    elif request_result.status_code == 400:
        print_err("Invalid request for : %s, %s, %s, %s" % (email, firstname, lastname, member))
        print_err("Error: %s" % request_result.content.decode(encoding='UTF-8'))
    else:
        print("\n\nGot error code %d for user : %s, %s, %s, %s" %
              (request_result.status_code, email, firstname, lastname, member))
        print("Body: %s\n\n" % request_result.content.decode(encoding='UTF-8'))


def handle_user_line(opts, line_num, user_line, firstname_index, lastname_index, email_index, member_index):
    firstname = user_line[firstname_index] if firstname_index is not None and len(user_line) > firstname_index else ""
    lastname = user_line[lastname_index] if lastname_index is not None and len(user_line) > lastname_index else ""
    email = user_line[email_index] if len(user_line) > email_index else ""
    member = bool(
        user_line[member_index] if member_index is not None and len(user_line) > member_index else opts.member_default
    )

    if len(email) == 0:
        print("Skipping line %d, can't find email." % line_num)
    elif opts.dry:
        print("Register user: %s, %s, %s, %s --- POST %s" % (email, firstname, lastname, member, opts.api))
    else:
        send_api_request(opts, email, firstname, lastname, member)


def create_users(creation_parameters):
    path = pathlib.Path(creation_parameters.filename)
    if not path.is_file():
        print_err("Specified filename is not a file")
        exit(1)

    with open(creation_parameters.filename, encoding="UTF-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=creation_parameters.delimiter)
        firstname_index = None
        lastname_index = None
        email_index = None
        for line in csv_reader:
            if csv_reader.line_num == 1:
                firstname_index, lastname_index, email_index, member_index = find_headers_indexes(
                    line, creation_parameters.firstname_column, creation_parameters.lastname_column,
                    creation_parameters.email_column, creation_parameters.member_column)
            elif csv_reader.line_num - 1 >= creation_parameters.skip:
                handle_user_line(creation_parameters, csv_reader.line_num, line, firstname_index,
                                 lastname_index, email_index, member_index)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename", help="file to get users from (required)", metavar="FILE")
    parser.add_option("-t", "--token", help="A valid token to authenticate to web service (required)", dest="token")
    parser.add_option("--bde", help="BDE UUID to register users to (required)", dest="bde")
    parser.add_option("--api", help="API url where to POST data [default: %default]", dest="api",
                      default="https://bde-polytech-mtp.herokuapp.com/users/unregistered")
    parser.add_option("--email", help="name of the email column [default: %default]",
                      default="email", dest="email_column")
    parser.add_option("--firstname", help="name of the firstname column [default: %default]",
                      default="firstname", dest="firstname_column")
    parser.add_option("--lastname", help="name of the lastname column [default: %default]",
                      default="lastname", dest="lastname_column")
    parser.add_option("--member", help="name of the member column [default: %default]",
                      default="member", dest="member_column")
    parser.add_option("--skip", help="Skip the N first lines of the CSV file", type=int,
                      dest="skip", default=0, metavar="N")
    parser.add_option("-d", "--delimiter", help="columns delimiter [default: %default]", dest="delimiter", default=",")
    parser.add_option("-w", "--wait", help="Minimum time, in milliseconds, between two requests",
                      dest="wait", type=int, default=0)
    parser.add_option("--dry", help="Execute as a dry-run (does not really call API)", dest="dry", default=False,
                      action="store_true")
    parser.add_option("--member-default", help="Indicates if users should be members by default", dest="member_default",
                      action="store_true", default=False)

    (options, args) = parser.parse_args()

    errored = False
    if options.filename is None:
        errored = True
        print_err("You must specify a filename to parse users from")
    if options.token is None:
        errored = True
        print_err("You must specify a token to authenticate to the service")
    if options.skip < 0:
        errored = True
        print_err("You can't skip a negative number of lines")
    if options.bde is None:
        errored = True
        print_err("You must provide a BDE UUID")
    if options.wait < 0:
        errored = True
        print_err("You can't specify a value lower than 0 for the wait option")

    if errored:
        parser.print_help()
        exit(1)
    else:
        create_users(options)
