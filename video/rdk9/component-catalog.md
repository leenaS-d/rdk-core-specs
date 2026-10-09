---
layout: data-table
title: Components Catalog | RDK9
nav: components
hero:
  eyebrow: Core and non-core components
  title: Components Catalog
  status: Approved
table:
  id: catalog
  source: catalog
  classes: component-catalog-table
  columns: [Component, Category, Layer, Type, Version, Source]
  search_placeholder: Search components
  empty_message: No components match the current filters.
  link_column: 5
  pill_columns: [1]
  pill_variant_columns: [3]
  filters:
    - field: category
      column: 1
      all_label: All categories
    - field: layer
      column: 2
      all_label: All layers
    - field: type
      column: 3
      all_label: All types
---

Explore the RDK9 Core and Non-core Components Catalog, connecting application-facing capabilities with middleware and vendor-layer implementations.
