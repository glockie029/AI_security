"""原 Attention/Causal Mask 演示，运行时才导入 NumPy。"""


def main():
    import numpy as np

    # 假设一句话由 4 个 Token 组成
    tokens = ["我", "正在", "学习", "安全"]

    # 模拟 Attention 分数
    scores = np.array([
        [1, 2, 3, 4],
        [2, 1, 3, 4],
        [3, 2, 1, 4],
        [4, 3, 2, 1],
    ], dtype=float)

    # 上三角掩码：屏蔽未来 Token
    mask = np.triu(
        np.ones_like(scores, dtype=bool),
        k=1
    )

    scores[mask] = -np.inf

    # Softmax
    exp_scores = np.exp(
        scores - np.max(scores, axis=-1, keepdims=True)
    )

    weights = exp_scores / exp_scores.sum(
        axis=-1, keepdims=True
    )

    print("Attention 权重：")
    print(np.round(weights, 3))


if __name__ == "__main__":
    main()
