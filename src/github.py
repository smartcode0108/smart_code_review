import requests


class GitHubAPI:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "Ollama-Code-Review-Bot",
            "Accept": "application/vnd.github.v3+json",
        }

    def make_request(self, method, path, data=None, additional_headers=None):
        url = f"{self.base_url}{path}"
        headers = self.headers.copy()
        if additional_headers:
            headers.update(additional_headers)

        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PATCH":
                response = requests.patch(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            if response.status_code >= 200 and response.status_code < 300:
                try:
                    return response.json()
                except ValueError:
                    return response.text
            else:
                raise Exception(
                    f"GitHub API request failed: {response.status_code} - {response.text}"
                )
        except requests.RequestException as e:
            raise Exception(f"Error making request to GitHub API: {e}")

    def get_pull_request(self, owner, repo, pr_number):
        path = f"/repos/{owner}/{repo}/pulls/{pr_number}"
        return self.make_request("GET", path)

    def create_review_comment(self, owner, repo, pr_number, commit_id, path, position, body):
        try:
            if not path or position is None:
                raise ValueError("Invalid path or position for inline comment.")

            review_path = f"/repos/{owner}/{repo}/pulls/{pr_number}/comments"
            return self.make_request(
                "POST",
                review_path,
                {
                    "body": body,
                    "commit_id": commit_id,
                    "path": path,
                    "position": position,
                    "side": "RIGHT",
                },
            )
        except ValueError as ve:
            print(f"Skipping invalid inline comment: {ve}")
            return None
        except Exception as error:
            print(f"Error creating review comment: {error}")
            raise error
    def post_comment(self, owner, repo, pr_number, body):
        path = f"/repos/{owner}/{repo}/issues/{pr_number}/comments"
        return self.make_request("POST", path, {"body": body})

    def create_review(self, owner, repo, pr_number, comments, body):
        path = f"/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        return self.make_request(
            "POST",
            path,
            {
                "body": body,
                "event": "COMMENT",
                "comments": comments,
            },
        )

    def get_pull_request_diff(self, owner, repo, pr_number):
        path = f"/repos/{owner}/{repo}/pulls/{pr_number}"
        additional_headers = {"Accept": "application/vnd.github.v3.diff"}
        return self.make_request("GET", path, additional_headers=additional_headers)

    def update_review_comment(self, owner, repo, comment_id, body):
        path = f"/repos/{owner}/{repo}/pulls/comments/{comment_id}"
        return self.make_request("PATCH", path, {"body": body})

    def get_existing_comments(self, owner, repo, pr_number):
        path = f"/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        return self.make_request("GET", path)
    
    def genaral_comment_to_pr(self, repo_owner, repo_name, pr_number, comment_body):
        """
        Posts a comment on the specified pull request.

        Args:
            repo_owner (str): The owner of the repository.
            repo_name (str): The name of the repository.
            pr_number (int): The pull request number.
            comment_body (str): The content of the comment.

        Returns:
            dict: The response from the GitHub API.
        """
        if not comment_body.strip():
            print("Comment body is empty. Skipping posting the comment.")
            return

        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/issues/{pr_number}/comments"
        data = {"body": comment_body}

        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code != 201:
            raise Exception(f"Failed to post comment: {response.status_code} - {response.text}")
        print("Comment posted successfully.")
        return response.json()