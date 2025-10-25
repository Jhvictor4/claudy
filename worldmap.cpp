#include "worldmap.h"
#include <vector>
#include <set>
#include <queue>
#include <map>
#include <algorithm>
#include <cmath>

using namespace std;

vector<vector<int>> create_map(int N, int M, vector<int> A, vector<int> B) {
    // Build adjacency list
    vector<set<int>> adj(N + 1);
    for (int i = 0; i < M; i++) {
        adj[A[i]].insert(B[i]);
        adj[B[i]].insert(A[i]);
    }

    // Edge case: single node
    if (N == 1) {
        return {{1}};
    }

    // Detect graph type
    int maxDeg = 0;
    int deg1Count = 0;
    for (int i = 1; i <= N; i++) {
        maxDeg = max(maxDeg, (int)adj[i].size());
        if (adj[i].size() == 1) deg1Count++;
    }

    // Case 1: Linear chain
    if (M == N - 1 && deg1Count == 2 && maxDeg == 2) {
        int start = 1;
        for (int i = 1; i <= N; i++) {
            if (adj[i].size() == 1) {
                start = i;
                break;
            }
        }

        vector<int> chain;
        set<int> visited;
        int curr = start;

        while ((int)chain.size() < N) {
            chain.push_back(curr);
            visited.insert(curr);
            for (int next : adj[curr]) {
                if (!visited.count(next)) {
                    curr = next;
                    break;
                }
            }
        }

        int K = min(N, 240);
        vector<vector<int>> grid(K, vector<int>(K, 1));
        for (int i = 0; i < K && i < N; i++) {
            for (int j = 0; j < K; j++) {
                grid[i][j] = chain[i];
            }
        }
        return grid;
    }

    // Case 2: Star graph
    if (M == N - 1 && maxDeg == N - 1) {
        int center = 1;
        for (int i = 1; i <= N; i++) {
            if ((int)adj[i].size() == N - 1) {
                center = i;
                break;
            }
        }

        vector<int> leaves;
        for (int i = 1; i <= N; i++) {
            if (i != center) leaves.push_back(i);
        }

        int K = min(N, 240);
        vector<vector<int>> grid(K, vector<int>(K, center));

        for (int j = 0; j < K; j++) grid[0][j] = center;
        for (int j = 0; j < K && j < (int)leaves.size(); j++) {
            grid[1][j] = leaves[j];
        }
        for (int i = 2; i < K; i++) {
            for (int j = 0; j < K; j++) {
                grid[i][j] = center;
            }
        }
        return grid;
    }

    // Case 3: General graph (BFS placement with fixes)
    int K = min(max(2, N + (int)ceil(sqrt(2.0 * M))), 240);

    // FIX 1: Initialize grid to 0 (empty), not 1
    vector<vector<int>> grid(K, vector<int>(K, 0));

    map<int, vector<pair<int,int>>> positions;
    set<int> placed;
    set<pair<int,int>> used_cells;  // FIX 2: Track used cells
    queue<int> q;

    int dirs[4][2] = {{-1,0},{1,0},{0,-1},{0,1}};

    // FIX 3: Handle all components, not just node 1
    for (int start_node = 1; start_node <= N; start_node++) {
        if (placed.count(start_node)) continue;

        // Start BFS from this component
        int start_r = K/2 + (start_node - 1) / 10;  // Spread components
        int start_c = K/2 + (start_node - 1) % 10;
        if (start_r >= K) start_r = K - 1;
        if (start_c >= K) start_c = K - 1;

        grid[start_r][start_c] = start_node;
        positions[start_node].push_back({start_r, start_c});
        placed.insert(start_node);
        used_cells.insert({start_r, start_c});
        q.push(start_node);

        while (!q.empty()) {
            int u = q.front();
            q.pop();

            for (int v : adj[u]) {
                if (placed.count(v)) continue;

                // FIX 4: Limit positions per node to 3
                int max_positions = 3;

                bool foundPos = false;
                for (auto [ur, uc] : positions[u]) {
                    if (foundPos || (int)positions[v].size() >= max_positions) break;

                    for (auto& d : dirs) {
                        int nr = ur + d[0];
                        int nc = uc + d[1];

                        if (nr < 0 || nr >= K || nc < 0 || nc >= K) continue;
                        if (grid[nr][nc] != 0) continue;  // FIX 5: Check for empty cell (0)
                        if (used_cells.count({nr, nc})) continue;

                        // Check if placing v here creates false adjacencies
                        bool canPlace = true;
                        for (auto& dd : dirs) {
                            int nnr = nr + dd[0];
                            int nnc = nc + dd[1];
                            if (nnr >= 0 && nnr < K && nnc >= 0 && nnc < K) {
                                int neighbor = grid[nnr][nnc];
                                if (neighbor != 0 && neighbor != v && placed.count(neighbor)) {
                                    if (!adj[v].count(neighbor)) {
                                        canPlace = false;
                                        break;
                                    }
                                }
                            }
                        }

                        if (canPlace) {
                            grid[nr][nc] = v;
                            positions[v].push_back({nr, nc});
                            used_cells.insert({nr, nc});
                            placed.insert(v);
                            q.push(v);
                            foundPos = true;
                            break;
                        }
                    }
                    if (foundPos) break;
                }
            }
        }
    }

    // Fill remaining empty cells with node 1
    for (int i = 0; i < K; i++) {
        for (int j = 0; j < K; j++) {
            if (grid[i][j] == 0) {
                grid[i][j] = 1;
            }
        }
    }

    return grid;
}
