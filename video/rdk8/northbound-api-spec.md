---
layout: data-table
title: Firebolt Core API Specification | RDK8
nav: northbound
hero:
  eyebrow: Interface catalog
  title: Firebolt Core API Specification
note: >-
  Phase I - Core Defined: the first Firebolt API specification release is
  published for development preview and early validation of RDK8's
  standardized, versioned app API layer.
table:
  id: northbound
  source: assets/data/northbound-apis.json
  columns: [Modules, Version, Methods]
  fields: [component, releaseTag, name]
  sort_field: component
  search_placeholder: Search Northbound APIs
  empty_message: No northbound apis have been loaded.
  show_version: false
---

The RDK8 Northbound API Specifications provide a consistent app-facing layer for web and native applications to access RDK8 platform services through Firebolt.
