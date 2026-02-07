#!/usr/bin/env python

import os
import sys
import csv
import time

from math import ceil
from argparse import ArgumentParser

from github import Github, GithubException, Auth
from urllib3 import Retry


def starred_repos(user, delay=1.0):
    """Fetch starred repos with rate limiting to avoid GitHub API limits.
    
    Args:
        user: GitHub user object
        delay: Seconds to wait between page requests (default: 1.0)
    """
    starred = user.get_starred()
    total_pages = ceil(starred.totalCount / 30)

    for page_num in range(0, total_pages):
        # Add delay between page requests to avoid rate limiting
        if page_num > 0:
            time.sleep(delay)
        
        for repo in starred.get_page(page_num):
            yield repo


def config_retry(backoff_factor=1.0, total=8):
    """urllib3 will sleep for:
        {backoff factor} * (2 ** ({number of total retries} - 1))

    Recalculates and Overrides Retry.DEFAULT_BACKOFF_MAX"""
    Retry.DEFAULT_BACKOFF_MAX = backoff_factor * 2 ** (total - 1)
    return Retry(total=total, backoff_factor=backoff_factor)


def parse_args():
    parser = ArgumentParser(description="export a GitHub user's starred repositorys to CSV")
    parser.add_argument("--user")
    parser.add_argument("--github-token")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between API requests in seconds (default: 1.0)")
    return parser.parse_args()


def main():
    args = parse_args()
    user = args.user or os.environ.get("GH_USER")
    if not user:
        print("Please set `--user` or GH_USER environment variable to a valid GitHub user name.", file=sys.stderr)
        exit(1)

    if args.github_token:
        auth = Auth.Token(args.github_token)
        gh = Github(auth=auth, retry=config_retry())
    else:
        gh = Github(retry=config_retry())
    
    try:
        user = gh.get_user(user)
    except GithubException as e:
        if e.status == 403 and "rate limit" in str(e.data).lower():
            print("\nError: GitHub API rate limit exceeded.", file=sys.stderr)
            print("\nOptions:", file=sys.stderr)
            print("  1. Wait an hour and try again", file=sys.stderr)
            print("  2. Use a GitHub token for higher rate limits:", file=sys.stderr)
            print("     GH_USER=defunkt uv run export_stars.py --github-token YOUR_TOKEN > stars.csv", file=sys.stderr)
            print("\nTo create a token: https://github.com/settings/tokens", file=sys.stderr)
            exit(1)
        raise

    writer = csv.writer(sys.stdout)

    # Use a small delay to avoid hitting GitHub's unauthenticated rate limit (60 requests/hour)
    # With 30 repos per page and delay between pages, we stay well under the limit
    try:
        for repo in starred_repos(user, delay=args.delay):
            writer.writerow((repo.html_url, repo.description))
    except GithubException as e:
        if e.status == 403 and "rate limit" in str(e.data).lower():
            print("\nError: GitHub API rate limit exceeded.", file=sys.stderr)
            print("\nOptions:", file=sys.stderr)
            print("  1. Wait an hour and try again", file=sys.stderr)
            print("  2. Use a GitHub token for higher rate limits:", file=sys.stderr)
            print("     GH_USER=defunkt uv run export_stars.py --github-token YOUR_TOKEN > stars.csv", file=sys.stderr)
            print("\nTo create a token: https://github.com/settings/tokens", file=sys.stderr)
            exit(1)
        raise


if __name__ == "__main__":
    main()