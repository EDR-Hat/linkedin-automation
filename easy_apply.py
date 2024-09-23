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

def get_fresh_joblist(browser, terms_list, applied):
    all_jobs = []

    terms_used = 0

    for term in terms_list:
        job_list_startups = 20
        while True:
            try:
                job_list = find_recent_jobs(path, browser, -1, term)
                terms_used += 1
                break
            except:
                if job_list_startups == 0:
                    print('could not get job list')
                    exit(1)
                job_list_startups -= 1
        j_time = time.time()
        not_visited = [(x, term) for x in job_list if x[0].split('?')[0].split('/')[-2] not in applied]
        print(len(not_visited), ' unvisited job listings for term', term)
        all_jobs = all_jobs + not_visited
        if len(all_jobs) > 10:
            break
        terms_list.pop(0)
    print(len(all_jobs), ' total unvisited job listings')
    if len(all_jobs) == 0:
        b.close()
        b.quit()
        exit(0)
    return all_jobs, terms_used

def crawl_jobs(b, not_visited, bad_company, excluded_titles, path):
    for job in not_visited:
        skip = False
        for bad_title in excluded_titles:
            if job[0][1].lower().find(bad_title) != -1:
                print('excluding job', job, ' because of bad title', bad_title)
                skip = True
                break
        if skip:
            # should make a separate skipped jobs file
            applied.add(job[0][0].split('?')[0].split('/')[-2])
            continue
        
        success = None
        try:
            success = apply_easy_job(b, job[0][0], bad_company, path, search_term=job[1])
        except Exception as e:
            exception_jobs.add(job[0][0].split('?')[0].split('/')[-2])
            print('browser problem with exception:', e)
            try:
                b.close()
                b.quit()
            except:
                pass
            b = startup_new_browser()
            print('current runtime is:', time.time() - start_time)
            continue
        if success:
            applied.add(job[0][0].split('?')[0].split('/')[-2])
        else:
            error_jobs.add(job[0][0].split('?')[0].split('/')[-2])
        print('current runtime is:', time.time() - start_time)
        if time.time() - start_time >= sleep_time:
            print('quitting because time was up')
            break

    f = open(path + 'already_applied.json', 'w')
    json.dump(list(applied), f)
    f.close()

    f = open(path + 'error_jobs.json', 'w')
    json.dump(list(error_jobs), f)
    f.close()

    f = open(path + 'exception_jobs.json', 'w')
    json.dump(list(exception_jobs), f)
    f.close()


start_time = time.time()

search_terms = ['software%20engineer', 'software%20developer', 'software%20test%20engineer', 'automation%20engineer',  'database%20administrator', 'application%20developer', 'application%20engineer', 'data%20analyst', 'python%20programmer', 'computer%20programmer', 'linux%20engineer', 'systems%20administrator', 'sysadmin', 'software%20quality%20assurance', 'site%20reliability%20engineer', 'devops%20engineer', 'cybersecurity%20engineer', 'systems%20analyst',  'systems%20engineer', 'software%20qa%20specialist', 'software%20quality%20assurance%20specialist',  'qa%20engineer','quality%20assurance%20engineer', 'mobile%20app%20developer', 'game%20developer', 'web%20developer',  'software%20test%20engineer','application%20developer', 'junior%20engineer']

while time.time() - start_time <= (sleep_time * 0.75) and len(search_terms) > 0:
    print('entering main whlie loop')
    if os.path.isfile(path + 'already_applied.json'):
        f = open(path + 'already_applied.json', 'r')
        applied = set(json.load(f))
        f.close()
    else:
        applied = set()


    if os.path.isfile(path + 'error_jobs.json'):
        f = open(path + 'error_jobs.json', 'r')
        error_jobs = set(json.load(f))
        f.close()
    else:
        error_jobs = set()

    if os.path.isfile(path + 'exception_jobs.json'):
        f = open(path + 'exception_jobs.json', 'r')
        exception_jobs = set(json.load(f))
        f.close()
    else:
        exception_jobs = set()
    prev_jobs = applied | exception_jobs | error_jobs

    if os.path.isfile(path + 'excluded_titles.json'):
        f = open(path + 'excluded_titles.json', 'r')
        excluded_titles = set(json.load(f))
        f.close()
    else:
        excluded_titles = set()


    b = startup_new_browser()
    not_visited, drops = get_fresh_joblist(b, search_terms, prev_jobs)
    crawl_jobs(b, not_visited, bad_company, excluded_titles, path)
    print('time ratio', time.time() - start_time, sleep_time * 0.75 )
    b.close()
    b.quit()
    for x in range(drops):
        if len(search_terms) > 0:
            search_terms.pop(0)
