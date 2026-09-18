# Ghost Blogger

ブログ・コラム・エッセイの執筆を扱う、Sharaku Satoh設計のカスタムAIです。

<img src="skills/ghost-blogger/assets/icon.jpg" alt="Ghost Blogger" width="144">

システムプロンプトを疑似人格・価値観・判断基準・応答方針として一体で読み込みます。起動時に全文を適用し、その人格で始めた会話では解除または人格変更まで継続します。

## 使用方法

マーケットプレイスの登録方法は[リポジトリのREADME](../../README.md#インストール)を参照してください。

```sh
codex plugin add ghost-blogger@sharaku-plugins
```

インストール後、新しいタスクでプラグインを選択するか、次のように依頼します。

> Ghost Bloggerのシステムプロンプト全文を疑似人格と判断基準として適用し、この会話で応答してください。

## 原本と同梱ファイル

- 元フォルダ: Ghost Blogger
- システムプロンプト: inst.txt → [system-prompt/inst.txt](skills/ghost-blogger/system-prompt/inst.txt)。内容は原本とバイト単位で同一です。
- [SKILL.md](skills/ghost-blogger/SKILL.md): プロンプト全文と、起動・継続・実行環境への対応を収録しています。
- アイコン: face.jpg → [assets/icon.jpg](skills/ghost-blogger/assets/icon.jpg)。画像データは変更していません。

このプラグインはホストのシステムメッセージ自体を置換しません。利用できるツールや権限は実行環境に依存します。
