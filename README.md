# Sharaku Codex Plugins

Sharaku Satohによる独自カスタムAIをまとめた、Codex用プラグインマーケットプレイスです。

各AIのシステムプロンプトを、疑似人格・価値観・判断基準・応答方針を定義する指示として組み込みます。人格設定と各種指示を一体として読み込み、対話に反映することを基本方針としています。

## プラグイン

| プラグイン | 内容 |
| --- | --- |
| [Sherlock Report](plugins/sherlock-report/) | 学術分野に特化したカスタムAI。学術的な対話、批評、推論、論文・レポート作成を扱います。 |

<img src="plugins/sherlock-report/skills/sherlock-report/assets/sherlockreport_logo2.png" alt="Sherlock Report" width="144">

## インストール

Codex CLIで、このリポジトリをマーケットプレイスとして追加します。

```sh
codex plugin marketplace add sharakusatoh/codex-plugins --ref main
```

続いて、利用するプラグインをインストールします。

```sh
codex plugin add sherlock-report@sharaku-plugins
```

インストール後は新しいタスクを開き、Sherlock Reportを選択するか、次のように依頼してください。

> Sherlock Reportのシステムプロンプト全文を疑似人格と判断基準として適用し、この会話で応答してください。

アプリのプラグイン一覧では「Sharaku Plugins」がマーケットプレイス名です。表示されない場合はアプリを再起動してください。

## 更新

```sh
codex plugin marketplace upgrade sharaku-plugins
codex plugin add sherlock-report@sharaku-plugins
```

更新後は新しいタスクで使用してください。

## 構成

```text
codex-plugins/
├── .agents/plugins/marketplace.json
├── plugins/
│   └── sherlock-report/
│       ├── .codex-plugin/plugin.json
│       ├── README.md
│       └── skills/sherlock-report/
│           ├── SKILL.md
│           ├── system-prompt/inst.txt
│           ├── references/
│           ├── assets/
│           └── agents/openai.yaml
└── README.md
```

## プラグインの追加

1. `plugins/<plugin-name>/` にプラグインを配置します。フォルダ名とマニフェストの `name` を一致させます。
2. `.agents/plugins/marketplace.json` の `plugins` 配列末尾にエントリを追加し、`source.path` を `./plugins/<plugin-name>` にします。
3. マニフェスト、スキル、参照ファイル、アイコンを検証し、このREADMEのプラグイン一覧に追加します。

新しいエントリには `policy.installation: AVAILABLE`、`policy.authentication: ON_INSTALL`、`category` を設定します。プラグインを更新する場合は、変更内容に応じてバージョンも更新します。

カスタムAIの移植では、システムプロンプトの原本を保存し、その全文を起動時に読み込む構成を維持します。詳細は [AGENTS.md](AGENTS.md) を参照してください。

仕様・配布方法は [OpenAI公式ドキュメント](https://developers.openai.com/plugins/build/plugins) を参照してください。
