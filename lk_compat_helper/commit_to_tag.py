#!/usr/bin/env python3
import argparse
from datetime import datetime
import logging
import os
import sys
from typing import Optional, Tuple

import github
from github import Github, GithubException  # type: ignore

logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(message)s")
logger = logging.getLogger("__main__")


class CLinuxKernelRepo:
    def __init__(self, token: str, commit: str):
        self.handle = Github(token)
        self.commit = commit
        self.commit_date: Optional[datetime] = None
        self.linux_kernel_repo = self.handle.get_repo("torvalds/linux")

    def _get_tags(self) -> Tuple[github.PaginatedList.PaginatedList, int]:  # pragma: no cover
        tags = self.linux_kernel_repo.get_tags()
        # totalCount: is a time consuming operation as it is a PaginatedList
        # and the property involves looping through pages.
        return (tags, tags.totalCount)

    def _get_commit(self) -> github.Commit.Commit:  # pragma: no cover
        return self.linux_kernel_repo.get_commit(sha=self.commit)

    def _get_tag(self) -> str:
        """
        Binary search the tags based on tag date and commit date, exclude release candidates (RCs).
        """
        tags, num_tags = self._get_tags()
        if not tags:
            logger.error("Failed to query tags")
            return "Unknown"

        start_tag_idx = 0
        end_tag_idx = num_tags
        tag_idx = (start_tag_idx + end_tag_idx) // 2
        while tag_idx and end_tag_idx - start_tag_idx != 1:
            tag = tags[tag_idx]
            tag_dt = tag.commit.commit.committer.date
            tag_dts_s = tag_dt.strftime("%y-%d-%mT%H:%M:%SZ")
            logger.debug(f"Checking {tag_idx}: {tag.name}, {tag.commit.commit.sha}, {tag_dts_s}")
            if self.commit_date:
                if tag_dt >= self.commit_date:
                    start_tag_idx = tag_idx
                    tag_idx = (start_tag_idx + end_tag_idx) // 2
                else:
                    end_tag_idx = tag_idx
                    tag_idx = (start_tag_idx + end_tag_idx) // 2

        found = False
        for tag_idx in range(start_tag_idx, end_tag_idx):
            tag = tags[tag_idx]
            tag_dt = tag.commit.commit.committer.date
            if tag_dt >= self.commit_date:
                found = True
                break

        # Skip RCs and Fetch the release
        while "rc" in tags[tag_idx].name:
            tag_idx -= 1
            if tag_idx < 0:
                return "Unknown"

        if not found and tag_idx == start_tag_idx and tag_dt < self.commit_date:
            return "Unmerged"

        return tags[tag_idx].name

    def get_commit_details(self) -> None:
        commit_details = self._get_commit()
        self.commit_date = commit_details.commit.committer.date
        logger.debug(f"Commit Date is {self.commit_date}")
        if self.commit_date is None:
            logger.error("Failed to query commit date, quit")
            sys.exit(1)

    def get_tag(self) -> str:
        self.get_commit_details()
        tag = self._get_tag()

        return tag


def main() -> None:  # pragma: no cover
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-a",
        "--api-token",
        required=False,
        default=os.environ.get("GITHUB_API_TOKEN"),
        type=str,
        help="Github API Access token, default: GITHUB_API_TOKEN environment variable",
    )

    parser.add_argument(
        "-c",
        "--commit",
        required=True,
        type=str,
        help="Commit to find the tag it first appeared in.",
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if args.api_token is None:
        logger.error("Please provide a Github API token")
        sys.exit(1)

    lkHandle = CLinuxKernelRepo(args.api_token, args.commit)

    try:
        tag = lkHandle.get_tag()
        logger.info(f"Earliest tag which has {args.commit} is {tag}")
        sys.exit(0)
    except GithubException as e:
        logger.error(e.status)
        logger.error(e.data["message"])
        sys.exit(2)


if __name__ == "__main__":  # pragma: no cover
    main()
