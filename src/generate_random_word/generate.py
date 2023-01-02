import random
import typing


def generate(ttl: int, sentence: str) -> str:

    mp: typing.Dict[str, typing.List[str]] = {}
    tokens = sentence.split()
    for index, token in enumerate(tokens):
        if index < len(tokens) - 1:
            successive = tokens[index + 1]
            if token in mp.keys():
                mp[token].append(successive)
            else:
                mp[token] = [successive]
        elif token not in mp.keys():
            # special case 如果最后一个单词没有任何其余的 successive
            mp[token] = []

    # 你写的有问题因为如果选择到的当前单词如果没有 successive，但是 output 又不满足长度是需要重新 draw 的
    # 所以正确的写法应该是一个 dfs 搜索
    output = []
    result = dfs(output, ttl, mp)
    if result is None:
        raise ValueError("NOT FOUND")

    return " ".join(result)


def draw_token(tokens: typing.List[str]) -> str:
    return tokens[random.randint(0, len(tokens) - 1)]


def dfs(cur: typing.List[str], ttl: int,
        mp: typing.Dict[str, typing.List[str]]) -> typing.List[str] | None:
    if len(cur) == ttl:  # base case
        return cur

    if len(cur) == 0:
        tokens = list(mp.keys())
    else:
        previous_token = cur[-1]
        tokens = mp[previous_token]
        if len(tokens) == 0:  # invalid previous value
            return None

    cur = cur.copy()
    cur.append(draw_token(tokens))
    visited: typing.Set[str] = set()
    visited.add(cur[-1])
    result = dfs(cur, ttl, mp)
    while result is None:
        if visited == set(tokens):
            return None
        new_entry = draw_token(tokens)
        while new_entry in visited:

            new_entry = draw_token(tokens)
        visited.add(new_entry)
        cur[-1] = new_entry
        result = dfs(cur, ttl, mp)

    return result


text = "this is a sentence it is not a good one and it is also bad"

print(generate(5, text))