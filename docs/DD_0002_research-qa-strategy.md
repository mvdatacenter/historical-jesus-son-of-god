# DD-0002: Research Findings Public Boundary

## Problem

The book uses a research findings workflow outside this public repository to evaluate exploratory research before it reaches the manuscript.
That workflow contains generated findings, research Q&A, open research gaps, review artifacts, and source-discovery context that belong outside this public repository.

This public repository still needs a stable contract for how research becomes public manuscript material.

## Goals

1. State which research artifacts belong outside this public repository.
2. Define which promoted artifacts may enter this public repository.
3. Preserve the public citation-review contract for manuscript material.

## Decision

The detailed findings workflow lives outside this public repository.
This repository keeps only the public-facing contract:

1. Exploratory findings stay outside this repository until they are promoted.
2. A promoted finding enters public work only as verified citation material, bibliography data, source-verification material, manuscript prose, or code/data directly used to construct a result in the book.
3. Manuscript additions still follow the established sequence: route by chapter argument, embed only when the addition strengthens the section, verify factual claims against sources, and run citation review before final text is committed.
4. Public citation verification remains governed by [DD-0001](DD_0001_citation-review-report.md).

## Public Review Contract

Public manuscript changes must show the evidence that supports the claim.
Research notes, generated findings, rejected leads, and open research questions stay outside this repository until they are converted into public-safe artifacts.

When a claim is valuable but still unverified, record it in the research workflow outside this repository.
When a claim is verified and enters the manuscript, cite the source in the public book and run the citation-verification workflow here.

## Public Files

This repository keeps:

- manuscript chapters and bibliography;
- source registry and citation-verification code;
- downloaded public source texts and generated citation-review reports;
- public design docs, review guidelines, and post-mortems.

These artifacts stay outside this repository:

- generated findings;
- research Q&A records;
- open research-gap lists;
- extraction-review UIs and verdict files;
- exploratory maps, one-off investigations, and cache-backed research artifacts.
