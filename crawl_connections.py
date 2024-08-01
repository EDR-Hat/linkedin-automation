from linkedin import *

#purpose of this script is to crawl your existing connections, save all seen profiles into a list
# and limit the number of connections sent out to a certain amount

if len(sys.argv) < 3:
    print('usage: {0} [directory path for saving information] [target limit of connections to send out] [[arg #1 for browser] [arg #2 for browser]]'.format(sys.argv[0]))
    exit(1)

path = sys.argv[1]

if not os.path.isdir(path):
    print('provided path {0} is not a valid path'.format(path))
    exit(2)

try:
    limit = int(sys.argv[2])
except:
    print('{2} was not an integer number!'.format(sys.argv[2]))
    exit(2)

if not os.path.isfile(path + 'connections.json'):
    print('no saved connection list!')
    exit(1)

if os.path.isfile(path + 'next_profiles.json'):
    f = open(path + 'next_profiles.json', 'r')
    encounters = set(json.load(f))
    f.close()
else:
    encounters = set()

if os.path.isfile(path + 'already_visited.json'):
    f = open(path + 'already_visited.json', 'r')
    visited = list(json.load(f))
    f.close()
else:
    visited = []

args = []
if len(sys.argv) > 3:
    for arg in sys.argv[3:]:
        args.append(arg)

b = setup_new_browser(path, args)
clicks = 0

conn = get_connections(path)

unvisited = [x for x in conn if x not in visited]

if len(unvisited) == 0:
    print('all connections in list have been visited')
    exit(3)

for href in unvisited:
    try:
        print('trying: ', href)
        info = connect_all_suggested_profiles(href, b)
        print(info)
    except Exception as e:
        print('connection attempt for {0} failed with error {1}'.format(href, e))
        continue
    encounters = encounters | info[1]
    clicks += info[0]
    if info[2]:
        print('hit weekly invitation limit, aborting early')
        break
    visited.append(href)
    if clicks >= limit:
        break

f = open(path + 'already_visited.json', 'w')
json.dump(list(visited), f)
f.close()

f = open(path + 'next_profiles.json', 'w')
json.dump(list(encounters), f)
f.close()

save_cookies(path, b)
b.close()
