from linkedin import *

#purpose of this script is to initate or update a connections list

if len(sys.argv) < 2:
    print('usage: {0} [directory path for saving information]'.format(sys.argv[0]))
    exit(1)

path = sys.argv[1]

if not os.path.isdir(path):
    print('provided path {0} is not a valid path'.format(path))
    exit(2)

b = setup_new_browser(path)

if os.path.isfile(path + 'connections.json'):
    update_connections(path, b)
else:
    conn = scrape_current_connections(b)
    save_connections(path, conn)

save_cookies(path, b)
b.close()
