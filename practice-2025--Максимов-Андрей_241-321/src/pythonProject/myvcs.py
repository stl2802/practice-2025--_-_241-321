import argparse
import os
import hashlib
import json
from datetime import datetime

REPO_DIR = ".myvcs"
VERSION = "1.0"
COMMITS_DIR = os.path.join(REPO_DIR, "commits")
OBJECTS_DIR = os.path.join(REPO_DIR, "objects")
INDEX_FILE = os.path.join(REPO_DIR, "index")
HEAD_FILE = os.path.join(REPO_DIR, "HEAD")
CONFIG_FILE = os.path.join(REPO_DIR, "config")


class GitPlach:
    @staticmethod
    def init():
        if not os.path.exists(REPO_DIR):
            os.makedirs(REPO_DIR)
            os.makedirs(OBJECTS_DIR)
            os.makedirs(COMMITS_DIR)

            with open(INDEX_FILE, 'w') as f:
                json.dump([], f)

            with open(HEAD_FILE, 'w') as f:
                f.write("main")  # Default branch

            with open(CONFIG_FILE, 'w') as f:
                json.dump({
                    "version": VERSION,
                    "created": datetime.now().isoformat(),
                    "author": os.getenv("USER", "anonymous")
                }, f)

            print(f"Initialized empty GitPlach repository in {os.path.abspath(REPO_DIR)}")
            return True
        else:
            print("GitPlach repository already exists")
            return False

    @staticmethod
    def _get_file_hash(filepath):
        sha1 = hashlib.sha1()
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(65536)  # 64kb chunks
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()

    @staticmethod
    def add(filepath):
        if not os.path.exists(REPO_DIR):
            print("Not a GitPlach repository")
            return False

        if not os.path.exists(filepath):
            print(f"File {filepath} does not exist")
            return False

        try:
            with open(INDEX_FILE, 'r') as f:
                index = json.load(f)

            file_hash = GitPlach._get_file_hash(filepath)
            obj_path = os.path.join(OBJECTS_DIR, file_hash)

            with open(filepath, 'rb') as src, open(obj_path, 'wb') as dst:
                dst.write(src.read())

            index.append({
                "path": os.path.abspath(filepath),
                "hash": file_hash,
                "timestamp": datetime.now().isoformat()
            })

            with open(INDEX_FILE, 'w') as f:
                json.dump(index, f, indent=2)

            print(f"Added {filepath} to staging area")
            return True

        except Exception as e:
            print(f"Error adding file: {str(e)}")
            return False

    @staticmethod
    def remove(filepath):
        if not os.path.exists(REPO_DIR):
            print("Not a GitPlach repository")
            return False

        try:
            with open(INDEX_FILE, 'r') as f:
                index = json.load(f)

            new_index = [item for item in index if item['path'] != os.path.abspath(filepath)]

            if len(new_index) == len(index):
                print(f"File {filepath} not in staging area")
                return False

            with open(INDEX_FILE, 'w') as f:
                json.dump(new_index, f, indent=2)

            print(f"Removed {filepath} from staging area")
            return True

        except Exception as e:
            print(f"Error removing file: {str(e)}")
            return False

    @staticmethod
    def save(message):
        if not os.path.exists(REPO_DIR):
            print("Not a GitPlach repository")
            return False

        try:
            with open(INDEX_FILE, 'r') as f:
                index = json.load(f)

            if not index:
                print("Nothing to commit")
                return False

            with open(HEAD_FILE, 'r') as f:
                current_branch = f.read().strip()

            commit_id = hashlib.sha1(datetime.now().isoformat().encode()).hexdigest()
            commit_path = os.path.join(COMMITS_DIR, commit_id)

            commit_data = {
                "id": commit_id,
                "message": message,
                "author": os.getenv("USER", "anonymous"),
                "timestamp": datetime.now().isoformat(),
                "branch": current_branch,
                "files": index
            }

            with open(commit_path, 'w') as f:
                json.dump(commit_data, f, indent=2)

            # Clear staging area
            with open(INDEX_FILE, 'w') as f:
                json.dump([], f)

            print(f"Committed {commit_id[:8]} on {current_branch}: {message}")
            return True

        except Exception as e:
            print(f"Error creating commit: {str(e)}")
            return False

    @staticmethod
    def check():
        if not os.path.exists(REPO_DIR):
            print("Not a GitPlach repository")
            return False

        try:
            commits = []
            for commit_file in os.listdir(COMMITS_DIR):
                with open(os.path.join(COMMITS_DIR, commit_file), 'r') as f:
                    commit_data = json.load(f)
                    commits.append(commit_data)

            commits.sort(key=lambda x: x['timestamp'], reverse=True)

            print("\nCommit history:")
            for commit in commits:
                print(f"{commit['id'][:8]} [{commit['branch']}] {commit['message']}")
                print(f"  Author: {commit['author']}")
                print(f"  Date:   {commit['timestamp']}")
                print(f"  Files:  {len(commit['files'])}\n")

            return True

        except Exception as e:
            print(f"Error reading commits: {str(e)}")
            return False


def main():
    print("Программа запущена!")
    parser = argparse.ArgumentParser(
        description="GitPlach - простой система контроля версий",
        prog="gitplach"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"GitPlach {VERSION}",
        help="Показать версию"
    )

    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")


    init_parser = subparsers.add_parser("init", help="Инициализировать новый репозиторий")


    add_parser = subparsers.add_parser("add", help="Добавить файлы в staging area")
    add_parser.add_argument("filepath", help="Путь к файлу")


    remove_parser = subparsers.add_parser("remove", help="Удалить файлы из staging area")
    remove_parser.add_argument("filepath", help="Путь к файлу")


    save_parser = subparsers.add_parser("save", help="Создать новый коммит")
    save_parser.add_argument("-m", "--message", required=True, help="Сообщение коммита")

    check_parser = subparsers.add_parser("check", help="Показать историю коммитов")

    args = parser.parse_args()

    if args.command == "init":
        GitPlach.init()
    elif args.command == "add":
        GitPlach.add(args.filepath)
    elif args.command == "remove":
        GitPlach.remove(args.filepath)
    elif args.command == "save":
        GitPlach.save(args.message)
    elif args.command == "check":
        GitPlach.check()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()