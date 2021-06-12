# linux-kernel-compat-helper
Linux kernel compatibility helper to add version guards for an out-of-tree modules or to get the tag information for a particular commit.

# Introduction
For maintaining an out-of-tree module it is important to support multiple kernel version compatibility
using Linux kernel version guards, we can get the exact commit for the fix by using `git blame` or `git bisect` etc, but the main problem is to figure out the version number which the fix
is present first.

## The problem statement

### Clone Linus's `linux.git`

If you have clone Linus tovarlds [`linux.git`](git://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git)
then we can use below command to figure out the tag in which the commit first appeared. But cloning this repo
and keeping it up-to-date is inconvinient.

```
$ git describe --contains <commit_sha>
```

## Solution

### Github Linus's `linux.git`
This repo is kept up-to-date and we can use the Github API to query commits and tags without cloning the repo and maintaining it. This module uses this approach and does a simple binary search based on commit and tag date.

# Usage
## Prerequisites
* Github API token with proper permissions
* `pipenv` installed
* Tested on Ubuntu Distribution, but should work in others.

## Running
* Create and Install the virtual environment
    - `pipenv install`

* Run the application, below command will display the usage.
    - `pipenv run lk-get-tag -h`

## Example commands
```
$ export GITHUB_API_TOKEN=<token>
$ pipenv install
$ pipenv run lk-get-tag -c <commit_sha>
```