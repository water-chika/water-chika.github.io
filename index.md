---
layout: default
title: water-chika
---

# water-chika

## Guides

- [Enable HDR for PRAGMATA on Steam Linux](pragmata-hdr-steam-linux.html)
- [Fix STEINS;GATE Not Launching on Steam Linux](steins-gate-steam-linux.html)

## Repositories

This site catalogs the public repositories owned by [water-chika](https://github.com/water-chika). The complete generated inventory is available in [`repos.json`](repos.json).

### Linear Algebra

This is a C++20 library written while studying linear algebra. It is used to practice C++ and provide feedback while learning the subject.

Related repositories:
[linear_algebra](https://github.com/water-chika/linear_algebra),
[linear_algebra_test](https://github.com/water-chika/linear_algebra_test),
[linear_algebra_test_build](https://github.com/water-chika/linear_algebra_test_build),
[integer](https://github.com/water-chika/integer), and
[rational_number](https://github.com/water-chika/rational_number).

The test code can be built from [linear_algebra_test_build](https://github.com/water-chika/linear_algebra_test_build).

Because [linear_algebra](https://github.com/water-chika/linear_algebra) is implemented with templates, matrices and vectors can use other integer or rational types. The [integer](https://github.com/water-chika/integer) and [rational_number](https://github.com/water-chika/rational_number) repositories provide simple implementations of those types.

### SPIR-V Parser

[spirv_parser](https://github.com/water-chika/spirv_parser) contains a SPIR-V disassembler.

### constexpr map

[constexpr_map](https://github.com/water-chika/constexpr_map) uses metaprogramming to implement a constexpr map with O(1) query time. It can also be used as a constexpr set.

### HIP support

I am adding HIP support to [cpp_helper](https://github.com/water-chika/cpp_helper) and [linear_algebra](https://github.com/water-chika/linear_algebra), allowing the linear algebra library to run on AMD GPUs.

### Parallel Scripts

[parallel_extract_zip](https://github.com/water-chika/parallel_extract_zip) contains scripts for parallel tasks such as extracting archives, copying folders, and comparing folders.
