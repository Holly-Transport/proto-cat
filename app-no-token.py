import streamlit as st
import requests
import random
from datetime import datetime
import pandas as pd

# Constant for WorldBank organization
ORG_NAME = "worldbank"
GITHUB_API_URL = f"https://api.github.com/orgs/{ORG_NAME}/repos"

def get_all_repositories():
    """Fetch all repositories from the WorldBank organization."""
    repos = []
    page = 1
    while True:
        response = requests.get(GITHUB_API_URL, params={"page": page, "per_page": 100})
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
    image_id = random.randint(1, 1000)
    return f"https://picsum.photos/seed/{image_id}/100/100"

def format_date(date_str):
    """Convert ISO 8601 date to MM/YYYY format."""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return date_obj.strftime("%m/%Y")
    except Exception:
        return "Unknown"

def apply_filters(repos):
    """Apply all filters from sidebar and return filtered repositories."""
    df = pd.DataFrame(repos)
    
    # Sidebar filters
    st.sidebar.header("Filter Repositories")
    
    # Clear filters button
    if st.sidebar.button("Clear All Filters"):
        st.session_state.keyword = ""
        st.session_state.min_stars = 0
        st.session_state.min_forks = 0
        st.session_state.selected_languages = []
        st.session_state.has_url = "All"
        st.rerun()
    
    # Initialize session state for filters if not exists
    if 'keyword' not in st.session_state:
        st.session_state.keyword = ""
    if 'min_stars' not in st.session_state:
        st.session_state.min_stars = 0
    if 'min_forks' not in st.session_state:
        st.session_state.min_forks = 0
    if 'selected_languages' not in st.session_state:
        st.session_state.selected_languages = []
    if 'has_url' not in st.session_state:
        st.session_state.has_url = "All"
    
    # Keyword search
    st.session_state.keyword = st.sidebar.text_input("Search by keyword", value=st.session_state.keyword)
    if st.session_state.keyword:
        mask = (
            df['name'].str.contains(st.session_state.keyword, case=False, na=False) |
            df['description'].str.contains(st.session_state.keyword, case=False, na=False)
        )
        df = df[mask]
    
    # Stars filter
    st.session_state.min_stars = st.sidebar.number_input(
        "Minimum Stars",
        min_value=0,
        value=st.session_state.min_stars
    )
    if st.session_state.min_stars > 0:
        df = df[df['stargazers_count'] >= st.session_state.min_stars]
    
    # Forks filter
    st.session_state.min_forks = st.sidebar.number_input(
        "Minimum Forks",
        min_value=0,
        value=st.session_state.min_forks
    )
    if st.session_state.min_forks > 0:
        df = df[df['forks_count'] >= st.session_state.min_forks]
    
    # Language filter
    languages = sorted(df['language'].dropna().unique())
    st.session_state.selected_languages = st.sidebar.multiselect(
        "Programming Language",
        languages,
        default=st.session_state.selected_languages
    )
    if st.session_state.selected_languages:
        df = df[df['language'].isin(st.session_state.selected_languages)]
    
    # URL filter
    st.session_state.has_url = st.sidebar.radio(
        "Has Project URL",
        ["All", "Yes", "No"],
        index=["All", "Yes", "No"].index(st.session_state.has_url)
    )
    if st.session_state.has_url == "Yes":
        df = df[df['homepage'].notna() & (df['homepage'] != "")]
    elif st.session_state.has_url == "No":
        df = df[df['homepage'].isna() | (df['homepage'] == "")]
    
    return df.to_dict('records')

def main():
    st.title("code.partnership.org")
    
    st.write("Browsing World Bank's public GitHub repositories, as an example")
    
    with st.spinner("Fetching repositories..."):
        repos = get_all_repositories()
    
    if repos:
        # Sort repositories by stars (desc) and then by date (most recent first)
        repos = sorted(repos, key=lambda x: (x['stargazers_count'], x['updated_at']), reverse=True)
        
        # Apply filters and get filtered repos
        filtered_repos = apply_filters(repos)
        
        # Display total count
        st.write(f"**Found {len(filtered_repos)} repositories matching your criteria**")
        
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
            st.write("No repositories found matching your filters.")

if __name__ == "__main__":
    main()
