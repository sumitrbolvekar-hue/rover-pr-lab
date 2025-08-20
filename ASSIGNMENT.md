# Git Lab Assignment: Kestrel-1 Rover, Review and Merge

**Course:** 26RA2308 Git for Software Development and Collaboration
**Builds on:** Experiments 1 to 10. **Based on:** Experiment 11 (Pull Request Workflow)
**Time allowed:** 1 hour. **Marks:** 100

---

## The story

The Kestrel-1 rover team has grown, and nobody pushes straight to `main` any more: **every change goes through a pull request**,
so that a teammate can read it before it is merged. You are the team's new maintainer. This morning you set up the rules and
follow three changes through the whole cycle. The lab has one rule:

> **`main` is always working. Work happens on a branch, and a pull request is how it gets to `main`.**

In the next hour you plan the work with **issues** (labels, a milestone), open a **pull request** that closes an issue, leave a
**review comment** and answer it with one more commit, merge three pull requests in the three different ways GitHub offers
(**squash**, **merge commit**, **rebase**) and compare the history each one leaves, add a `CONTRIBUTING.md`, and **protect
`main`** so that a direct push is refused. You reuse `git switch -c`, `git push -u` and `git pull` (Experiments 7 and 9), `git log
--graph` (Experiment 8), the heredoc `cat > file << 'EOF'` of Experiment 4 and the Conventional Commits of Experiment 5.

## What you need

