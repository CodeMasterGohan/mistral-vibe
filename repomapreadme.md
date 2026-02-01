Vibe RepoMap: The Context Intelligence EngineRepoMap is the context selection system powering Mistral Vibe. It addresses the "Lost in the Middle" phenomenon in Large Language Models (LLMs) by intelligently selecting the most relevant 1-2K tokens of code from potentially massive repositories.Unlike standard RAG (Retrieval-Augmented Generation) which relies on vector similarity, RepoMap builds a semantic dependency graph of the codebase, applies Personalized PageRank to determine symbol importance, and uses binary search optimization to fit the highest-value context into a strict token budget.🏗 Architecture OverviewThe RepoMap pipeline consists of five tightly integrated phases designed to distill thousands of files down to a "skeleton" of the codebase that is most relevant to the user's current task.graph TD
    subgraph Phase 1: Extraction
    A[Source Code] -->|Tree-sitter| B(AST Parsing)
    B -->|S-Expression Queries| C(Tags: Defs & Refs)
    C -->|SQLite| D[Tag Cache]
    end

    subgraph Phase 2: Graph Construction
    C --> E[Dependency Graph]
    E -->|Edge Weights| F(MultiDiGraph)
    end

    subgraph Phase 3: Personalization
    G[Chat Context] --> H{Scoring Engine}
    I[User Mentions] --> H
    J[File Proximity] --> H
    H -->|Bias Vector| K[Personalization Scores]
    end

    subgraph Phase 4: Ranking
    F --> L(PageRank)
    K --> L
    L --> M[Ranked Definitions]
    end

    subgraph Phase 5: Selection
    M --> N{Binary Search}
    N -->|Token Counting| O[Sampling Estimator]
    O --> P[Final Context Map]
    end
🧠 The Algorithm Deep DivePhase 1: Tag Extraction (Parsing)The system parses code to identify definitions (classes, functions) and references (calls, usage).Engine: Uses Tree-sitter for 40+ languages.Querying: Language-specific .scm (S-expression) files define exactly what constitutes a definition or reference.Data Structure: Extracted tags are stored as lightweight named tuples: (rel_fname, fname, line, name, kind).Fallback Strategy: For languages that define symbols but don't expose references via Tree-sitter (e.g., C/C++), the system falls back to a Pygments lexer to backfill references by tokenizing the source code.Caching: Results are cached in a SQLite database, keyed by file modification time (mtime) to avoid re-parsing unchanged files.Phase 2: Graph ConstructionA MultiDiGraph (NetworkX) is constructed where nodes are files and edges represent dependencies.Edge Logic: If main.py calls utils.process_data(), a directed edge is created from main.py -> utils.py.Weight Dampening: A "Square Root Dampening" is applied to edge weights ($weight \propto \sqrt{count}$). This ensures that a utility function referenced 100 times doesn't get 100x the importance, preventing common utilities from dominating the graph.Symbol Penalties:Common Symbols: Symbols defined in $>5$ files are treated as generic and penalized.Private Symbols: Symbols starting with _ (e.g., _internal_impl) are penalized ($0.1\times$).Phase 3: Personalization & ScoringThe graph is not static; it adapts to the user's specific session context using a Personalization Vector. This vector biases the PageRank algorithm.TriggerBoost FactorLogicChat Files10.0xFiles currently open/edited by the user are the center of attention.Mentions5.0xFiles explicitly named by the user (e.g., "Look at config.py").Def Token Match20.0xCritical: If the user asks "How does auth work?", any file defining a symbol named auth gets a massive boost.Ref Name Match25.0xIf a file contains a reference matching a user query token exactly.Proximity±1.0Files in the same directory as active chat files get a small boost; distant files are penalized.Phase 4: PageRank RankingWe run a Personalized PageRank algorithm on the dependency graph.Teleportation: The random walker "teleports" back to the personalized nodes (chat files/mentions) more frequently. This ensures the ranking "flows" from the user's focus out to the dependencies.Rank Distribution: The final PageRank score of a file is distributed to its individual definitions based on how often they are referenced.Phase 5: Context SelectionThe system must select the optimal set of symbols to fit the token budget (default 1024 tokens).Binary Search: It performs a binary search over the ranked list of definitions to find a cut-off point that yields a context size within 15% of the target.Tree Rendering: Selected symbols are rendered as a "code skeleton"—signatures and minimal context—hiding implementation details to save space.Adaptive Sampling: To speed up the binary search, token counting uses sampling (counting ~1% of lines) rather than full tokenization, achieving ~100x speedup with ±5% accuracy.⚙️ Configuration (RepoMapConfig)The behavior of the engine is controlled by the RepoMapConfig class in vibe/repomap/core.py.@dataclass(frozen=True)
class RepoMapConfig:
    # Path-based multipliers
    path_boost_multiplier: float = 2.0       # Priority for 'entrypoint' paths
    path_test_multiplier: float = 0.4        # Penalize 'tests/', 'spec/'
    path_framework_multiplier: float = 0.5   # Penalize 'vendor/', 'third_party/'

    # Personalization boosts
    chat_file_boost: float = 10.0            # Active file importance
    mentioned_file_boost: float = 5.0        # User mentioned file importance
    def_token_match_boost: float = 20.0      # User query matches definition
    
    # Graph edge weights
    chat_file_edge_weight: float = 50.0      # References FROM chat files are heavy
    private_symbol_penalty: float = 0.1      # '_private' symbols are weak
    common_symbol_threshold: int = 5         # Threshold for 'common' symbol penalty
