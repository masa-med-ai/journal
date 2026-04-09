# 📚 Daily Journal Digest

PubMed から消化器内視鏡・消化器病学の最新論文を毎朝3本 AI 選定し、
日本語臨床解説 HTML メールとして配信する GitHub Actions ワークフローです。

---

## フォルダ構成

```
gi-journal-digest/
├── .github/
│   └── workflows/
│       └── daily-journal-digest.yml   ← GitHub Actions ワークフロー本体
├── digest/
│   ├── render_email.py                ← papers.json → HTML メール変換スクリプト
│   ├── email_template.html            ← メール HTML テンプレート
│   ├── mailing_list.txt               ← 配信先メールアドレス一覧 ★要編集
│   └── journal_digest_database.csv   ← 紹介済み論文の重複防止データベース（自動更新）
└── README.md
```

---

## セットアップ手順

### Step 1 — リポジトリ作成

GitHub で新しいリポジトリを作成し、このフォルダの中身をそのままプッシュします。

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
git push -u origin main
```

### Step 2 — Secrets の登録

リポジトリの **Settings → Secrets and variables → Actions → New repository secret** で以下を登録します。

| Secret 名 | 内容 |
|-----------|------|
| `CLAUDE_CODE_OAUTH_TOKEN` | Claude Code の OAuth トークン（後述） |
| `GMAIL_USER` | 送信元 Gmail アドレス（例: `yourname@gmail.com`） |
| `GMAIL_APP_PASSWORD` | Gmail アプリパスワード（後述） |

#### CLAUDE_CODE_OAUTH_TOKEN の取得方法

1. [Claude Code](https://claude.ai/download) をインストールしてターミナルから `claude` を起動
2. ブラウザで認証後、以下のコマンドでトークンを確認します：
   ```bash
   cat ~/.claude/.credentials.json
   ```
3. `claudeAiOauthToken` の値をコピーして Secret に登録

> **注意**: トークンは個人アカウントに紐づきます。有効期限が切れた場合は再ログインして更新してください。

#### Gmail アプリパスワードの取得方法

アプリパスワードは、通常の Google パスワードとは別に発行する16桁の専用パスワードです。
2段階認証が有効なアカウントでのみ使用できます。

**① Google アカウントで 2段階認証を有効化する**

まだ設定していない場合は以下の手順で有効化してください。

1. [https://myaccount.google.com/security](https://myaccount.google.com/security) を開く
2. 「Google へのログイン方法」→「2段階認証プロセス」をクリック
3. 画面の指示に従って設定（SMS または Google 認証アプリを推奨）

**② アプリパスワードを発行する**

1. [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) を開く
   - 2段階認証が有効でないとこのページは表示されません
2. 「アプリを選択」→ **「メール」** を選ぶ
3. 「デバイスを選択」→ **「その他（名前を入力）」** を選び、任意の名前（例: `GitHub Actions`）を入力
4. **「生成」** ボタンをクリック
5. 黄色いボックスに表示される **16桁のパスワード**（スペースなし）をコピー

> ⚠️ このパスワードは一度しか表示されません。コピーしたらすぐに Secret に登録してください。

**③ GitHub Secret に登録する**

1. GitHub リポジトリの **Settings → Secrets and variables → Actions**
2. **New repository secret** をクリック
3. Name: `GMAIL_APP_PASSWORD`、Secret: コピーした16桁のパスワードを貼り付け
4. **Add secret** をクリック

> **注意**: Gmail の「安全性の低いアプリのアクセス」（旧機能）は廃止されています。
> 必ずアプリパスワードを使用してください。

### Step 3 — 配信先の設定

`digest/mailing_list.txt` を編集して配信先を追加します：

```
# 1行に1アドレス。# はコメント行。
yourname@gmail.com
colleague@hospital.ac.jp
```

変更後は `git commit & push` するだけで反映されます。

### Step 4 — 動作確認（手動実行）

GitHub の **Actions タブ → Daily Journal Digest → Run workflow** で手動実行できます。
初回はログを確認しながら動作を検証することをおすすめします。

---

## 自動実行スケジュール

デフォルトは **毎朝 7:00 JST**（UTC 22:00）です。
変更する場合は `.github/workflows/daily-journal-digest.yml` の `cron` 行を編集してください。

```yaml
# 例: 毎朝 6:30 JST に変更する場合
- cron: '30 21 * * *'
```

---

## カスタマイズポイント

- **対象ジャーナルの変更**: ワークフロー内の `prompt` セクションのジャーナルリストを編集
- **選定基準の変更**: `prompt` の「論文選定」セクションを書き換え
- **メール件名の変更**: `subject:` の行を変更（`📚 Journal Digest — ...`）
- **HTML デザインの変更**: `digest/email_template.html` を編集

---

## GitHub Actions × Claude Code の仕組み

このワークフローは **`anthropics/claude-code-action`** を使って GitHub Actions の中で Claude Code を動かしています。

```
GitHub Actions ランナー（ubuntu-latest）
  └─ anthropics/claude-code-action@v1
       └─ Claude Code（claude-sonnet-4-6）
            ├─ PubMed MCP サーバーを起動（npx pubmed_mcp_server2）
            ├─ PubMed を検索（mcp__pubmed__search_pubmed）
            ├─ 論文を選定・解説文を生成
            └─ papers.json + CSV を書き出し
```

### claude-code-action の主なパラメータ

```yaml
uses: anthropics/claude-code-action@v1
with:
  claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}

  # Claude に渡す自然言語プロンプト
  prompt: |
    ...

  # Claude Code の起動オプション
  claude_args: |
    --model claude-sonnet-4-6       # 使用モデル
    --max-turns 25                  # 最大ターン数（ツール呼び出し回数の上限）
    --allowedTools Read,Write,...   # 許可するツール（セキュリティのため明示）
    --mcp-config '{"mcpServers":{...}}'  # MCP サーバー設定
```

### MCP（Model Context Protocol）とは

Claude Code が外部サービス（PubMed など）と通信するための拡張プロトコルです。
このワークフローでは `pubmed_mcp_server2`（npm パッケージ）を起動し、
`mcp__pubmed__search_pubmed` ツールとして Claude から呼び出せるようにしています。

### `--allowedTools` によるセキュリティ管理

CI 環境では意図しないコマンド実行を防ぐため、許可するツールを明示的に列挙します。
`Bash(python3:*)` のように括弧で実行コマンドを絞ることも可能です。

---

## トラブルシューティング

**papers.json が生成されない**
→ Actions ログで Claude Code のステップを確認。`CLAUDE_CODE_OAUTH_TOKEN` が期限切れの可能性があります。

**メールが届かない**
→ `GMAIL_USER` / `GMAIL_APP_PASSWORD` の設定を確認。Gmail の「安全性の低いアプリのアクセス」ではなくアプリパスワードを使用してください。

**同じ論文が繰り返し紹介される**
→ `digest/journal_digest_database.csv` が正しくコミットされているか確認してください。

---

## ライセンス

MIT
