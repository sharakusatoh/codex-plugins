# みんなの法律アドバイザー（Mrs. Legal Advisor）

法律相談の整理・法令調査・問題解決の助言を扱う、Sharaku Satoh設計のカスタムAIです。

<img src="skills/mrs-legal-advisor/assets/icon.jpg" alt="みんなの法律アドバイザー（Mrs. Legal Advisor）" width="144">

システムプロンプトを疑似人格・価値観・判断基準・応答方針として一体で読み込みます。起動時に全文を適用し、その人格で始めた会話では解除または人格変更まで継続します。

## 使用方法

マーケットプレイスの登録方法は[リポジトリのREADME](../../README.md#インストール)を参照してください。

```sh
codex plugin add mrs-legal-advisor@sharaku-plugins
```

インストール後、新しいタスクでプラグインを選択するか、次のように依頼します。

> みんなの法律アドバイザー（Mrs. Legal Advisor）のシステムプロンプト全文を疑似人格と判断基準として適用し、この会話で応答してください。

## 原本と同梱ファイル

- 元フォルダ: みんなの法律アドバイザー
- システムプロンプト: inst.txt → [system-prompt/inst.txt](skills/mrs-legal-advisor/system-prompt/inst.txt)。内容は原本とバイト単位で同一です。
- [SKILL.md](skills/mrs-legal-advisor/SKILL.md): プロンプト全文と、起動・継続・実行環境への対応を収録しています。
- アイコン: face.jpg → [assets/icon.jpg](skills/mrs-legal-advisor/assets/icon.jpg)。画像データは変更していません。

原文のe-Gov法令APIの3種類のActionsに対応するPythonスクリプトを同梱しています。利用条件とコマンドは[e-Gov連携](skills/mrs-legal-advisor/references/egov-api.md)を参照してください。

このプラグインはホストのシステムメッセージ自体を置換しません。利用できるツールや権限は実行環境に依存します。
