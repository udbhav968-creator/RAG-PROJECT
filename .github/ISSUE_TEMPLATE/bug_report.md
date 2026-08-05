name: Bug report
description: Create a report to help us improve Industrial RAG Engine
title: '[BUG]: '
labels: ['bug']
assignees: ''

body:
  - type: textarea
    id: description
    attributes:
      label: Bug Description
      description: A clear and concise description of what the bug is.
    validations:
      required: true
  - type: textarea
    id: reproduction
    attributes:
      label: Steps to Reproduce
      description: Steps to reproduce the behavior.
    validations:
      required: true
