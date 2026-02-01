Here is the comprehensive, step-by-step migration plan for implementing `RepoMap` in Kilo Code, followed by a series of optimized prompts designed to guide a large-context AI through the implementation.

# Cora Code Migration Plan: RepoMap

This document outlines the architectural and functional plan to port the `RepoMap` feature from the Python-based `mistral-vibe` to the TypeScript/VS Code environment of Kilo Code.

## **Phase 1: Architecture & Dependencies**

**Goal:** Establish the necessary libraries and asset structure to support `RepoMap` in a TypeScript environment without heavy external dependencies.

### **1.1 Dependencies**

* **`web-tree-sitter`**: The WASM-based binding for Tree-sitter. This is the standard for VS Code extensions, ensuring cross-platform compatibility without native node module compilation issues.
* **`js-tiktoken`**: A JavaScript port of OpenAI's token counter. Essential for accurately managing the context window limit (default 1024 tokens for the map).
* **`lru-cache`**: A standard library for efficient caching of parsed tags to prevent re-parsing unchanged files.

### **1.2 Directory Structure**

All logic will be encapsulated in a new service module.

```text
src/services/repomap/
├── index.ts                # Service entry point (Singleton)
├── types.ts                # Interfaces mirroring Python dataclasses
├── configuration.ts        # RepoMapConfig and constants
├── utils.ts                # Helper functions (tokenization, normalization)
├── tag-extractor.ts        # Logic ported from tags.py (Tree-sitter)
├── graph.ts                # Logic ported from graph.py (PageRank implementation)
├── renderer.ts             # Logic ported from rendering.py (Tree visualization)
└── queries/                # .scm files copied directly from vibe/repomap/queries/
    ├── python.scm
    ├── typescript.scm
    └── ...

```

---

## **Phase 2: Core Logic Porting**

### **2.1 Configuration & Types**

* **File:** `src/services/repomap/types.ts`
* **Objective:** Define strict TypeScript interfaces that mirror the Python dataclasses.
* **Details:**
* `RepoMapConfig`: Port constants like `path_boost_multiplier` and `chat_file_boost`.
* `Tag`: Interface `{ rel_fname, fname, line, name, kind, parent }`.
* `RepoMapResult`: Interface for the final output and error metrics.



### **2.2 Tag Extraction (The Parser)**

* **File:** `src/services/repomap/tag-extractor.ts`
* **Source:** `vibe/repomap/tags.py`
* **Logic:**
* **Initialization:** Load `web-tree-sitter` and the language WASM files (e.g., `tree-sitter-typescript.wasm`).
* **Query Loading:** Read `.scm` files from the `queries/` directory.
* **Extraction:**
1. Parse file content into a syntax tree.
2. Run the SCM query to capture `name.definition` and `name.reference`.
3. **Scope Resolution:** Reimplement `_build_scope_map` to determine the parent class/function of a tag.


* **Caching:** Use `lru-cache` keyed by `filePath + mtime` to store extraction results.



### **2.3 Graph Construction & PageRank**

* **File:** `src/services/repomap/graph.ts`
* **Source:** `vibe/repomap/graph.py`
* **Constraint:** Do not use `networkx`. Implement a custom, lightweight graph structure.
* **Logic:**
* **Graph Builder:** Create nodes for files and directed edges for references (`ref` -> `def`).
* **Edge Weighting:** Apply multipliers:
* Standard Ref: `1.0`
* Chat File Ref: `50.0`
* Common Symbol Damping: Implement `_compute_idf_weight`.


* **PageRank:** Implement a standalone iterative PageRank algorithm:
* Initialize nodes with `1/N`.
* Iterate (20 steps or convergence).
* Apply `0.85` damping factor.


* **Personalization:** Port `_compute_personalization` to boost ranks based on the user's current query (fuzzy matching mentions) and active file history.



### **2.4 Rendering & Visualization**

* **File:** `src/services/repomap/renderer.ts`
* **Source:** `vibe/repomap/rendering.py`
* **Logic:**
* **Selection:** Sort tags by their computed PageRank score.
* **Bin Packing:** Select the top tags that fit within the `mapTokens` limit (1024) using `js-tiktoken`.
* **Tree Formatting:** Generate a visual tree structure (like a folder tree) that includes the selected signatures (class/function headers) while eliding the bodies.



---

## **Phase 3: Integration Strategy**

### **3.1 Service Orchestration**

* **File:** `src/services/repomap/index.ts`
* **Responsibility:**
* Expose `generateRepoMap(query, activeFiles, workspaceFiles)`.
* Coordinate the pipeline: `Extract -> Build Graph -> Rank -> Render`.
* Ensure non-blocking execution (yield to event loop during heavy graph ops).



### **3.2 VS Code Context**