💻 CLI UsageVibe provides a utility script for generating and inspecting repo maps: scripts/generate_repomap.py.Basic GenerationGenerate the markdown representation (what the LLM sees) and print to stdout:uv run scripts/generate_repomap.py --markdown
Exporting ArtifactsGenerate JSON data, Gephi graphs, and GraphML for visualization:uv run scripts/generate_repomap.py --output ./artifacts --formats json,gexf,graphml
JSON: Contains full ranking data, cache statistics, and extraction errors.GEXF: Graph Exchange XML Format. Import this into Gephi to visualize your codebase's dependency structure.Incremental UpdatesFor large repositories, use incremental indexing to only process changed files:uv run scripts/generate_repomap.py --incremental --state-file ./map_state.json
Repository StatisticsPrint detailed stats about graph nodes, edges, and language breakdown:uv run scripts/generate_repomap.py --stats
Example Output:Repository Statistics
==================================================
  Name: mistral-vibe
  Total Files: 120
  Total LOC: 15,400
  Primary Language: Python
  Graph Nodes: 120
  Graph Edges: 840
🐍 Python API UsageTo use RepoMap programmatically:from vibe.repomap import RepoMap

# 1. Initialize
repo_map = RepoMap(
    map_tokens=1024,          # Target context size
    root="/path/to/repo",     # Repository root
    verbose=True
)

# 2. Generate Context
# chat_files: Files the user is currently looking at
# other_files: All other files in the repo
context_string = repo_map.get_repo_map(
    chat_files=["src/main.py"],
    other_files=["src/utils.py", "src/config.py"],
    mentioned_idents={"auth", "login"} # Optional keywords from user query
)

print(context_string)
Diagnostics APITo inspect internal state (rankings, cache hits, errors):result = repo_map.get_repo_map_with_diagnostics(
    chat_files=["src/main.py"],
    other_files=all_files
)

print(f"Cache Hits: {result.cache_hits}")
print(f"Top Ranked Def: {result.ranked_defs[0]}")
print(f"Extraction Errors: {len(result.errors)}")
⚡ Performance & CachingMetricComplexityNotesFirst Run$O(F \times N)$$F$=files, $N$=size. Dominated by Tree-sitter parsing.Subsequent$O(\log D)$$D$=definitions. Graph is cached; only PageRank + Search runs.Token Count$O(1)$Uses adaptive sampling (1% of lines) for instant estimation.Caching StrategyLocation: .vibe/cache/repomap/Invalidation: Checks file modification time (mtime). If the file hasn't changed on disk, the AST parse step is skipped entirely.
