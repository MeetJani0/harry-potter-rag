import os
import subprocess

REPO_NAME = "harry-potter-rag"

gitignore_content = """
.env
hp_rag/
__pycache__/
*.pyc
.DS_Store
"""

if not os.path.exists(".gitignore"):
    with open(".gitignore", "w") as f:
        f.write(gitignore_content.strip())

commands = [
    "git init",
    "git add .",
    'git commit -m "Initial commit - Harry Potter RAG Assistant"',
    f"gh repo create {REPO_NAME} --public --source=. --push"
]

for cmd in commands:
    subprocess.run(cmd, shell=True, check=True)

print("✅ Repository created and pushed successfully!")