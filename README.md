# Repos

This repository catalogs the public repositories owned by
[water-chika](https://github.com/water-chika).

- `repos.json` is the generated repository inventory.
- `update-repos.sh` regenerates the inventory through the GitHub API.

Update the catalog with:

```sh
./update-repos.sh
```

List repository names without cloning their histories:

```sh
jq -r '.[].name' repos.json
```

Query GitHub directly when a local catalog is not needed:

```sh
gh repo list water-chika --limit 1000
```

The catalog replaces the previous submodule collection. Submodules pin commits
and are useful for build dependencies, but they are unnecessary for a repository
index and make ordinary clones much larger and harder to maintain.

Recently I use a standalone building repo to seperate building from source code because this could resolve duplicate deps of repos.

## Linear Algebra

This is a C++20 library written when I study Linear Algebra. The library is used to practice my C++ and give me some feedback to learning Linear Algebra.

Related repos:
[linear_algebra](https://github.com/water-chika/linear_algebra),
[linear_algebra_test](https://githbu.com/water-chika/linear_algebar_test),
[linear_algebra_test_build](https://github.com/water-chika/linear_algebra_test_build),
[integer](https://github.com/water-chika/integer),
[rational_number](https://github.com/water-chika/rational_number),

Test code could be built from: [linear_algebra_test_build](https://github.com/water-chika/linear_algebra_test_build)

Because [linear_algebra](https://github.com/water-chika/linear_algebra) is implemented by template, it could use other integer types or rational types as parameter of matrix and vector. I write a simple implementation of integer and rational in [integer](https://github.com/water-chika/integer),
[rational_number](https://github.com/water-chika/rational_number).

## SPIRV Parser

It contains a SPIRV disassember: [spirv_parser](https://github.com/water-chika/spirv_parser)

## constexpr map

Repo: [constexpr_map](https://github.com/water-chika/constexpr_map)

It uses meta-programming to implement a constexpr map with O(1) query time. It also could be used like a constexpr set.

## HIP support

I'm trying to add support of HIP to [cpp_helper](https://github.com/water-chika/cpp_helper) and [linear_algebra](https://github.com/water-chika/linear_algebra).
With this, [linear_algebra](https://github.com/water-chika/linear_algebra) library could be run on AMD GPU.

## Parallel Scripts

There is a repo contains some scripts to parallel do some thing like extract zip, copy folders and compare folders.

URL: [parallel_extract_zip](https://github.com/water-chika/parallel_extract_zip)

