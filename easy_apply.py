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

job_list_startups = 20
while True:
    try:
        job_list = find_recent_jobs(path, b)
        break
    except:
        if job_list_startups == 0:
            print('could not get job list')
            exit(1)
        job_list_startups -= 1

not_visited = [x for x in job_list if x.split('?')[0].split('/')[-2] not in applied]

for job in not_visited:
    try:
        success = apply_easy_job(b, job, excluded_companies)
    except Exception as e:
        print(e)
        success = False
    if success:
        applied.add(job.split('?')[0].split('/')[-2])

f = open(path + 'already_applied.json', 'w')
json.dump(list(applied), f)
f.close()

save_cookies(path, b)
b.close()
