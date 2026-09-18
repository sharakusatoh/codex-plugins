# e-Gov法令API Version 2

原文で指定された3種類のActionsを、公式HTTP APIへ接続する補助スクリプトに対応させています。Python 3.9以降の標準ライブラリだけで動作します。APIキーは不要で、検索・取得のみを行います。

このファイルの位置からスキルの実際のインストール先を求め、scripts/egov.pyを絶対パスで実行してください。以下のコマンドはスキルのディレクトリを作業場所にした例です。

| 原文のActions | コマンド | API |
| --- | --- | --- |
| searchLawsByKeyword(keyword) | search | GET /keyword |
| getLawData(id, response_format=json) | law | GET /law_data/{id} |
| listLawRevisions(id) | revisions | GET /law_revisions/{id} |

## 法令の特定

必要な法律用語だけで検索し、候補とlaw_id、revision_infoを確認します。検索語に相談者の個人情報を含める必要はありません。

```sh
python scripts/egov.py search "意思表示" --limit 5
python scripts/egov.py search "民法" --title --limit 5
```

--titleは法令一覧APIのlaw_title検索を使います。候補数・next_offsetを確認し、追加の候補が必要な場合だけ--offsetを指定して取得します。検索の既定値は10件相当、指定可能な上限は50です。本文キーワード検索のlimitはヒット位置数の上限であり、返る法令数とは一致しないことがあります。検索結果の抜粋は条文全体ではありません。

## 条文と対象時点

```sh
python scripts/egov.py law 129AC0000000089 --elm "MainProvision-Article[1]"
python scripts/egov.py law 129AC0000000089 --asof 2024-04-01 --elm "MainProvision-Article[1]"
```

条文が特定できる場合は--elmで必要な部分だけを取得します。法令全体が必要な場合だけ--elmを省略します。取得量が大きいときは--output law.jsonを付けてファイルに保存し、関係する部分を確認してください。全コマンドが--outputに対応します。保存先の親フォルダは既存のものを指定します。

```sh
python scripts/egov.py revisions 129AC0000000089 --output revisions.json
```

履歴から対象のlaw_revision_idを選び、lawコマンドのIDに渡すと、その履歴の本文を取得できます。履歴ID指定時には--asofはAPI側で無視されます。施行日、履歴の状態、改正情報を確認し、未施行の改正を現行法と混同しないでください。

原文どおり、取得した法令名・可能なら法令番号・条項を回答に示し、一次情報へリンクします。APIの取得失敗はエラーと終了コード1で報告します。失敗や検索0件を根拠に条文を推測しないでください。利用環境でPythonまたはネットワークを使用できない場合は、利用可能な公式サイトの閲覧手段で確認するか、取得できない範囲を明示します。

仕様は[e-Gov法令API公式ドキュメント](https://laws.e-gov.go.jp/api/2/swagger-ui/)を参照してください。実装時にVersion 2.1.139を確認しました。本文JSONは公式仕様上の試行版のため、応答形式に変更があった場合は公式仕様に合わせて更新します。
