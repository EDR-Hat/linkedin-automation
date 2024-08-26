from linkedin import *
import time

if len(sys.argv) < 3:
    print('usage: {0} [directory path for saving information] [number of seconds before script times out] [[arg #1 for browser] [arg #2 for browser]]'.format(sys.argv[0]))
    exit(1)

path = sys.argv[1]

try:
    sleep_time = int(sys.argv[2])
except:
    print('sleep time is not set to integer amount.')
    exit(1)

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
if len(sys.argv) > 3:
    for arg in sys.argv[3:]:
        args.append(arg)

def startup_new_browser():
    browser_startups = 30
    while True:
        try:
            b = setup_new_browser(path, args)
            break
        except Exception as e:
            if browser_startups == 0:
                print("browser couldn't startup properly", e)
                exit(1)
            print('hit browser setup error, trying again', e)
            browser_startups -= 1
    return b

start_time = time.time()

b = startup_new_browser()
b_time = time.time()
print('browser setup time:', time.time() - b_time)

job_list_startups = 20
while True:
    try:
        job_list = find_recent_jobs(path, b, -1)
        break
    except:
        if job_list_startups == 0:
            print('could not get job list')
            exit(1)
        job_list_startups -= 1
j_time = time.time()
print('joblist crawl time:', j_time - b_time)
b.quit()
b = startup_new_browser()
not_visited = [x for x in job_list if x.split('?')[0].split('/')[-2] not in applied]

for job in not_visited:
    try:
        apply_easy_job(b, job, bad_company, path)
    except Exception as e:
        print('browser problem with exception:', e)
        if str(e).lower().find('context discarded') != -1:
            try:
                b.quit()
            except:
                pass
            b = startup_new_browser()
    applied.add(job.split('?')[0].split('/')[-2])
    print('current runtime is:', time.time() - start_time)
    if time.time() - start_time >= sleep_time:
        print('quitting because time was up')
        break

f = open(path + 'already_applied.json', 'w')
json.dump(list(applied), f)
f.close()

save_cookies(path, b)
b.quit()
