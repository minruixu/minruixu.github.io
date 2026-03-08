# minruixu.github.io
Welcome to Minrui's page

## Local Build And Publish

This repository is set up for local precompilation and static publishing from `main/docs`.

Build the site and refresh the publish directory with:

```bash
./scripts/build_docs.sh
```

Then commit and push the updated `docs/` directory.

In GitHub, set `Settings > Pages > Source` to `Deploy from a branch`, then select:

- Branch: `main`
- Folder: `/docs`
