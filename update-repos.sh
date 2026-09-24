#!/usr/bin/env bash
set -euo pipefail

output=${1:-repos.json}
temporary=$(mktemp "${output}.XXXXXX")
trap 'rm -f "$temporary"' EXIT

gh api --paginate \
    'users/water-chika/repos?per_page=100&type=owner&sort=full_name' |
    jq -s '[.[][] | {
        name,
        url: .html_url,
        ssh_url,
        default_branch,
        description,
        archived,
        fork
    }] | sort_by(.name | ascii_downcase)' > "$temporary"

mv "$temporary" "$output"
trap - EXIT
