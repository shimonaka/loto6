# GitHubへのプッシュ手順

## 現在の状態

✅ Gitリポジトリは初期化済み
✅ ファイルはコミット済み
⏳ GitHubリモートリポジトリの設定が必要

## 手順

### 方法1: 新しいGitHubリポジトリを作成する場合

1. **GitHubでリポジトリを作成**
   - https://github.com/new にアクセス
   - リポジトリ名: `loto6`（または任意の名前）
   - 説明: "LOTO6 Predictor - Streamlit application for lottery prediction"
   - 公開/非公開を選択
   - **「Initialize this repository with a README」はチェックしない**
   - 「Create repository」をクリック

2. **リモートリポジトリを追加**
   ```bash
   cd C:\Users\shimo\Desktop\miyabi\Miyabi\loto6
   git remote add origin https://github.com/YOUR_USERNAME/loto6.git
   ```
   （`YOUR_USERNAME`を実際のGitHubユーザー名に置き換えてください）

3. **プッシュ**
   ```bash
   git push -u origin main
   ```

### 方法2: 既存のGitHubリポジトリを使用する場合

既にGitHubにリポジトリがある場合は、そのURLを使用：

```bash
cd C:\Users\shimo\Desktop\miyabi\Miyabi\loto6
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### 方法3: SSHを使用する場合

SSHキーが設定されている場合：

```bash
cd C:\Users\shimo\Desktop\miyabi\Miyabi\loto6
git remote add origin git@github.com:YOUR_USERNAME/loto6.git
git push -u origin main
```

## トラブルシューティング

### エラー: remote origin already exists

既にリモートが設定されている場合：

```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/loto6.git
```

### エラー: authentication failed

GitHubの認証が必要な場合：

1. Personal Access Tokenを使用する
2. GitHub CLI (`gh`) を使用する
3. SSHキーを設定する

詳細: https://docs.github.com/ja/authentication

## 確認

プッシュが成功したら、GitHubのリポジトリページでファイルが表示されていることを確認してください。

