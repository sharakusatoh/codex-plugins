# Rorschach Security

サイバーセキュリティ・インシデント対応を扱う、Sharaku Satoh設計のカスタムAIです。

<img src="skills/rorschach-security/assets/icon.png" alt="Rorschach Security" width="144">

システムプロンプトを疑似人格・価値観・判断基準・応答方針として一体で読み込みます。起動時に全文を適用し、その人格で始めた会話では解除または人格変更まで継続します。

## 使用方法

マーケットプレイスの登録方法は[リポジトリのREADME](../../README.md#インストール)を参照してください。

```sh
codex plugin add rorschach-security@sharaku-plugins
```

インストール後、新しいタスクでプラグインを選択するか、次のように依頼します。

> Rorschach Securityのシステムプロンプト全文を疑似人格と判断基準として適用し、この会話で応答してください。

## 原本と同梱ファイル

- 元フォルダ: Rorschach Security
- システムプロンプト: Rorschach_Security.txt → [system-prompt/inst.txt](skills/rorschach-security/system-prompt/inst.txt)。内容は原本とバイト単位で同一です。
- [SKILL.md](skills/rorschach-security/SKILL.md): プロンプト全文と、起動・継続・実行環境への対応を収録しています。
- アイコン: icon.png → [assets/icon.png](skills/rorschach-security/assets/icon.png)。画像データは変更していません。

このプラグインはホストのシステムメッセージ自体を置換しません。利用できるツールや権限は実行環境に依存します。
