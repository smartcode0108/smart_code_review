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

    def create_review_comment(self, owner, repo, pr_number, commit_id, path, line, body):
        try:
            pr = self.get_pull_request(owner, repo, pr_number)
            head_sha = pr["head"]["sha"]

            review_path = f"/repos/{owner}/{repo}/pulls/{pr_number}/comments"
            return self.make_request(
                "POST",
                review_path,
                {
                    "body": body,
                    "commit_id": head_sha,
                    "path": path,
                    "position": line,
                    "side": "RIGHT",
                },
            )
        except Exception as error:
            if "position" in str(error):
                print("Retrying comment creation without position parameter...")
                review_path = f"/repos/{owner}/{repo}/pulls/{pr_number}/comments"
                return self.make_request(
                    "POST",
                    review_path,
                    {
                        "body": body,
                        "commit_id": head_sha,
                        "path": path,
                        "line": line,
                        "side": "RIGHT",
                    },
                )
            print("Error creating review comment:", error)
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