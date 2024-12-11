import streamlit as st
import requests
import random
from datetime import datetime

# GitHub API base URL
GITHUB_API_URL = "https://api.github.com"

# Access the GitHub API token from Streamlit secrets
GITHUB_API_TOKEN = st.secrets["GITHUB_API_TOKEN"]
HEADERS = {"Authorization": f"token {GITHUB_API_TOKEN}"}

def get_all_repositories(org_name):
    """Fetch all repositories of the specified organization."""
    url = f"{GITHUB_API_URL}/orgs/{org_name}/repos"
    repos = []
    page = 1
    while True:
        response = requests.get(url, headers=HEADERS, params={"page": page, "per_page": 100})
        if response.status_code == 200:
            batch = response.json()
            if not batch:
                break
            repos.extend(batch)
            page += 1
        else:
            st.error(f"Failed to fetch repositories. Status code: {response.status_code} - {response.json().get('message', 'Unknown error')}")
            break
    return repos

def generate_random_image_url():
    """Generate a placeholder image URL."""
    image_id = random.randint(1, 1000)  # Example for generating random image identifiers
    return f"https://picsum.photos/seed/{image_id}/100/100"

def format_date(date_str):
    """Convert ISO 8601 date to MM/YYYY format."""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return date_obj.strftime("%m/%Y")
    except Exception:
        return "Unknown"

def main():
    st.title("Prototype for Discussion: code.worldbank.org")

    # Organization selector
    # org_name = st.selectbox("Select GitHub Organization:", ["worldbank", "datapartnership"], index=0)
    # st.write(f"Browsing repositories for the organization: **{org_name}**")

    # Default organization
    org_name = "worldbank"
    st.write(f"Browsing repositories for the organization: **{org_name}**")

    with st.spinner("Fetching repositories..."):
        repos = get_all_repositories(org_name)

    if repos:
        # Sort repositories by stars (desc) and then by date (most recent first)
        repos = sorted(repos, key=lambda x: (x['stargazers_count'], x['updated_at']), reverse=True)

        # Search functionality
        search_query = st.text_input("Search for a repository:", placeholder="Type repository name or description...")

        # Filter repositories
        if search_query:
            filtered_repos = [
                repo for repo in repos
                if search_query.lower() in repo['name'].lower() or (repo.get('description') and search_query.lower() in repo['description'].lower())
            ]
        else:
            filtered_repos = repos

        # Display repositories
        st.subheader("Repositories")
        if filtered_repos:
            for repo in filtered_repos:
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.image(generate_random_image_url(), caption="", use_container_width=True)
                with col2:
                    st.markdown(f"### [{repo['name']}]({repo['html_url']})")
                    st.write(repo.get('description', 'No description available'))
                    if repo.get('homepage'):
                        st.markdown(f"[Visit Project Site]({repo['homepage']})")
                st.write(f"⭐ Stars: {repo['stargazers_count']} | Last Updated: {format_date(repo['updated_at'])}")
                st.markdown("---")
        else:
            st.write("No repositories found matching your query.")

if __name__ == "__main__":
    main()


