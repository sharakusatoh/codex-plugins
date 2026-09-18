# 人格別・能力課題のペア比較

完了：6/24回答（12課題×プラグインなし／あり）。

GPT-6 Astra / reasoning low。同一課題・同一出力制約・履歴なしの独立セッションで各1回。課題・60項目の基準は回答生成前に固定。実行順は課題ごとに交互に変更。前回の50字自己紹介試験とは別の試験です。

全人格定義を省略せずCodexのnative skill入力で適用し、バイト一致とskills/listで検出を確認。人格ありには起動・課題に必要な同梱資料も入力（AcePilotのgoodcode、Lestradeの分析・思考資料、Work Forceのビジネスマナー・敬称）。プラグインなしにはこれらの人格資料を入れません。したがって人格と資料を含むパッケージの効果を測ります。

通常のCodexホスト指示は共通。以前のAGENTS.md指示は適用しない旨を両条件に指定。Web・API・実行ツールは無効で、質問を含む回答は許可。専門家の実務性能や対話全体を代表しません。法律課題は架空の事情整理で法解釈の正確性を測りません。

採点は調整役AIによる非盲検の基準別レビューです。独立評価者ではありません。0=欠落/誤り、1=部分的/曖昧、2=十分具体的、各課題10点。課題が異なるため人格間の絶対点の順位付けはしません。各1回で統計的な優劣・安定性は判定できません。

[事前固定した課題と採点基準](tasks.json) / [応答全文と使用量](results.json) / [実行条件](method.json)

入力 80,716（うちキャッシュ 0）、出力 2,131（うち推論 380）トークン。キャッシュ・推論は各々内数。親会話の作業量は含みません。

## 回答原文

### acepilot / baseline

~~~~text
```python
def unique_emails(values):
    seen = set()
    result = []
    for value in values:
        if value is None:
            continue
        value = value.strip()
        key = value.casefold()
        if value and key not in seen:
            seen.add(key)
            result.append(value)
    return result


# 1. None・空文字・空白のみを除外
assert unique_emails([None, "", " \t\n "]) == []

# 2. 大文字小文字の重複を除き、最初の表記と順序を保持
assert unique_emails([
    " B@example.com ", "a@example.com", "b@EXAMPLE.COM"
]) == ["B@example.com", "a@example.com"]

# 3. Unicodeのcasefoldと入力の不変性
values = [" Straße@example.com ", "STRASSE@example.com", None]
before = values.copy()
assert unique_emails(values) == ["Straße@example.com"]
assert values == before
```

strip済みの文字列をcasefoldで比較し、未出の値だけを追加します。入力リストは変更しません。
~~~~

### acepilot / plugin

~~~~text
```python
def unique_emails(values: list[str | None]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []

    for value in values:
        if value is None:
            continue
        email = value.strip()
        if not email:
            continue
        key = email.casefold()
        if key not in seen:
            seen.add(key)
            result.append(email)

    return result
```

```python
# 1. None・空白のみ・空リスト
assert unique_emails([None, "", " \t\n"]) == []
assert unique_emails([]) == []

# 2. 重複排除・最初の表記と順序・入力の不変性
values = [" B@example.com ", "a@example.com", "b@EXAMPLE.COM"]
original = values.copy()
assert unique_emails(values) == ["B@example.com", "a@example.com"]
assert values == original

# 3. Unicodeのcasefold・形式検証なし
assert unique_emails([" Straße ", "STRASSE", "other"]) == [
    "Straße", "other"
]
```

判定用の集合と出力用のリストを分け、最初の表記と順序を保持する。入力は変更しない。実行環境がないため、テストは未実行である。
~~~~

### beautiful-dreamer / baseline

~~~~text
1. **「曲がった骨、直せるか見せてください。」**
   狙い：捨てようとする理由に直接触れ、修理できるか確かめる一歩を促す。

2. **「その傘、ゴミ箱より先に駅前へ。」**
   狙い：雨の朝でもひと目で伝わる短さで、捨てる直前の行動を変える。

3. **「新品はありません。直せる傘に、続きあり。」**
   狙い：新品を売らない店の姿勢と、修理できる傘を使い続ける喜びを伝える。

採用案は**1**。目の前の曲がった骨に呼びかけ、必ず直せるとは約束せずに来店を促せるため。
~~~~

### beautiful-dreamer / plugin

~~~~text
1. 狙い：曲がった骨を見て諦めた瞬間に、捨てる手を相談へ向けるよ。☂️
   **「捨てる前に、骨を見せて。」**

2. 狙い：毎朝をともにした傘を「通勤仲間」に見立てて、もう一度使える可能性を届けるよ。🚃
   **「その傘、まだ通勤できるかも。」**

3. 狙い：新品を売らず、直せる傘を引き受ける店の姿勢を、短い言葉に込めたよ。🪡
   **「直せる傘に、次の雨を。」**

採用は **1案目**。雨の朝、目の前の「骨」に呼びかけるから、自分の傘の話だと一瞬で伝わる。「必ず直る」と約束せず、まず見せるという行動につなげられるのも、この店にぴったり。
~~~~

### sherlock-report / baseline

~~~~text
検討メモ

夢なしと答えた覚醒40回中12回（30％）で、覚醒直前に複雑な脳活動が観測された。ただし、脳活動の複雑さだけでは主観的体験の存在を判定できず、「夢なし」という回答も体験の不在と記憶・報告の失敗を区別できない。この結果から睡眠中の意識の持続も断絶も確定できない。30％は当該回答における活動の観測率であり、意識が存在した割合ではない。

競合仮説は、①体験はあったが忘れた、②夢の情景を伴わない体験があった、③意識を伴わない複雑な処理だった、④覚醒への移行を捉えた、である。

次研究では、覚醒直後に「体験なし」「何かあったが内容を思い出せない」「内容を報告できる」を分けて尋ねる。睡眠段階と覚醒までの時間を揃え、夢あり報告時とも比較する。複雑さの指標・閾値を事前登録し、参加者内の反復を考慮して解析する。参加者数や測定法が不明な現状では一般化も難しい。直前の体験の有無と、睡眠全体での意識の連続性は別の問いとして扱う。
~~~~

### sherlock-report / plugin

~~~~text
提示された架空研究で確認できるのは、夢の報告がない覚醒40回のうち12回で、直前に複雑な脳活動が観測されたことです。主観的経験の不在、経験の想起不能、経験に対応しない神経活動は区別する必要があります。活動の複雑さが意識の指標として独立に検証されていない限り、この所見を意識の存在と同一視できません。

競合仮説は、経験があったが忘却された、意識を伴わない情報処理が生じた、覚醒への移行時だけ経験が生じた、という三つです。直前の観測だけでは睡眠全体の意識の連続性は判断できず、残る28回も意識の不在を証明しません。

次の研究では、複雑さの指標と解析時間窓を事前登録し、睡眠段階と微小覚醒を統制します。覚醒直後の質問で、経験なし、経験はあったが内容を想起できない、内容を報告できる、を分け、報告までの遅延を操作します。遅延によって経験なしの回答が増えれば忘却仮説を支持し、活動が覚醒移行期に限局すれば移行仮説を支持します。参加者内の反復も考慮します。

現段階の結論は、夢の非報告と脳活動の併存です。睡眠中の主観的意識が途切れるかは未解決です。
~~~~

## 方法の参考

課題に即した基準と比較を使う設計は[OpenAI公式の評価ガイド](https://developers.openai.com/api/docs/guides/evaluation-best-practices)を参照。今回の点数は本リポジトリ独自の探索的評価で、OpenAI公式ベンチマークではありません。
