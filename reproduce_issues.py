import subprocess
import os

def run_git(args):
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    return result.stdout

def check_rename():
    os.makedirs("repo", exist_ok=True)
    os.chdir("repo")
    subprocess.run(["git", "init"], check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "you@example.com"], check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Your Name"], check=True, capture_output=True)

    with open("old.txt", "w") as f: f.write("content\n")
    subprocess.run(["git", "add", "old.txt"], check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "add"], check=True, capture_output=True)

    subprocess.run(["git", "mv", "old.txt", "new.txt"], check=True, capture_output=True)
    with open("new.txt", "a") as f: f.write("more\n")
    subprocess.run(["git", "add", "new.txt"], check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "move"], check=True, capture_output=True)

    print("--- numstat output ---")
    print(run_git(["diff", "--numstat", "HEAD^", "HEAD"]))

    print("--- name-status output ---")
    print(run_git(["diff", "--name-status", "HEAD^", "HEAD"]))

if __name__ == "__main__":
    check_rename()
