#!/usr/bin/env python3

import argparse
import json
import subprocess
import tempfile
from pathlib import Path


def fetch_repositories() -> list[dict]:
    result = subprocess.run(
        [
            "gh",
            "api",
            "--paginate",
            "users/water-chika/repos?per_page=100&type=owner&sort=full_name",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    decoder = json.JSONDecoder()
    repositories = []
    position = 0
    while position < len(result.stdout):
        page, position = decoder.raw_decode(result.stdout, position)
        repositories.extend(page)
        while position < len(result.stdout) and result.stdout[position].isspace():
            position += 1

    fields = (
        "name",
        "html_url",
        "ssh_url",
        "default_branch",
        "description",
        "archived",
        "fork",
    )
    catalog = []
    for repository in repositories:
        missing = [field for field in fields if field not in repository]
        if missing:
            raise ValueError(
                f"Repository {repository.get('name', '<unknown>')} is missing: "
                f"{', '.join(missing)}"
            )
        catalog.append(
            {
                "name": repository["name"],
                "url": repository["html_url"],
                "ssh_url": repository["ssh_url"],
                "default_branch": repository["default_branch"],
                "description": repository["description"],
                "archived": repository["archived"],
                "fork": repository["fork"],
            }
        )

    return sorted(catalog, key=lambda repository: repository["name"].casefold())


def main() -> None:
    parser = argparse.ArgumentParser(description="Update the water-chika repository catalog")
    parser.add_argument("output", nargs="?", type=Path, default=Path("repos.json"))
    args = parser.parse_args()

    catalog = fetch_repositories()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=args.output.parent,
        prefix=f"{args.output.name}.",
        delete=False,
    ) as output:
        json.dump(catalog, output, indent=2, ensure_ascii=False)
        output.write("\n")
        temporary = Path(output.name)

    temporary.replace(args.output)


if __name__ == "__main__":
    main()
