
import requests
import logging
import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to fetch all organizations that contain the enterprise name
def fetch_all_orgs(token):
    logging.info(f"Fetching organizations containing '{GITHUB_ENTERPRISE}'...")
    orgs = []
    url = "https://api.github.com/user/orgs"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    params = {"per_page": 100}

    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            # Filter organizations based on the enterprise name
            orgs.extend([org["login"] for org in response.json() if GITHUB_ENTERPRISE.lower() in org["login"].lower()])
            # Check for pagination
            url = response.links.get("next", {}).get("url")
        else:
            logging.error(f"Failed to fetch organizations: {response.status_code} - {response.text}")
            response.raise_for_status()

    logging.info(f"Fetched {len(orgs)} organizations containing '{GITHUB_ENTERPRISE}'.")
    return orgs

# Function to fetch all repositories for an organization
def fetch_all_repos(org, token):
    logging.info(f"Fetching all repositories for the organization: {org}...")
    repos = []
    url = f"https://api.github.com/orgs/{org}/repos"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    params = {"per_page": 100, "type": "all"}  # Fetch both public and private repositories

    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            repos.extend([repo["name"] for repo in response.json()])
            # Check for pagination
            url = response.links.get("next", {}).get("url")
        elif response.status_code == 403 and "SAML" in response.text:
            logging.error(f"SAML enforcement error for {org}. Please authorize your PAT.")
            return []  # Skip this organization
        else:
            logging.error(f"Failed to fetch repositories for {org}: {response.status_code} - {response.text}")
            response.raise_for_status()

    logging.info(f"Fetched {len(repos)} repositories for the organization: {org}.")
    return repos

# Function to save repositories to an Excel file in the specified format
def save_repos_to_excel(orgs_repos, output_file="enterprise_repositories.xlsx"):
    logging.info(f"Saving repositories to Excel file: {output_file}")
    # Create a dictionary where keys are organization names and values are lists of repositories
    data = {org: repos for org, repos in orgs_repos.items()}
    # Convert the dictionary to a DataFrame
    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in data.items()]))
    # Save to Excel
    df.to_excel(output_file, index=False)
    logging.info(f"Repositories saved to {output_file}")

def main():
    # Fetch all organizations containing the enterprise name
    orgs = fetch_all_orgs(GITHUB_PAT)

    # Fetch repositories for each organization
    orgs_repos = {}
    for org in orgs:
        repos = fetch_all_repos(org, GITHUB_PAT)
        orgs_repos[org] = repos

    # Save all repositories to an Excel file
    save_repos_to_excel(orgs_repos)

if __name__ == "__main__":
    main()
