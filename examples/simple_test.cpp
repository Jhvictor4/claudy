#include <iostream>
#include <vector>
using namespace std;

#include "world_map.cpp"

int main() {
    // Simple test: linear chain
    vector<int> A = {1, 2, 3, 4};
    vector<int> B = {2, 3, 4, 5};

    auto result = create_map(5, 4, A, B);

    cout << "Grid size: " << result.size() << "x" << result[0].size() << "\n";
    for (auto& row : result) {
        for (int val : row) {
            cout << val << " ";
        }
        cout << "\n";
    }

    return 0;
}