* Inject the generated map into the AI's system prompt or context window, wrapped in XML tags (e.g., `<repo_map>...</repo_map>`).

---

# **AI Implementation Prompts**

Use the following prompts in sequence to generate the code. Provide the content of the Python reference files (`core.py`, `tags.py`, `graph.py`, `rendering.py`) alongside these prompts.

### **Prompt 1: Types & Configuration**

```markdown
**Context:** We are porting the `RepoMap` feature from a Python codebase (`mistral-vibe`) to a TypeScript VS Code extension (Kilo Code).
**Reference:** `core.py` (RepoMapConfig), `tags.py` (Tag definitions).

**Task:**
1.  Create `src/services/repomap/types.ts`. Define strict interfaces for:
    * `Tag`: { relPath: string, absPath: string, line: number, name: string, kind: 'def' | 'ref', parent?: string }
    * `RepoMapConfig`: Mirror the configuration dataclass.
    * `ExtractionError` & `RepoMapResult`.
2.  Create `src/services/repomap/configuration.ts`.
    * Export a default configuration object matching `_DEFAULT_CONFIG`.
    * Export constants for `_PHRASE_SYNONYMS` and `_STOPWORDS`.
3.  Create `src/services/repomap/utils.ts`.
    * Port `_extract_ident_tokens` (regex based).
    * Port `_normalize_mentions`.

**Requirements:**
* Use TypeScript.
* Ensure regex patterns are JS-compatible.

```

### **Prompt 2: Tag Extraction (Web Tree Sitter)**

```markdown
**Context:** Parsing layer using `web-tree-sitter`.
**Reference:** `tags.py`.

**Task:** Create `src/services/repomap/tag-extractor.ts`.
1.  Implement class `TagExtractor`.
2.  **Init:** Accept a resource path to load `tree-sitter.wasm` and language WASMs.
3.  **Method `extractTags(filePath, code)`:**
    * Load the appropriate language parser.
    * Load the corresponding `.scm` query from disk.
    * Execute the query to find captures.
    * Map captures to the `Tag` interface.
4.  **Scope Resolution:** Port `_build_scope_map` logic to identify the parent class/function for a tag.
5.  **Caching:** Implement a simple in-memory cache using `Map<string, {mtime: number, tags: Tag[]}>`.

**Requirements:**
* Assume `web-tree-sitter` is imported as `Parser`.
* Handle file reading via standard Node `fs/promises`.

```

### **Prompt 3: Graph & PageRank**

```markdown
**Context:** PageRank implementation without `networkx`.
**Reference:** `graph.py` and `core.py` (ranking logic).

**Task:** Create `src/services/repomap/graph.ts`.
1.  **Data Structure:** Define a `Graph` class using adjacency lists (Map<node, edges>).
2.  **Method `buildGraph(tags, config)`:**
    * Create nodes for files.
    * Create edges for references (`ref` tag -> `def` tag).
    * Implement edge weighting logic (chat boost, technical word boost, IDF damping).
3.  **Method `computePageRank(personalization)`:**
    * Implement iterative PageRank (damping = 0.85).
    * Handle dangling nodes (nodes with no outgoing edges).
    * Input `personalization` is a Map<filePath, weight>.
4.  **Helper:** Port `_compute_idf_weight`.

**Requirements:**
* Write a custom, efficient PageRank implementation.
* Do not import external graph libraries.

```

### **Prompt 4: Renderer**

```markdown
**Context:** Visualization and token management.
**Reference:** `rendering.py`.

**Task:** Create `src/services/repomap/renderer.ts`.
1.  **Dependencies:** Use `js-tiktoken` for counting.
2.  **Method `render(rankedTags, tokenLimit)`:**
    * Sort tags by PageRank score.
    * Select tags until `tokenLimit` is reached.
3.  **Method `toTree(tags)`:**
    * Generate a "skeleton" representation of the code.
    * Show file paths as a tree.
    * Show selected function/class signatures indented correctly.
    * Elide bodies with `...`.

**Requirements:**
* Output must be clear, readable text/markdown.
* Strictly respect the token budget.

```

### **Prompt 5: Service Entry Point**

```markdown
**Context:** Wiring it all together.

**Task:** Create `src/services/repomap/index.ts`.
1.  Export `RepoMapService`.
2.  **Method `generate(query, chatHistoryFiles, workspaceFiles)`:**
    * Step 1: `TagExtractor.extract` (Parallel/Async).
    * Step 2: Calculate personalization (mentions in query).
    * Step 3: `Graph.build` & `Graph.pageRank`.
    * Step 4: `Renderer.render`.
3.  **Performance:** Ensure graph operations do not block the main thread (use `setImmediate` or chunking if possible).

**Requirements:**
* Handle errors gracefully (return empty string on failure).
* Add logging for debug purposes.

```
