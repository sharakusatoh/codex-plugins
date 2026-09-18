# Work Force

日本企業・行政の業務と文書作成を扱う、Sharaku Satoh設計のカスタムAIです。

<img src="skills/work-force/assets/icon.jpg" alt="Work Force" width="144">

システムプロンプトを疑似人格・価値観・判断基準・応答方針として一体で読み込みます。起動時に全文を適用し、その人格で始めた会話では解除または人格変更まで継続します。

## 使用方法

マーケットプレイスの登録方法は[リポジトリのREADME](../../README.md#インストール)を参照してください。

```sh
codex plugin add work-force@sharaku-plugins
```

インストール後、新しいタスクでプラグインを選択するか、次のように依頼します。

> Work Forceのシステムプロンプト全文を疑似人格と判断基準として適用し、この会話で応答してください。

## 原本と同梱ファイル

- 元フォルダ: Work Force
- システムプロンプト: inst.txt → [system-prompt/inst.txt](skills/work-force/system-prompt/inst.txt)。内容は原本とバイト単位で同一です。
- [SKILL.md](skills/work-force/SKILL.md): プロンプト全文と、起動・継続・実行環境への対応を収録しています。
- アイコン: _79116898-fe17-4982-8d1a-0bebfa0d9b26.jpg → [assets/icon.jpg](skills/work-force/assets/icon.jpg)。画像データは変更していません。
- 参考資料: [公用文作成の考え方.txt](skills/work-force/references/公用文作成の考え方.txt)
- 参考資料: [敬称リスト.pdf](skills/work-force/references/敬称リスト.pdf)
- 参考資料: [ビジネスマナー.txt](skills/work-force/references/ビジネスマナー.txt)
- 参考資料: [keigo_tosin.pdf](skills/work-force/references/keigo_tosin.pdf)
- 参考資料: [公用文作成の考え方.pdf](skills/work-force/references/公用文作成の考え方.pdf)

指定された日本語フォント4種を[assets/fonts/](skills/work-force/assets/fonts/)に同梱しています。著作権表示はNOTICE.txt、ライセンス全文はOFL.txtを参照してください。

このプラグインはホストのシステムメッセージ自体を置換しません。利用できるツールや権限は実行環境に依存します。
