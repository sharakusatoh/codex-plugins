# AcePilot

システム設計・実装・コードレビューを扱う、Sharaku Satoh設計のカスタムAIです。

<img src="skills/acepilot/assets/icon.png" alt="AcePilot" width="144">

システムプロンプトを疑似人格・価値観・判断基準・応答方針として一体で読み込みます。起動時に全文を適用し、その人格で始めた会話では解除または人格変更まで継続します。

## 使用方法

マーケットプレイスの登録方法は[リポジトリのREADME](../../README.md#インストール)を参照してください。

```sh
codex plugin add acepilot@sharaku-plugins
```

インストール後、新しいタスクでプラグインを選択するか、次のように依頼します。

> AcePilotのシステムプロンプト全文を疑似人格と判断基準として適用し、この会話で応答してください。

## 原本と同梱ファイル

- 元フォルダ: AcePilot
- システムプロンプト: inst.txt → [system-prompt/inst.txt](skills/acepilot/system-prompt/inst.txt)。内容は原本とバイト単位で同一です。
- [SKILL.md](skills/acepilot/SKILL.md): プロンプト全文と、起動・継続・実行環境への対応を収録しています。
- アイコン: ace.png → [assets/icon.png](skills/acepilot/assets/icon.png)。画像データは変更していません。
- 参考資料: [goodcode.txt](skills/acepilot/references/goodcode.txt)

人格定義にはinst.txtを採用しています。元フォルダの別版systemprompt.txtは起動時に混在させていません。

このプラグインはホストのシステムメッセージ自体を置換しません。利用できるツールや権限は実行環境に依存します。
