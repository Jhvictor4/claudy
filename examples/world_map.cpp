#include <vector>
#include <set>
#include <algorithm>
#include <queue>
#include <map>
#include <cmath>

using namespace std;

/**
 * IOI 2025 World Map Solution
 *
 * Key insight: We need to embed a graph into a 2D grid where:
 * - Graph edges = Grid 4-adjacencies (not diagonal)
 * - Grid adjacencies NOT in graph = ERROR
 *
 * Special Cases:
 * 1. Linear Chain: Place in single row → K = N
 * 2. Star: Need center physically adjacent to all leaves
 * 3. Complete: All nodes mutually adjacent (hardest!)
 * 4. Tree: BFS placement from root
 * 5. General: BFS with careful placement
 */

vector<vector<int>> create_map(int N, int M, vector<int> A, vector<int> B) {
    // Build adjacency list
    vector<set<int>> adj(N + 1);
    for (int i = 0; i < M; i++) {
        adj[A[i]].insert(B[i]);
        adj[B[i]].insert(A[i]);
    }

    // Base case
    if (N == 1) return {{1}};

    // Priority 1: Check for STAR graph (center has degree N-1)
    int star_center = -1;
    if (M == N - 1) {
        for (int i = 1; i <= N; i++) {
            if ((int)adj[i].size() == N - 1) {
                star_center = i;
                break;
            }
        }
    }

    if (star_center != -1) {
        // Star graph: Use cross/plus pattern
        // Center at (1,1), leaves at (0,1), (2,1), (1,0), (1,2), etc.
        int numLeaves = N - 1;
        int side = max(3, 2 * ((numLeaves + 3) / 4) + 1); // Enough room

        vector<vector<int>> grid(side, vector<int>(side, star_center));
        int mid = side / 2;
        grid[mid][mid] = star_center;

        vector<int> leaves;
        for (int i = 1; i <= N; i++) {
            if (i != star_center) leaves.push_back(i);
        }

        // Place leaves in 4 directions from center
        int idx = 0;
        int dirs[4][2] = {{-1,0},{1,0},{0,-1},{0,1}};

        // First ring
        for (auto& d : dirs) {
            if (idx < numLeaves) {
                grid[mid + d[0]][mid + d[1]] = leaves[idx++];
            }
        }

        // Additional rings if needed
        for (int ring = 2; ring <= side/2 && idx < numLeaves; ring++) {
            for (auto& d : dirs) {
                if (idx < numLeaves) {
                    grid[mid + ring * d[0]][mid + ring * d[1]] = leaves[idx++];
                }
            }
        }

        return grid;
    }

    // Priority 2: Check for LINEAR CHAIN
    bool isChain = (M == N - 1);
    if (isChain) {
        int endpoints = 0;
        for (int i = 1; i <= N; i++) {
            if (adj[i].size() == 1) endpoints++;
            else if (adj[i].size() != 2) {
                isChain = false;
                break;
            }
        }
        isChain = isChain && (endpoints == 2);
    }

    if (isChain) {
        // Find path
        int start = -1;
        for (int i = 1; i <= N; i++) {
            if (adj[i].size() == 1) {
                start = i;
                break;
            }
        }

        vector<int> path;
        vector<bool> visited(N + 1, false);
        int curr = start;
        while (curr != -1) {
            path.push_back(curr);
            visited[curr] = true;
            int next = -1;
            for (int neighbor : adj[curr]) {
                if (!visited[neighbor]) {
                    next = neighbor;
                    break;
                }
            }
            curr = next;
        }

        return {path};
    }

    // Priority 3: Check for COMPLETE GRAPH
    bool isComplete = (M == N * (N - 1) / 2);
    if (isComplete) {
        // Complete graphs need all pairs adjacent
        // Use a star-like pattern with node 1 at center, others in cross
        // Then fill background with node 1 to ensure all are mutually adjacent through node 1

        if (N == 2) return {{1, 2}};
        if (N == 3) return {{1, 2}, {3, 1}};
        if (N == 4) {
            // All 4 must be mutually adjacent
            return {{1, 2, 1},
                    {3, 1, 4},
                    {1, 2, 1}};
        }

        // For N >= 5, use grid where node 1 fills most space
        // and other nodes are placed in cross pattern
        int size = (N / 2) + 2;
        vector<vector<int>> grid(size, vector<int>(size, 1));
        int mid = size / 2;

        int node = 2;
        // Horizontal line through middle
        for (int j = 0; j < size && node <= N; j++) {
            if (j != mid) grid[mid][j] = node++;
        }
        // Vertical line through middle
        for (int i = 0; i < size && node <= N; i++) {
            if (i != mid) grid[i][mid] = node++;
        }

        return grid;
    }

    // General case: BFS placement
    int side = max(3, (int)ceil(sqrt(2.5 * N)) + 3);
    vector<vector<int>> grid(side, vector<int>(side, 0));

    map<int, pair<int,int>> pos;
    vector<bool> placed(N + 1, false);

    int startR = side / 2;
    int startC = side / 2;
    grid[startR][startC] = 1;
    pos[1] = {startR, startC};
    placed[1] = true;

    queue<int> q;
    q.push(1);

    int dirs[4][2] = {{-1,0},{1,0},{0,-1},{0,1}};

    while (!q.empty()) {
        int u = q.front();
        q.pop();
        auto [ur, uc] = pos[u];

        for (int v : adj[u]) {
            if (placed[v]) continue;

            // Place v adjacent to u
            bool found = false;
            for (auto& d : dirs) {
                int nr = ur + d[0];
                int nc = uc + d[1];
                if (nr >= 0 && nr < side && nc >= 0 && nc < side && grid[nr][nc] == 0) {
                    grid[nr][nc] = v;
                    pos[v] = {nr, nc};
                    placed[v] = true;
                    q.push(v);
                    found = true;
                    break;
                }
            }

            // If no space adjacent to u, try adjacent to any other neighbor of v
            if (!found && !placed[v]) {
                for (int w : adj[v]) {
                    if (placed[w] && w != u) {
                        auto [wr, wc] = pos[w];
                        for (auto& d : dirs) {
                            int nr = wr + d[0];
                            int nc = wc + d[1];
                            if (nr >= 0 && nr < side && nc >= 0 && nc < side && grid[nr][nc] == 0) {
                                grid[nr][nc] = v;
                                pos[v] = {nr, nc};
                                placed[v] = true;
                                q.push(v);
                                found = true;
                                break;
                            }
                        }
                        if (found) break;
                    }
                }
            }
        }
    }

    // Handle isolated nodes
    for (int i = 1; i <= N; i++) {
        if (!placed[i]) {
            bool found = false;
            // Try to place adjacent to neighbors
            for (int j : adj[i]) {
                if (placed[j]) {
                    auto [jr, jc] = pos[j];
                    for (auto& d : dirs) {
                        int nr = jr + d[0];
                        int nc = jc + d[1];
                        if (nr >= 0 && nr < side && nc >= 0 && nc < side && grid[nr][nc] == 0) {
                            grid[nr][nc] = i;
                            pos[i] = {nr, nc};
                            placed[i] = true;
                            found = true;
                            break;
                        }
                    }
                    if (found) break;
                }
            }

            // Place anywhere if isolated
            if (!placed[i]) {
                for (int r = 0; r < side && !placed[i]; r++) {
                    for (int c = 0; c < side && !placed[i]; c++) {
                        if (grid[r][c] == 0) {
                            grid[r][c] = i;
                            pos[i] = {r, c};
                            placed[i] = true;
                        }
                    }
                }
            }
        }
    }

    // Trim and return
    int minR = side, maxR = -1, minC = side, maxC = -1;
    for (int i = 0; i < side; i++) {
        for (int j = 0; j < side; j++) {
            if (grid[i][j] != 0) {
                minR = min(minR, i);
                maxR = max(maxR, i);
                minC = min(minC, j);
                maxC = max(maxC, j);
            }
        }
    }

    if (minR > maxR) return {{1}};

    vector<vector<int>> result(maxR - minR + 1, vector<int>(maxC - minC + 1));
    for (int i = minR; i <= maxR; i++) {
        for (int j = minC; j <= maxC; j++) {
            result[i - minR][j - minC] = (grid[i][j] == 0) ? 1 : grid[i][j];
        }
    }

    return result;
}
