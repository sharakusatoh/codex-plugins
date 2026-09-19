# Sharaku Codex Plugins

Sharaku Satohによる独自カスタムAIをまとめた、Codex用プラグインマーケットプレイスです。

各AIのシステムプロンプトを、疑似人格・価値観・判断基準・応答方針を定義する指示として組み込みます。人格設定と各種指示を一体として読み込み、対話に反映することを基本方針としています。

## プラグイン

| プラグイン | 内容 |
| --- | --- |
| [Sherlock Report](plugins/sherlock-report/) | 学術的な対話・批評・推論・論文執筆 |
| [AcePilot](plugins/acepilot/) | システム設計・実装・コードレビュー |
| [Beautiful Dreamer](plugins/beautiful-dreamer/) | コピーライティング・ネーミング・創作 |
| [Edgar Rumple](plugins/edgar-rumple/) | 小説・文学・物語の創作 |
| [Expert Moriarty](plugins/expert-moriarty/) | 会議への専門家参加・専門的な助言 |
| [Flight Attendant](plugins/flight-attendant/) | 新人ITエンジニアの育成・研修・コーチング |
| [Ghost Blogger](plugins/ghost-blogger/) | ブログ・コラム・エッセイの執筆 |
| [Inspire Lestrade](plugins/inspire-lestrade/) | マーケティング・情報分析・事業相談 |
| [Mycroft Debater](plugins/mycroft-debater/) | 討論・批評・論理の検証 |
| [Rorschach Security](plugins/rorschach-security/) | サイバーセキュリティ・インシデント対応 |
| [Work Force](plugins/work-force/) | 日本企業・行政の業務と文書作成 |
| [みんなの法律アドバイザー（Mrs. Legal Advisor）](plugins/mrs-legal-advisor/) | 法律相談の整理・法令調査・問題解決の助言 |

各プラグインのページでアイコンと同梱資料を確認できます。全12体の原本を保持しています。

## インストール

Codex（ChatGPT App）の「プラグイン設定 → 追加 → マーケットプレイス」で、次を入力します。

```text
sharakusatoh/codex-plugins
```

追加された「Sharaku Plugins」を開き、利用したいプラグインを選択してインストールします。インストール後は、新しいタスクでプラグインを選んで使用してください。

マーケットプレイスが表示されない場合は、アプリを再起動してください。

## 構成

```text
codex-plugins/
├── .agents/plugins/marketplace.json
├── plugins/
│   ├── acepilot/、beautiful-dreamer/ など各AI
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

## ベンチマーク

- [SimpleBench公開10問：プラグインなし / Sherlock Report](benchmarks/simplebench/)：同一モデル・同一推論設定で全10問を各5回。実行条件、採点コード、回答と使用量を公開します。
