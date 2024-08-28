from linkedin import *


if len(sys.argv) < 2:
    print('usage: {0} [directory path for saving information] [[arg #1 for browser] [arg #2 for browser]]'.format(sys.argv[0]))
    exit(1)

path = sys.argv[1]

if not os.path.isdir(path):
    print('provided path {0} is not a valid path'.format(path))
    exit(2)

if os.path.isfile(path + 'already_applied.json'):
    f = open(path + 'already_applied.json', 'r')
    applied = set(json.load(f))
    f.close()
else:
    applied = set()

#a set of manually added company urls that you do not want to send in future applications to
#use this to exclude companies that come up as scam consulting firms etc
if os.path.isfile(path + 'excluded_companies.json'):
    f = open(path + 'excluded_companies.json', 'r')
    bad_company = set(json.load(f))
    f.close()
else:
    bad_company = set()

args = []
if len(sys.argv) > 2:
    for arg in sys.argv[2:]:
        args.append(arg)

browser_startups = 30
while True:
    try:
        b = setup_new_browser(path, args)
        break
    except:
        if browser_startups == 0:
            print("browser couldn't startup properly")
            exit(1)
        print('hit browser setup error, trying again')
        browser_startups -= 1

while True:
    job = input('enter a job test url')
    try:
        success = apply_easy_job(b, job, bad_company, path,  pause=True)
    except Exception as e:
        print(e)
    skip = input('exit?')
    if skip == 'Y':
        exit(0)

b.close()
