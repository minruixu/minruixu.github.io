#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

for ruby_bin_dir in \
  "/opt/homebrew/opt/ruby@3.3/bin" \
  "/opt/homebrew/opt/ruby/bin" \
  "/usr/local/opt/ruby@3.3/bin" \
  "/usr/local/opt/ruby/bin"
do
  if [ -d "$ruby_bin_dir" ] && [[ ":$PATH:" != *":$ruby_bin_dir:"* ]]; then
    export PATH="$ruby_bin_dir:$PATH"
    break
  fi
done

BUNDLER_VERSION="$(awk '/^BUNDLED WITH$/{getline; gsub(/^ +/, "", $0); print; exit}' Gemfile.lock)"

if [ -z "$BUNDLER_VERSION" ]; then
  echo "Could not determine bundler version from Gemfile.lock" >&2
  exit 1
fi

bundle "_${BUNDLER_VERSION}_" exec github-pages build --source . --destination ./_site

rm -rf docs
mkdir -p docs
rsync -a --delete ./_site/ ./docs/
touch ./docs/.nojekyll

echo "Static site refreshed in ./docs"
