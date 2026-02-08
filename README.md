# Repos

Recently I use a standalone building repo to seperate building from source code because this could resolve duplicate deps of repos.

## Linear Algebra

This is a C++20 library written when I study Linear Algebra. The library is used to practice My C++ and give me some feedback to learning Linear algebra.

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
