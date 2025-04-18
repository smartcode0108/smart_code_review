import requests


class GitHubAPI:
    def __init__(self, token):
        """
        **Docstring:**


        # Get GitHub repository information
        def get_repo_info(self):
            \"\"\"
            Gets GitHub repository information.

            Args:
                self: The object instance.

            Returns:
                dict: GitHub repository information.
        """
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "Ollama-Code-Review-Bot",
            "Accept": "application/vnd.github.v3+json",
        }

    def make_request(self, method, path, data=None, additional_headers=None):
        """
        ## Summary

        Sends a request to the GitHub API using the specified HTTP method.

        ## Args:

        - `method` (str): HTTP method to use (e.g., "GET", "POST", "PATCH").
        - `url` (str): GitHub API endpoint.
        - `additional_headers` (dict): Additional headers to include in the request.
        - `data` (dict): Data to send in the request body (only used for POST, PATCH methods).

        ## Returns:

        - dict: Parsed JSON response if successful.
        - str: Text response if successful (if unable to parse JSON).
        - Exception: In case of request errors or GitHub API errors.
        """
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
        """
        ## GET Request Function

        Returns the result of a GET request to the specified path.

        Args:
            path (str): The path to send the request to.

        Returns:
            dict: The JSON response from the server.
        """
        path = f"/repos/{owner}/{repo}/pulls/{pr_number}"
        return self.make_request("GET", path)

    def create_review_comment(
        self, owner, repo, pr_number, commit_id, path, position, body
    ):
        """
        Summary line.

        Args:
            path (str): Path to the file for the inline comment.
            position (int): Position within the file for the inline comment.

        Returns:
            dict or None: Response object or None if an error occurred.
        """
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
        """
        ## Summary

        Send a POST request to the specified path with the given body.

        ## Args

        - path (str): The path to send the request to.
        - body (dict): The body of the request.

        ## Returns

        - dict: The response from the server.
        """
        path = f"/repos/{owner}/{repo}/issues/{pr_number}/comments"
        return self.make_request("POST", path, {"body": body})

    def create_review(self, owner, repo, pr_number, comments, body):
        """
        Summary line.

        Args:
            path (str): path.
            body (str): body.
            comments (str): comments.

        Returns:
            str: request.
        """
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
        """
        Summary: Makes a GET request to the GitHub API endpoint.

        Args:
            path (str): The path to the GitHub API endpoint.

        Returns:
            dict: The response from the GitHub API.
        """
        path = f"/repos/{owner}/{repo}/pulls/{pr_number}"
        additional_headers = {"Accept": "application/vnd.github.v3.diff"}
        return self.make_request("GET", path, additional_headers=additional_headers)

    def update_review_comment(self, owner, repo, comment_id, body):
        """
        ## Summary: Send a PATCH request to the specified path with the given body.

        ## Args:
            path (str): The path to send the request to.
            body (dict): The body of the request.

        ## Returns:
            dict: The response from the server.
        """
        path = f"/repos/{owner}/{repo}/pulls/comments/{comment_id}"
        return self.make_request("PATCH", path, {"body": body})

    def get_existing_comments(self, owner, repo, pr_number):
        """
        ## Summary line.

        ## Args:
            path (str): The API endpoint to request.

        ## Returns:
            Response object: The API response object.
        """
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
            raise Exception(
                f"Failed to post comment: {response.status_code} - {response.text}"
            )
        print("Comment posted successfully.")
        return response.json()
