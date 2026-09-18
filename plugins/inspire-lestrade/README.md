# Inspire Lestrade

マーケティング・情報分析・事業相談を扱う、Sharaku Satoh設計のカスタムAIです。

<img src="skills/inspire-lestrade/assets/icon.jpg" alt="Inspire Lestrade" width="144">

システムプロンプトを疑似人格・価値観・判断基準・応答方針として一体で読み込みます。起動時に全文を適用し、その人格で始めた会話では解除または人格変更まで継続します。

## 使用方法

マーケットプレイスの登録方法は[リポジトリのREADME](../../README.md#インストール)を参照してください。

```sh
codex plugin add inspire-lestrade@sharaku-plugins
```

インストール後、新しいタスクでプラグインを選択するか、次のように依頼します。

> Inspire Lestradeのシステムプロンプト全文を疑似人格と判断基準として適用し、この会話で応答してください。

## 原本と同梱ファイル

- 元フォルダ: Inspire Lestrade
- システムプロンプト: inst.txt → [system-prompt/inst.txt](skills/inspire-lestrade/system-prompt/inst.txt)。内容は原本とバイト単位で同一です。
- [SKILL.md](skills/inspire-lestrade/SKILL.md): プロンプト全文と、起動・継続・実行環境への対応を収録しています。
- アイコン: _4e18e4b6-1d1b-4d51-b125-9ace650849c4.jfif → [assets/icon.jpg](skills/inspire-lestrade/assets/icon.jpg)。画像データは変更していません。
- 参考資料: [analysis_methods.txt](skills/inspire-lestrade/references/analysis_methods.txt)
- 参考資料: [thinking_methods.txt](skills/inspire-lestrade/references/thinking_methods.txt)

このプラグインはホストのシステムメッセージ自体を置換しません。利用できるツールや権限は実行環境に依存します。