`git`, `python3`, a free **GitHub account** with your SSH key added (Experiment 3: `ssh -T git@github.com` must greet you by name; if
it does not, do the section "Before the lab" of Experiment 10's handout or `connect_git_and_github.docx`), and the **GitHub CLI,
`gh`**, logged in. If your terminal does not print English messages, run `export LC_ALL=C` first, because the grader reads what Git
and `gh` print. If a long output opens in a pager (a screen with `:` or `(END)` at the bottom), press `q` to leave it.

## Before the lab: install and log in to the GitHub CLI (once)

`gh` lets you open pull requests, merge them and manage issues from the terminal. Check whether you have it:

```bash
gh --version
```

If it says `command not found`, install it: **macOS** `brew install gh`; **Windows** `winget install --id GitHub.cli` (then open a new
Git Bash); **Ubuntu** follow the five-line `apt` instructions on `https://github.com/cli/cli/blob/trunk/docs/install_linux.md`.
Then log in once:

```bash
gh auth login
```

Answer: **GitHub.com**, **SSH** (it offers your existing key), **Login with a web browser**. Copy the one-time code it prints, press
`Enter`, paste the code in the browser page that opens, and confirm. Check:

```bash
gh auth status
```

It must say `Logged in to github.com account <your user name>`.

## Rules

1. Work **only inside your clone** `rover-pr-lab`. Push **only to `origin`**, your own GitHub repository. Never use `--force`.
2. Make your repository **Public** when you create it (Task 1). GitHub's free plan protects branches only in public repositories.
3. Type the commands yourself. The grader checks that your pasted output matches what is really in your repository (your commit
   numbers, your issue and pull request numbers, your user name), so output copied from a classmate is detected.
4. Keep the branch names, titles, commit messages and file contents exactly as written. Your pull requests and issues get **their own
   numbers** from GitHub; the handout uses the numbers 1 to 5 because that is what you get when you do the tasks in order.
5. A pull request normally needs **a second person** to approve it, and GitHub does not let you approve or request changes on your
   own pull request. This lab therefore asks you for a **comment** review only. If you have a partner, review each other's pull
   request with `--approve` too, as an extra: nothing in the grader depends on it.

## How you hand in your work

1. In Task 1 you copy `submission/outputs.template.txt` to `submission/outputs.txt`.
2. After **each step** (numbered **1.1**, **1.2**, ...), paste what the terminal printed under the matching `--- N.M` line of
   `submission/outputs.txt`, replacing `(paste output here)`. Do not edit or delete the `=== TASK` and `--- N.M` lines. Type your
   answers after the colon of the `ANSWER-n :` lines (the line just below each `# Qn` question).
3. Fill in your name and registration number at the top of the file.
4. Run the automatic grader whenever you want to see where you stand:

   ```bash
   python3 tests/grade.py
   ```

   It prints **PASS** or **FAIL** for every task, tells you exactly which check failed, and shows your score out of 100. The grader
   never uses the internet: it reads your clone and what you pasted.
5. When you are done, show the final grader output to your instructor (it is also saved in `submission/results.txt`), and submit
   `submission/outputs.txt` as instructed. The file is not pushed to GitHub on purpose: `.gitignore` keeps it local.

## Time plan

| Task | Time on the clock | Topic | Suggested time | Marks |
|---|---|---|---|---|
| 1 | 09:00 | Connect and plan the work | 12 min | 20 |
| 2 | 09:12 | Open a pull request | 14 min | 25 |
| 3 | 09:26 | Three ways to merge | 14 min | 25 |
| 4 | 09:40 | The contributing guide and the closed issue | 5 min | 15 |
| 5 | 09:45 | Protect main | 6 min | 15 |
| | | Buffer for running the grader and fixing mistakes | 9 min | |

**Skipped a task, or running behind?** You do not lose the rest of the lab. A **catch-up box** at the start of the next task
brings your clone and your GitHub repository to the state you need, in a few lines. If you skipped several tasks, run their boxes in
order. You lose only the marks of the task you skipped.

---

## Task 1: Connect and plan the work (20 marks)

Get the project, give it a home of your own on GitHub, and plan the work as two issues.

```bash
cd ~
git clone https://github.com/qbit-glitch/26RA2308-gitlab-11-rover-pr-lab.git rover-pr-lab
cd rover-pr-lab
cp submission/outputs.template.txt submission/outputs.txt
git config user.name "Your Full Name"
git config user.email "your-email@example.com"
git remote rename origin upstream
```

Use your own real name and e-mail (not the placeholders, and not one of the teammates'). Do **not** use `--global` here. The clone's
`origin` points at the **course** repository; renaming it to `upstream` frees the name `origin` for **your own** repository.

Now, in the browser: sign in to github.com, click **New repository**, call it `rover-pr-lab`, choose **Public**, leave everything
else empty (**no** README, **no** .gitignore, **no** license) and click **Create repository**. Copy its SSH address. Then, back in
the terminal (replace `YOUR-USERNAME` with your GitHub user name):

```bash
git remote add origin git@github.com:YOUR-USERNAME/rover-pr-lab.git
git push -u origin main
```

* **1.1** Paste the output of `git push -u origin main`. `* [new branch]` means GitHub did not have `main` yet; `-u` links your
  local `main` to `origin/main`.

```bash
gh auth status
```

* **1.2** Paste the output. It shows which GitHub account `gh` acts as: it must be the owner of the repository you just made.

An **issue** is a unit of work. A **label** classifies it, an **assignee** takes responsibility, and a **milestone** groups issues
towards a deliverable. First make the milestone (there is nothing to paste for it; GitHub answers with a block of JSON), then the two
issues. `{owner}` and `{repo}` are filled in by `gh`: type them exactly like that.

```bash
gh api repos/{owner}/{repo}/milestones -f title="v1.0 Release"
```

```bash
gh issue create --title "Add obstacle detection unit tests" --body "The detector has no tests. Add pytest tests." --label enhancement --assignee @me --milestone "v1.0 Release"
```

* **1.3** Paste the output. The last line is the address of your issue: its number is **1**.

```bash
gh issue create --title "Update README installation section" --body "The README has no usage section." --label documentation --milestone "v1.0 Release"
```

* **1.4** Paste the output. This is issue number **2**.

```bash
gh issue list
```

* **1.5** Paste the output: your two open issues with their labels, newest first.
* Then type your answer to `ANSWER-1` in the file (there is no pasted output for it): a pull request whose description says
  `Closes #2` closes issue 2 when it is merged. Which word is that? (Write it as shown, one word.)

## Task 2: Open a pull request (25 marks)

Issue 2 asks for a Usage section in the README. Do it on a branch, open a pull request, leave a review comment as the reviewer, and
answer it as the author.

*Needs:* the repository and the issues of Task 1.

> **Catch-up box: only if you skipped Task 1.** Make your repository on GitHub as described in Task 1 (the browser part, and the
> `git remote add origin ...` line). Then run these four lines, once. They do what Task 1 does. If you did Task 1, do **not** run
> them. There is nothing to paste for them, and you lose only the marks of Task 1.
>
> ```bash
> git push -u origin main
> gh api repos/{owner}/{repo}/milestones -f title="v1.0 Release"
> gh issue create --title "Add obstacle detection unit tests" --body "The detector has no tests. Add pytest tests." --label enhancement --assignee @me --milestone "v1.0 Release"
> gh issue create --title "Update README installation section" --body "The README has no usage section." --label documentation --milestone "v1.0 Release"
> ```

Make the branch and add the section. There is nothing to paste for these two lines. The section contains a typo in a link
(`instal.md`): that is deliberate, and the review will find it.

```bash
git switch -c feature/readme-usage
cat >> README.md << 'EOF'

## Usage

Install the requirements first (see [the install guide](docs/instal.md)), then run:

    python3 src/controller.py
EOF
```

```bash
git commit -am "docs: add usage instructions to readme"
```

* **2.1** Paste the output of `git commit`. Note the branch name in square brackets.

```bash
git push -u origin feature/readme-usage
```

* **2.2** Paste the output. GitHub answers with a hint: `Create a pull request for 'feature/readme-usage' ...`. That is the web
  way to open a pull request (the **Compare & pull request** button). Here you use the terminal.

```bash
gh pr create --base main --head feature/readme-usage --title "docs: add usage instructions to readme" --body "Adds a Usage section. Closes #2"
```

* **2.3** Paste the output. The last line is the address of your pull request. `--base` is the branch it should be merged **into**,
  `--head` is the branch with the work. Its number is **3**: issues and pull requests share one counter.

```bash
gh pr list
```

* **2.4** Paste the output: your open pull request, its title and its branch.

Now be the reviewer. A review comment says what is wrong without blocking anything:

```bash
gh pr review feature/readme-usage --comment --body "Please fix the broken link"
```

* **2.5** Paste the output.

Now be the author again. Fix the typo (`instal.md` to `install.md`) by retyping the whole README, and push the new commit to the
**same branch**. There is nothing to paste for the first block.

```bash
cat > README.md << 'EOF'
# Kestrel-1 rover

Control and vision code for the Kestrel-1 rover.

See [the installation notes](docs/install.md) to set up a laptop.

## Usage

Install the requirements first (see [the install guide](docs/install.md)), then run:

    python3 src/controller.py
EOF
```

```bash
git commit -am "docs: fix broken link in usage section"
```

* **2.6** Paste the output of `git commit`.

```bash
git push
```

* **2.7** Paste the output. The pull request needs no action from you: the new commit simply joins it. (A plain `git push` is enough
  because `-u` linked the branch in step 2.2.)

```bash
gh pr view feature/readme-usage
```

* **2.8** Paste the output. Find `wants to merge 2 commits into main from feature/readme-usage`: the pull request now holds both
  commits, and its description says `Closes #2`.

## Task 3: Three ways to merge (25 marks)

GitHub merges a pull request in one of three ways, and each leaves a different history:

| Way | `gh` option | What lands on `main` |
|---|---|---|
| **Squash and merge** | `--squash` | all the commits of the branch become **one** new commit, `<title> (#<number>)` |
| **Merge commit** | `--merge` | every commit is kept, plus a **merge commit** with two parents |
| **Rebase and merge** | `--rebase` | every commit is **replayed** on top of `main`: same messages, new numbers, no merge commit |

You merge one pull request each way. Stay in your clone, on `main` for the setup.

*Needs:* the pull request of Task 2.

> **Catch-up box: only if you skipped Task 2.** Run these lines, once. They do what Task 2 does. If you did Task 2, do **not** run
> them. There is nothing to paste for them, and you lose only the marks of Task 2. (If you skipped Task 1 as well, run its box first.)
>
> ```bash
> git switch -c feature/readme-usage
> cat >> README.md << 'EOF'
>
> ## Usage
>
> Install the requirements first (see [the install guide](docs/instal.md)), then run:
>
>     python3 src/controller.py
> EOF
> git commit -am "docs: add usage instructions to readme"
> git push -u origin feature/readme-usage
> gh pr create --base main --head feature/readme-usage --title "docs: add usage instructions to readme" --body "Adds a Usage section. Closes #2"
> cat > README.md << 'EOF'
> # Kestrel-1 rover
>
> Control and vision code for the Kestrel-1 rover.
>
> See [the installation notes](docs/install.md) to set up a laptop.
>
> ## Usage
>
> Install the requirements first (see [the install guide](docs/install.md)), then run:
>
>     python3 src/controller.py
> EOF
> git commit -am "docs: fix broken link in usage section"
> git push
> ```

First two more pull requests (their numbers are 4 and 5). There is nothing to paste for these blocks; each ends with the
`gh pr create` that opens the pull request.

```bash
git switch main
git switch -c fix/detector-threshold
cat > src/detector.py << 'EOF'
"""Obstacle detector for the Kestrel-1 camera."""

THRESHOLD_CM = 30


def detect(distance_cm):
    return distance_cm < THRESHOLD_CM
EOF
git commit -am "fix(vision): raise the detection threshold"
git push -u origin fix/detector-threshold
gh pr create --base main --head fix/detector-threshold --title "fix(vision): raise the detection threshold" --body "The old threshold missed close obstacles."
```

```bash
git switch main
git switch -c feature/creep-speed
cat > src/controller.py << 'EOF'
"""Motion commands for the Kestrel-1 rover."""

MAX_SPEED = 60
CREEP_SPEED = 10


def move_forward(speed):
    return min(speed, MAX_SPEED)
EOF
git commit -am "feat(control): add creep speed"
cat > docs/speeds.md << 'EOF'
# Speeds

CREEP_SPEED is the slowest speed the rover drives at when it is close to an obstacle.
EOF
git add docs/speeds.md
git commit -m "docs: document the creep speed"
git push -u origin feature/creep-speed
gh pr create --base main --head feature/creep-speed --title "feat(control): add creep speed" --body "Adds a creep speed and documents it."
```

Now merge them, one way each. The pull request of Task 2 first. You are free to run these from any branch: `gh` talks to GitHub.

```bash
gh pr merge feature/readme-usage --squash
```

* **3.1** Paste the output. The two commits of the branch become one.

```bash
gh pr merge fix/detector-threshold --merge
```

* **3.2** Paste the output.

```bash
gh pr merge feature/creep-speed --rebase
```

* **3.3** Paste the output. (GitHub could merge all three without a conflict because they change different files.)

Everything happened on GitHub. Bring it down:

```bash
git switch main
git pull origin main
```

* **3.4** Paste the output of `git pull origin main`: a fast-forward over all the new commits.

```bash
git log --oneline --graph -8
```

* **3.5** Paste the output. Read it from the top: the two **replayed** commits (no merge, same messages as on the branch), then the
  **merge commit** with its branch (`|\` and `|/`), the **squash commit** `... (#3)` with a number in its title, and the commit
  you made on the branch of the merge.

After a merge the branch has done its job. Delete it, locally and on GitHub. (Git warns that the branch is merged into its remote
twin but not into `HEAD`: that is expected after a squash, which made a different commit.)

```bash
git branch -d feature/readme-usage
git push origin --delete feature/readme-usage
```

* **3.6** Paste the output of the two commands.
* Then type your answers: `ANSWER-2`: which merge strategy leaves a merge commit with two parents (`merge`, `squash` or `rebase`)?
  `ANSWER-3`: how many commits did the squash and merge add to `main`, for a pull request that had two commits?

## Task 4: The contributing guide and the closed issue (15 marks)

You did not close issue 2 yourself: the pull request description said `Closes #2`, and GitHub closed it when the pull request was
merged. Check, then write down the team's rules.

*Needs:* the merges of Task 3.

> **Catch-up box: only if you skipped Task 3.** Run these lines, once. They do what Task 3 does and merge the three pull requests.
> If you did Task 3, do **not** run them. There is nothing to paste for them, and you lose only the marks of Task 3. (If you skipped
> Task 2 as well, run its box first.)
>
> ```bash
> git switch main
> git switch -c fix/detector-threshold
> cat > src/detector.py << 'EOF'
> """Obstacle detector for the Kestrel-1 camera."""
>
> THRESHOLD_CM = 30
>
>
> def detect(distance_cm):
>     return distance_cm < THRESHOLD_CM
> EOF
> git commit -am "fix(vision): raise the detection threshold"
> git push -u origin fix/detector-threshold
> gh pr create --base main --head fix/detector-threshold --title "fix(vision): raise the detection threshold" --body "The old threshold missed close obstacles."
> git switch main
> git switch -c feature/creep-speed
> cat > src/controller.py << 'EOF'
> """Motion commands for the Kestrel-1 rover."""
>
> MAX_SPEED = 60
> CREEP_SPEED = 10
>
>
> def move_forward(speed):
>     return min(speed, MAX_SPEED)
> EOF
> git commit -am "feat(control): add creep speed"
> cat > docs/speeds.md << 'EOF'
> # Speeds
>
> CREEP_SPEED is the slowest speed the rover drives at when it is close to an obstacle.
> EOF
> git add docs/speeds.md
> git commit -m "docs: document the creep speed"
> git push -u origin feature/creep-speed
> gh pr create --base main --head feature/creep-speed --title "feat(control): add creep speed" --body "Adds a creep speed and documents it."
> gh pr merge feature/readme-usage --squash
> gh pr merge fix/detector-threshold --merge
> gh pr merge feature/creep-speed --rebase
> git switch main
> git pull origin main
> ```

```bash
gh issue list --state closed
```

* **4.1** Paste the output. Issue 2 is closed, and you never touched it.

A `CONTRIBUTING.md` tells newcomers how to work with the project. Type the whole block (there is nothing to paste for it).

```bash
cat > CONTRIBUTING.md << 'EOF'
# Contributing to Kestrel-1

## Branching strategy
- Branch from `main` for every feature or fix.
- Name branches `feature/<short-description>` or `fix/<short-description>`.

## Commit messages
Follow Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`.

## Pull requests
- All changes must go through a pull request.
- At least one reviewer approval is required before merging.
- Link pull requests to issues with `Closes #<number>`.
EOF
git add CONTRIBUTING.md
```

```bash
git commit -m "docs: add contributing guide"
```

* **4.2** Paste the output of `git commit`.

This is the last change that goes straight to `main`. After Task 5 it would be refused.

```bash
git push origin main
```

* **4.3** Paste the output.

```bash
gh issue list
```

* **4.4** Paste the output. Only issue 1 is still open.

## Task 5: Protect main (15 marks)

A rule that nobody enforces is a wish. **Branch protection** makes GitHub refuse a direct push to `main`, so every change has to come
through a pull request.

*Needs:* the guide of Task 4 on `main`.

> **Catch-up box: only if you skipped Task 4.** Run these lines, once, on `main`. They do what Task 4 does. If you did Task 4, do
> **not** run them. There is nothing to paste for them, and you lose only the marks of Task 4. (If you skipped Task 3 as well, run its
> box first.)
>
> ```bash
> cat > CONTRIBUTING.md << 'EOF'
> # Contributing to Kestrel-1
>
> ## Branching strategy
> - Branch from `main` for every feature or fix.
> - Name branches `feature/<short-description>` or `fix/<short-description>`.
>
> ## Commit messages
> Follow Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`.
>
> ## Pull requests
> - All changes must go through a pull request.
> - At least one reviewer approval is required before merging.
> - Link pull requests to issues with `Closes #<number>`.
> EOF
> git add CONTRIBUTING.md
> git commit -m "docs: add contributing guide"
> git push origin main
> ```

Turn the rule on. In the browser you would use **Settings, Branches, Add branch protection rule**, pattern `main`, tick **Require
a pull request before merging** and **Do not allow bypassing the above settings**. The same thing from the terminal, in one command
(type the whole block; it sets the number of required approvals to 0 so that you, working alone, can still merge your own pull
requests; a team would set 1):

```bash
gh api -X PUT repos/{owner}/{repo}/branches/main/protection --input - << 'EOF'
{
  "required_status_checks": null,
  "enforce_admins": true,
  "required_pull_request_reviews": { "required_approving_review_count": 0 },
  "restrictions": null
}
EOF
```

* **5.1** Paste the output (GitHub answers with JSON that names `.../branches/main/protection`). If `gh` says
  `Upgrade to GitHub Pro or make this repository public`, your repository is private: make it public in its Settings, at the bottom,
  and run the command again.

Now try to break the rule: commit straight on `main` and push. There is nothing to paste for the first two lines.

```bash
echo "direct push test" >> README.md
git commit -am "test: direct push (should be rejected)"
```

```bash
git push origin main
```

* **5.2** Paste the output. It is **supposed to be rejected**: `! [remote rejected]`, and GitHub's own lines say that the branch is
  protected and that changes must be made through a pull request.

Your laptop now has a commit that GitHub refused. Throw it away: `--hard` makes your `main` and your files equal to `origin/main`
again. (This is the one place in this course where `git reset --hard` is the right tool: the commit was never shared.)

```bash
git reset --hard origin/main
```

* **5.3** Paste the output.

```bash
git status
```

* **5.4** Paste the output: your `main` is up to date with `origin/main` and clean.

## Finish

```bash
python3 tests/grade.py
```

You want to see `PASS` for all five tasks and `TOTAL: 100/100`. Anything marked `FAIL` is listed with the reason; fix it and run the
grader again.

## Marks

| Task | Marks | How it is checked |
|---|---|---|
| 1 | 20 | the push, `gh auth status`, the two issue addresses and the list are pasted; one answer; your identity, your own repository and the tracking are real |
| 2 | 25 | the commit, push, pull request address and list, the review, the fix and `gh pr view` are pasted; the two commits really exist, in order, with the typo and its fix |
| 3 | 25 | the three merges, the pull, the graph and the branch deletion are pasted; two answers; `main` really holds a single squash commit, a merge commit with two parents, and two replayed commits |
| 4 | 15 | the closed list, the commit, the push and the open list are pasted; `CONTRIBUTING.md` is exactly the text of the handout |
| 5 | 15 | the protection answer, the rejected push, the reset and the status are pasted; your `main` really equals `origin/main` and does not hold the refused line |

A task shows **PASS** only when every check in it passes, and you earn marks for each check that passes even if the task as a whole
fails.

## If something goes wrong

* **You skipped a task and a later one fails.** Run the catch-up box at the start of the task after the one you skipped (in order,
  if you skipped several), then carry on.
* **`gh: command not found` or `To get started with GitHub CLI, please run: gh auth login`.** Do the section "Before the lab".
* **`Permission denied (publickey)` when you push.** GitHub does not know your SSH key: redo the key step (Experiment 3 or 10), check
  with `ssh -T git@github.com`.
* **`error: remote origin already exists`.** The clone's `origin` is still the course repository. Run `git remote rename origin
  upstream`, then `git remote add origin ...` again.
* **Step 1.1 is rejected, or says `remote contains work`.** You created the repository with a README or a licence, so it is not
  empty. Delete it (its Settings, at the bottom), create it again empty and Public, and push again.
* **`could not add label: 'enhancement' not found` or `no milestone found with title 'v1.0 Release'`.** The milestone command of Task 1
  was not run, or a label was deleted: run the `gh api ... milestones` line, or use `--label` with another label that `gh label list`
  shows.
* **Your issues or pull requests have other numbers than 1 to 5.** That is fine as long as you paste what GitHub printed. If the pull
  request of Task 2 is not number 3 or higher, you made it before the two issues: the grader wants the issues first.
* **`a pull request for branch "feature/readme-usage" into branch "main" already exists`.** You ran `gh pr create` twice. Carry on.
* **`Pull request ... is not mergeable` or conflicts.** Two branches changed the same lines. The lab's branches change different
  files, so check that you typed the file contents exactly; ask your instructor.
* **`--merge, --rebase, or --squash required`.** You left out the option of `gh pr merge`.
* **`failed to create review ... Can not approve your own pull request`.** GitHub forbids it. Use `--comment`, as the lab says.
* **Step 5.1 says `Upgrade to GitHub Pro`.** The repository is private: make it public (Settings, at the bottom, Change visibility).
* **Step 5.2 was not rejected.** The protection was not applied (check 5.1 for an error), or you are an administrator and the rule
  does not apply to you: the block sets `enforce_admins` to `true`, which includes you. Run 5.1 again. Then `git reset --hard origin/main`
  anyway, and your GitHub repository now holds the extra line: remove it with a pull request, or ask your instructor.
* **An editor opened and asked for a commit message.** You left out `-m "..."`. Save and exit (nano: `Ctrl+O`, `Enter`, `Ctrl+X`; vim:
  `Esc`, then `:wq` and `Enter`).
* **`tests/grade.py` says it cannot find the starting commit.** You are not inside your clone: `cd ~/rover-pr-lab`.
