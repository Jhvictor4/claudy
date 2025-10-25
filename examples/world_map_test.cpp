#include <iostream>
#include <vector>
#include <set>
#include <cassert>
#include "world_map.cpp"

using namespace std;

class Validator {
private:
    int N, M;
    vector<set<int>> adj;
    int K;
    vector<vector<int>> grid;

    void printGrid() {
        int rows = grid.size();
        int cols = grid.empty() ? 0 : grid[0].size();
        cout << "Grid " << rows << "x" << cols << ":\n";
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                cout << grid[i][j] << " ";
            }
            cout << "\n";
        }
    }

    bool validate() {
        int rows = grid.size();
        if (rows == 0) {
            cout << "ERROR: Grid is empty\n";
            return false;
        }

        int cols = grid[0].size();
        K = max(rows, cols);

        if (K > 240) {
            cout << "ERROR: K = " << K << " exceeds 240\n";
            return false;
        }

        // Check all countries appear
        set<int> countries;
        for (int i = 0; i < rows; i++) {
            if (grid[i].size() != cols) {
                cout << "ERROR: Grid rows have different lengths\n";
                return false;
            }
            for (int j = 0; j < cols; j++) {
                if (grid[i][j] < 1 || grid[i][j] > N) {
                    cout << "ERROR: Invalid country " << grid[i][j] << " at (" << i << "," << j << ")\n";
                    return false;
                }
                countries.insert(grid[i][j]);
            }
        }

        if ((int)countries.size() != N) {
            cout << "ERROR: Only " << countries.size() << " countries present, expected " << N << "\n";
            return false;
        }

        // Check adjacency constraints
        set<pair<int,int>> gridAdj;
        int dirs[4][2] = {{-1,0},{1,0},{0,-1},{0,1}};

        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                for (auto& d : dirs) {
                    int ni = i + d[0];
                    int nj = j + d[1];
                    if (ni >= 0 && ni < rows && nj >= 0 && nj < cols) {
                        int u = grid[i][j];
                        int v = grid[ni][nj];
                        if (u != v) {
                            int a = min(u, v), b = max(u, v);
                            gridAdj.insert({a, b});
                        }
                    }
                }
            }
        }

        // Check all graph edges are in grid adjacency
        for (int u = 1; u <= N; u++) {
            for (int v : adj[u]) {
                if (u < v) {
                    if (gridAdj.find({u, v}) == gridAdj.end()) {
                        cout << "ERROR: Edge (" << u << "," << v << ") not in grid\n";
                        return false;
                    }
                }
            }
        }

        // Check all grid adjacencies are in graph
        for (auto [u, v] : gridAdj) {
            if (adj[u].find(v) == adj[u].end()) {
                cout << "ERROR: Grid adjacency (" << u << "," << v << ") not in graph\n";
                return false;
            }
        }

        return true;
    }

public:
    bool test(int N, int M, vector<int> A, vector<int> B, string testName) {
        this->N = N;
        this->M = M;
        adj.assign(N + 1, set<int>());

        for (int i = 0; i < M; i++) {
            adj[A[i]].insert(B[i]);
            adj[B[i]].insert(A[i]);
        }

        cout << "\n=== Test: " << testName << " ===\n";
        cout << "N=" << N << ", M=" << M << "\n";

        grid = create_map(N, M, A, B);
        printGrid();

        bool valid = validate();
        if (valid) {
            cout << "PASS - K/N ratio: " << (double)grid.size() / N << "\n";
        } else {
            cout << "FAIL\n";
        }

        return valid;
    }
};

int main() {
    Validator validator;
    int passed = 0, total = 0;

    // Test 1: Single node
    total++;
    if (validator.test(1, 0, {}, {}, "Single node")) passed++;

    // Test 2: Linear chain
    total++;
    if (validator.test(5, 4, {1,2,3,4}, {2,3,4,5}, "Linear chain (5 nodes)")) passed++;

    // Test 3: Star graph
    total++;
    if (validator.test(5, 4, {1,1,1,1}, {2,3,4,5}, "Star graph (5 nodes)")) passed++;

    // Test 4: Complete graph K4
    total++;
    if (validator.test(4, 6, {1,1,1,2,2,3}, {2,3,4,3,4,4}, "Complete graph K4")) passed++;

    // Test 5: Tree (not linear)
    total++;
    if (validator.test(7, 6, {1,1,2,2,3,3}, {2,3,4,5,6,7}, "Binary tree")) passed++;

    // Test 6: Path graph
    total++;
    if (validator.test(3, 2, {1,2}, {2,3}, "Path graph (3 nodes)")) passed++;

    // Test 7: Cycle (not a tree)
    total++;
    if (validator.test(4, 4, {1,2,3,4}, {2,3,4,1}, "Cycle (4 nodes)")) passed++;

    // Test 8: Complex graph
    total++;
    if (validator.test(6, 7, {1,1,2,2,3,4,5}, {2,3,3,4,4,5,6}, "Complex graph")) passed++;

    // Test 9: Two node path
    total++;
    if (validator.test(2, 1, {1}, {2}, "Two nodes")) passed++;

    // Test 10: Larger star
    total++;
    if (validator.test(10, 9, {1,1,1,1,1,1,1,1,1}, {2,3,4,5,6,7,8,9,10}, "Star graph (10 nodes)")) passed++;

    cout << "\n=================================\n";
    cout << "Results: " << passed << "/" << total << " tests passed\n";
    cout << "=================================\n";

    return (passed == total) ? 0 : 1;
}
