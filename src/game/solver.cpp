#include <algorithm>
#include <array>
#include <iostream>
#include <future>
#include <map>
#include <numeric>
#include <shared_mutex>
#include <string>
#include <thread>
#include <utility>
#include <vector>

namespace Solver {
    constexpr int FIELD_WIDTH = 7;
    constexpr int FIELD_HEIGHT = 6;

    struct GameState {
        std::array <std::array<int, FIELD_HEIGHT>, FIELD_WIDTH> cells{};
        std::array<int, FIELD_WIDTH> firstEmpty{};
        int currentColor = 1;

        void addToken(int column, int color) {
            cells[column][firstEmpty[column]++] = color;
        }

        void removeToken(int column) {
            cells[column][--firstEmpty[column]] = 0;
        }

        static constexpr std::pair<int, int>
        directions[4] = {
            { 0, 1 },
            { 1, -1 },
            { 1, 0 },
            { 1, 1 }
        };

        int getWinner() const {
            for (int i = 0; i < 4; ++i) {
                auto [dx, dy] = directions[i];
                for (int c = 0; c < FIELD_WIDTH; ++c) {
                    for (int r = 0; r < firstEmpty[c]; ++r) {
                        int color = cells[c][r];
                        int cnt = 0;
                        for (int x = c, y = r;
                             x < FIELD_WIDTH && y >= 0 && y < firstEmpty[x] && cells[x][y] == color;
                             x += dx, y += dy) {
                            ++cnt;
                        }
                        if (cnt == 4) return color;
                    }
                }
            }
            return 0;
        }

        int movesMade() const {
            return std::accumulate(firstEmpty.begin(), firstEmpty.end(), 0);
        }

        long long getCode() const {
            long long res = 0;
            for (int c = 0; c < FIELD_WIDTH; ++c) {
                for (int r = 0; r < firstEmpty[c]; ++r) {
                    if (cells[c][r] == 1) res |= 1LL << (7 * c + r);
                }
                res |= 1LL << (7 * c + firstEmpty[c]);
            }
            return res;
        }
    };

    GameState loadFromCode(long long code) {
        GameState field;
        const long long mask = (1LL << 7) - 1;
        int cnt_tokens = 0;
        for (int c = 0; c < 7; ++c) {
            long long column_code = (code & (mask << (7 * c))) >> (7 * c);
            field.firstEmpty[c] = 6;
            while (!(column_code & (1LL << field.firstEmpty[c]))) {
                --field.firstEmpty[c];
            }
            cnt_tokens += field.firstEmpty[c];

            for (int r = 0; r < field.firstEmpty[c]; ++r) {
                field.cells[c][r] = column_code & (1LL << r) ? 1 : -1;
            }
        }
        field.currentColor = cnt_tokens % 2 == 0 ? 1 : -1;
        return field;
    }

    class Cache {
    private:
        std::map<long long, int> m_cache;
        std::shared_mutex m_mutex;

    public:
        Cache() = default;

        int getWithDefault(long long key, int value) {
            m_mutex.lock_shared();
            auto it = m_cache.find(key);
            if (it != m_cache.end()) value = it->second;
            m_mutex.unlock_shared();
            return value;
        }

        void addRecord(long long key, int value) {
            m_mutex.lock();
            m_cache.emplace(key, value);
            m_mutex.unlock();
        }
    };

    constexpr int MAX_SCORE = 50;

    // minimax with alpha-beta pruning
    int dfs(GameState& position, Cache& cache, int alpha = -MAX_SCORE, int beta = MAX_SCORE) {
        long long code = position.getCode();
        int value = cache.getWithDefault(code, -position.currentColor * MAX_SCORE);
        if (value != -position.currentColor * MAX_SCORE) return value;

        int winner = position.getWinner();
        int moves = position.movesMade();
        if (winner != 0) {
            return winner == 1 ? MAX_SCORE - moves : moves - MAX_SCORE;
        }

        for (int c = 0; c < FIELD_WIDTH; ++c) {
            if (position.firstEmpty[c] == FIELD_HEIGHT) continue;

            position.addToken(c, position.currentColor);
            position.currentColor *= -1;
            int res = dfs(position, cache, alpha, beta);
            position.currentColor *= -1;
            position.removeToken(c);

            if (position.currentColor == 1) {
                value = std::max(value, res);
                if (value > beta) break;
                alpha = std::max(alpha, value);
            } else {
                value = std::min(value, res);
                if (value < alpha) break;
                beta = std::min(beta, value);
            }
        }

        if (moves < 34) cache.addRecord(code, value);
        return value;
    }
}

extern "C" int findBestMove(long long code) {
    using namespace Solver;
    auto position = loadFromCode(code);

    std::vector<std::thread> evalThreads;
    std::vector<std::pair<int, std::future<int>>> evalResults;
    Cache cache;

    for (int c = 0; c < FIELD_WIDTH; ++c) {
        if (position.firstEmpty[c] == FIELD_HEIGHT) continue;
        std::promise<int> valuePromise;
        evalResults.emplace_back(c, valuePromise.get_future());
        evalThreads.emplace_back(
            [promise = std::move(valuePromise), &cache, position, c]() mutable {
                position.addToken(c, position.currentColor);
                position.currentColor *= -1;
                int value = dfs(position, cache);
                promise.set_value(value);
            }
        );
    }

    int optValue = -position.currentColor * MAX_SCORE;
    int optMove = -1;
    for (auto& [col, valueFuture] : evalResults) {
        int value = valueFuture.get();
        if ((position.currentColor == 1 && value > optValue) ||
            (position.currentColor == -1 && value < optValue)) {
            optMove = col;
            optValue = value;
        }
    }

    for (auto& thread : evalThreads) {
        if (thread.joinable()) thread.join();
    }

    return optMove;
}
