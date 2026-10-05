---
layout: data-table
title: Southbound API Specifications | RDK8
nav: southbound
hero:
  eyebrow: Interface catalog
  title: Southbound API Specifications
  status: Published
table:
  id: southbound
  source: assets/data/southbound-apis.json
  columns: [HAL interface, Version, Source]
  fields: [halInterface, releaseTag, source]
  sort_field: halInterface
  link_column: 2
  strip_release_path: true
  search_placeholder: Search Southbound APIs
  empty_message: No southbound api specifications have been loaded.
  show_version: false
---

The Hardware Abstraction Layer (HAL) between middleware and the vendor layer — standardized interfaces that abstract hardware differences.
