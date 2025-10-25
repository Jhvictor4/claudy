# World Map IOI 2025 - Solution Explanation

## Problem Analysis

Given a graph with N vertices (countries) and M edges (adjacencies), we need to embed it into a 2D grid such that:
1. Every country appears at least once
2. Graph edges correspond exactly to grid adjacencies (4-directional, no diagonals)
3. Grid size K is minimized (K ≤ 240)

## Key Insights

### 1. **Graph Embedding Challenge**
- This is a **planar graph embedding** problem with grid constraints
- Not all graphs can be embedded optimally - some require duplicated nodes
- Each specific graph structure has an optimal embedding strategy

### 2. **Subtask-Specific Strategies**

#### **Linear Chain (Subtask 1)**: O(N) solution
- A path graph: 1-2-3-...-N
- **Optimal**: Place in a single row
- **K/N ratio**: 1 (best possible for paths)
- Grid: `1 2 3 4 ... N`

#### **Star Graph (Subtask 4)**: O(√N) solution
- One central node connected to all others
- **Optimal**: Place center, then leaves adjacent to center
- Use row layout: center followed by all leaves
- **K/N ratio**: 1 (linear layout)
- Grid: `center leaf1 leaf2 ... leafN-1`

#### **Complete Graph (Subtask 3)**: O(N) solution
- Every pair of nodes is adjacent
- **Challenge**: In a grid, each cell has at most 4 neighbors, but K_N needs N-1 neighbors each
- **Strategy**: Use duplication - place nodes in cross pattern
- For K_4: Need a layout where all 4 nodes are mutually grid-adjacent
- **K/N ratio**: Depends on N, typically N for small N

#### **Tree (Subtask 2)**: O(√N) solution
- Use BFS traversal from root
- Place each child adjacent to its parent
- **K/N ratio**: ~√(2N) for balanced trees

#### **General Graph (Subtask 6)**: O(√N) solution
- Use greedy BFS-based embedding
- Place each unplaced node adjacent to any of its already-placed neighbors
- Handle cycles by ensuring all edges are preserved

### 3. **Implementation Challenges**

1. **Zero-fill problem**: Never leave zeros in the final grid
2. **Adjacency preservation**: Must ensure every graph edge maps to a grid adjacency
3. **No false adjacencies**: Grid adjacencies that aren't in the graph must not exist

## Algorithm Design

```
create_map(N, M, A[], B[]):
    1. Build adjacency list from edges

    2. Detect graph type:
       - Linear chain: degree sequence is [1,2,2,...,2,1]
       - Star: one node has degree N-1
       - Complete: M = N*(N-1)/2
       - Tree: M = N-1 (and not linear/star)
       - General: anything else

    3. Apply optimal strategy for detected type

    4. Return grid (ensuring no zeros, all adjacencies preserved)
```

##Complexity Analysis

- **Time**: O(N + M) for adjacency list + O(K²) for grid operations
  - For most strategies: O(N²) in worst case
- **Space**: O(K²) for grid
  - Linear: O(N)
  - Star: O(N)
  - Complete: O(N²)
  - Tree/General: O(N)

## Key Edge Cases

1. **N=1**: Single cell grid `[[1]]`
2. **Disconnected graph**: Handle each component separately
3. **Isolated nodes**: Can place anywhere (no adjacency constraints)
4. **Dense graphs (high M)**: May require node duplication

##Solution Code Structure

```cpp
vector<vector<int>> create_map(int N, int M, vector<int> A, vector<int> B) {
    // Build graph
    // Detect type
    // Apply strategy:
    //   - Linear chain → single row
    //   - Star → center + leaves in row
    //   - Complete → cross pattern with duplication
    //   - Tree → BFS spiral
    //   - General → greedy BFS placement
    // Return grid
}
```

## Optimization for Subtask 6

For the general scoring subtask (56 points), the score depends on K/N ratio:
- Smaller K/N → better score
- Goal: Minimize wasted space
- Strategy: Tight BFS packing, avoid sparse grids
