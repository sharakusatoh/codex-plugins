# Sherlock Report

Sharaku Satoh設計の学術特化カスタムAIを、人格と判断基準を統合するプラグインとして移植したものです。

## 使い始める

インストール後、新しいタスクでSherlock Reportを選択するか、次のように指定してください。

「Sherlock Reportのシステムプロンプト全文を疑似人格と判断基準として適用し、この会話で応答してください。」

人格を起動すると、システムプロンプトの全節を読み込んで対話を開始し、同じ会話内では解除または人格変更まで適用を続けます。プラグインのインストールだけで、すべての会話の人格が切り替わるわけではありません。

## 収録内容

- skills/sherlock-report/SKILL.md：起動・継続の指示、環境への対応、システムプロンプト全文。
- skills/sherlock-report/system-prompt/inst.txt：指定された日本語システムプロンプトの原本。
- skills/sherlock-report/references/prism_description.txt：同じ元フォルダのPrism参考資料。
- skills/sherlock-report/assets/sherlockreport_logo2.png：指定されたアイコン。
- skills/sherlock-report/agents/openai.yaml：スキルの表示名、アイコン、開始用プロンプト。

システムプロンプト原本、参考資料、アイコンはバイト単位で元ファイルと一致します。原本全文は起動時に読み込まれるSKILL.mdにも直接収録しています。

## 実装上の範囲

「カスタムAIのシステムプロンプト」という役割をスキルとして実装しています。ホスト側のシステム指示や権限を置換するものではありません。疑似人格の適用と指示の反映はモデルの指示追従に依存し、完全な強制はできません。モデルとreasoning effortもこのプラグインから固定しません。

CanvasやPythonなどの機能は、利用できる環境に合わせて扱います。Canvasがない場合は編集可能な文書ファイルを使用します。必要な機能が使えない場合は、その制約を説明します。

元のGPTとの応答の同一性は未検証です。実際の対話で人格、判断、文体、確認手順を比較して調整してください。
