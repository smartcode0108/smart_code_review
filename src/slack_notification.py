import os
import requests
import urllib3
import json
from slack_client import SlackClient
# Disabling warnings from urllib3
urllib3.disable_warnings()

with open('config.json') as f:
    config = json.load(f)


GITHUB_HOST = config['github']['host']
GITHUB_USER = config['github']['user']
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


SLACK_REVIEW_CHANNEL = "abp-test"
# Get the project
# Class for interacting with GitHub REST API

class GitRestClient:
    """
    Class for interacting with the GitHub using REST API.
    """
    # URL templates for listing branches and pull requests
    LIST_BRANCHES = "repos/{org}/{repo}/branches?per_page=100"
    LIST_PRS = "repos/{org}/{repo}/pulls?per_page=100"
    LIST_MERGED_PRS = "repos/{org}/{repo}/pulls?state=closed&sort=updated&direction=desc"

    GET_PR = "repos/{org}/{repo}/pulls/{pr_num}"
    ADD_REVIEWERS = "repos/{org}/{repo}/pulls/{pr_num}/requested_reviewers"
    CREATE_PR = "repos/{org}/{repo}/pulls/"
    SET_PR_STATE = "repos/{}/{}/pulls/{}"

    def __init__(self, hostname, username, token):
        """
        Initialize the GitRestClient with the given hostname, username, and token.
        Also sets the organization to 'vplex' and prepares the headers for requests.
        Args:
            hostname (str): The hostname of the GitHub server.
            username (str): The username for the GitHub account.
            token (str): The personal access token for the GitHub account.
        """
        self.hostname = hostname
        self.org = "smartcode0108"
        self.username = username
        self.token = token
        self.headers = {'Authorization': f'token {token}'}

    def create_url(self, url_template, repo, **kwargs):
        """
        Create a URL for the given repository using the specified URL template.
        Args:
            url_template (str): The URL template for the API endpoint.
            repo (str): The name of the repository.
        Returns:
            str: The URL for the given repository using the specified template.
        """
        _url = f'https://{self.hostname}/{url_template.format(org=self.org, repo=repo, **kwargs)}'
        print(_url)
        return _url

    def send(self, method, url, body=None):
        """
        Sends a request to the specified URL using the given HTTP method.

        Args:
            method (str): The HTTP method to use. Valid options are "get" and "post".
            url (str): The URL to send the request to.
            body (dict, optional): The request body to send. Only applicable for "post" requests.

        Returns:
            requests.Response: The response object returned by the request.

        Raises:
            ValueError: If the HTTP method is not "get" or "post
        """
        resp = None
        if method == "get":
            resp = requests.get(url, headers=self.headers, verify=False)
        elif method == "post":
            json_str = json.dumps(body)
            resp = requests.post(url, headers=self.headers, data=json_str, verify=False)
        else:
            raise ValueError(f"Invalid HTTP method: {method}")
        return resp

    def get_branches(self, repo):
        """
        Get a list of branches for the given repository.
        Args:
            repo (str): The name of the repository.
        Returns:
            list: A list of branch names for the given repository.
        """
        _url = self.create_url(self.LIST_BRANCHES, repo)
        resp = self.send("get", _url)
        return resp.json()

    def get_prs(self, repo):
        """
        Get a list of pull requests for the given repository.
        Args:
            repo (str): The name of the repository.
        Returns:
            list: A list of pull requests for the given repository.
        """
        url = self.create_url(self.LIST_PRS, repo)
        response = self.send("get", url)
        return response.json()

    def get_merged_prs(self, repo):
        """
        Get a list of pull requests for the given repository.
        Args:
            repo (str): The name of the repository.
        Returns:
            list: A list of pull requests for the given repository.
        """
        url = self.create_url(self.LIST_MERGED_PRS, repo)
        response = self.send("get", url)
        return response.json()

    def get_pr(self, repo, pr_num):
        """
        Get a list of pull requests for the given repository.
        Args:
            repo (str): The name of the repository.
            pr_num (int): The name of the repository.
        Returns:
            list: A list of pull requests for the given repository.
        """
        url = self.create_url(self.GET_PR, repo, pr_num=pr_num)
        response = self.send("get", url)
        return response.json()

    def add_reviewers(self, repo, pr_num, reviewers):
        """
        Add reviewers to a pull request.
        Args:
            org (str): The organization that owns the repository.
            repo (str): The name of the repository.
            pr_num (int): The number of the pull request.
            reviewers (list): A list of usernames to add as reviewers.
        """
        # Prepare the URL and headers
        url = self.create_url(self.ADD_REVIEWERS, repo, pr_num=pr_num)

        headers = {'Authorization': f'token {GITHUB_TOKEN}'}

        # Prepare the data
        data = {'reviewers': reviewers}

        # Send the request
        response = self.send("post", url, body=data)

        # Check the response
        if response.status_code == 201:
            print(f"Successfully added reviewers to PR #{pr_num}.")
        else:
            print(
                f"Failed to add reviewers to PR #{pr_num}. Status code: {response.status_code}, Response: {response.text}")

    def get_pr_branches(self, repo):
        """
        Get a list of branches associated with pull requests for the given repository.
        Args:
            repo (str): The name of the repository.
        Returns:
            list: A list of branch names associated with pull requests for the given repository.
        """
        prs = self.get_prs(repo)
        branches = []
        for pr in prs:
            branches.append("origin/" + pr['head']['ref'])
        return branches

    def set_pr_state(self, repo, pr_num, state):
        """
        Set the state of a pull request.
        Args:
            org (str): The organization that owns the repository.
            repo (str): The name of the repository.
            pr_num (int): The number of the pull request.
            state (str): The state to set the pull request to.
        """

        url = self.create_url(self.SET_PR_STATE, repo, pr_num=pr_num)
        headers = {'Authorization': f'token {GITHUB_TOKEN}'}
        data = json.dumps({'state': state})
        response = requests.patch(url, headers=headers, data=data, verify=False)
        return response.status_code == 200

    def set_reviewers(self, repo, pr_num, review_profile):
        """
        Set the reviewers for a pull request in the specified GitHub repository.

        Args:
            repo (str): The name of the repository.
            pr_num (int): The number of the pull request.
            review_profile (str): review_profile. options are ds_team, ds_team_imp".

        Raises:
            ValueError: If the review_profile is not one of the expected values.

        Returns:
            None
        """

        team_users = [
            'tiwaryshobhit', 'Itsmeonlinetoday', 'Vojjala-Shivani']
        high_imp = ['Itsmeonlinetoday']
        profile = {"ds_team": team_users, "ds_team_imp": team_users + high_imp}
        if review_profile not in profile.keys():
            raise ValueError("Invalid profile %s, available profiles: ds_team, ds_team_imp" % review_profile)

        self.add_reviewers(repo, pr_num, profile[review_profile])
        print("pr: ", json.dumps(self.get_pr(repo, pr_num), indent=2))
        url = f"https://github.com/smartcode0108/{repo}/pull/{pr_num}"
        text = """hi @channel
Please review  %s""" % url
        self.send_slack_notification(text)

    def send_slack_notification(self, message):
        """
        Send a message to a Slack channel.
        Args:
            message (str): The message to send.
        """
        client = SlackClient("Mind Peer PR")
        client.send_message(SLACK_REVIEW_CHANNEL, message)
    project = "namespace/project"

    # Get the source and target branches
    source_branch = "your-feature-branch"
    target_branch = "master"

    def create_pr(self, repo, source_branch, target_branch, title, description):

        # Create the merge request
        data = {
            "title": title,
            "body": description,
            "head": target_branch,
            "base": source_branch
        }
        url = self.create_url(self.CREATE_PR, repo)
        print(data)
        print(self.headers)
        headers = {'Authorization': f'token {GITHUB_TOKEN}'}
        response = requests.patch(url, headers=self.headers, data=data, verify=False)
        print(response.status_code)
        # Check the response
        if response.status_code == 201:
            print("Merge request created successfully.")
            print(f"Merge request URL: {response.json()['html_url']}")
        else:
            print("Failed to create merge request.")
            print(f"Response: {response.text}")

    # Example usage:
    @staticmethod
    def input_repository_name():
        """
        Since we are using only one repository (smart_code_review),
        directly return the repository name and take PR number input.
        """
        repository_name = "smart_code_review"
        print(f"Using repository: {repository_name}")

        pr_number = int(input("Enter the PR number: "))

        print(f"The PR number is: {pr_number}")
        print(f"The repository is: {repository_name}")
        return repository_name, pr_number 


    @classmethod
    def test(cls):
        """
        Test method for the GitRestClient class.
        """
        print("test")

        client = GitRestClient(GITHUB_HOST, GITHUB_USER, GITHUB_TOKEN)
        repo, pr_num = client.input_repository_name()
        client.set_reviewers(repo, pr_num, "ds_team")


if __name__ == "__main__":
    # Running the test method if the script is run directly
    GitRestClient.test()
