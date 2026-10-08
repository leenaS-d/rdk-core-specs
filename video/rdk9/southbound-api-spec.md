---
layout: data-table
title: Southbound API Specifications | RDK9
nav: southbound
hero:
  eyebrow: Interface catalog
  title: Southbound API Specifications
  status: Draft
table:
  id: southbound
  source: assets/data/southbound-apis.json
  columns: [HAL interface, Version, Source]
  fields: [halInterface, version, source]
  sort_field: halInterface
  link_column: 2
  search_placeholder: Search Southbound APIs
  empty_message: No southbound api specifications have been loaded.
  show_version: false
---

The Hardware Abstraction Layer (HAL) between middleware and the vendor layer, standardized interfaces that abstract hardware differences.