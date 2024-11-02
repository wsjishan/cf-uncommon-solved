import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl

class TLSAdapter(HTTPAdapter):
    """A custom adapter to force TLS version 1.2."""
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

session = requests.Session()
session.mount("https://", TLSAdapter())

def get_solved_problems(handle):
    """Fetch solved problems for a given Codeforces handle."""
    url = f'https://codeforces.com/api/user.status?handle={handle}'
    try:
        response = session.get(url, verify=False)  # Disable SSL verification
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {handle}: {e}")
        return None

    submissions = response.json()
    if submissions['status'] != 'OK':
        print(f"Error in response for {handle}.")
        return None

    # Extract unique solved problem IDs
    solved_problems = set()
    for submission in submissions['result']:
        if submission['verdict'] == 'OK':
            problem = submission['problem']
            problem_id = f"{problem['contestId']}-{problem['index']}"
            solved_problems.add(problem_id)

    return solved_problems

def find_uncommon_solved(handle1, handle2):
    """Find and save the uncommon solved problems for two users."""
    solved1 = get_solved_problems(handle1)
    solved2 = get_solved_problems(handle2)

    if solved1 is None or solved2 is None:
        print("Error in fetching problems. Check handles or API connectivity.")
        return

    # Calculate uncommon solved problems (exclusive to each user)
    only_user1 = solved1 - solved2  # Problems only solved by handle1
    only_user2 = solved2 - solved1  # Problems only solved by handle2

    # Write results to a text file with links
    with open("uncommon_problems.txt", "w") as file:
        file.write(f"Problems only {handle1} solved ({len(only_user1)}):\n")
        for problem in sorted(only_user1):
            link = f"https://codeforces.com/problemset/problem/{problem.replace('-', '/')}"
            file.write(f"{problem} - {link}\n")

        file.write(f"\nProblems only {handle2} solved ({len(only_user2)}):\n")
        for problem in sorted(only_user2):
            link = f"https://codeforces.com/problemset/problem/{problem.replace('-', '/')}"
            file.write(f"{problem} - {link}\n")

    print(f"Uncommon problems have been saved to 'uncommon_problems.txt'.")

# Take handles as input from the user
handle1 = input("Enter the first Codeforces handle: ")
handle2 = input("Enter the second Codeforces handle: ")

find_uncommon_solved(handle1, handle2)