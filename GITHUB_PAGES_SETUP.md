# GitHub Pages公開手順

## 概要

LOTO6 PredictorをGitHub Pagesで公開する手順です。

## 方法1: GitHub Actionsを使用（推奨）

### ステップ1: GitHub Pagesを有効化

1. GitHubリポジトリ（https://github.com/shimonaka/loto6）にアクセス
2. **Settings** → **Pages** を開く
3. **Source** で **GitHub Actions** を選択
4. 保存

### ステップ2: ワークフローファイルをコミット

`.github/workflows/deploy-pages.yml` が既に作成されています。

```bash
cd C:\Users\shimo\Desktop\miyabi\Miyabi\loto6
git add .github/workflows/deploy-pages.yml
git add index.html
git commit -m "feat: Add GitHub Pages deployment"
git push
```

### ステップ3: デプロイの確認

1. GitHubリポジトリの **Actions** タブを開く
2. ワークフローが実行されるのを待つ
3. 完了後、**Settings** → **Pages** で公開URLを確認

**公開URL**: `https://shimonaka.github.io/loto6/`

## 方法2: 手動でGitHub Pagesを有効化

### ステップ1: index.htmlをルートに配置

`loto6_predictor.html` を `index.html` にコピー（既に作成済み）

### ステップ2: GitHub Pagesを有効化

1. GitHubリポジトリの **Settings** → **Pages** を開く
2. **Source** で **Deploy from a branch** を選択
3. **Branch** で `main` を選択
4. **Folder** で `/ (root)` を選択
5. **Save** をクリック

### ステップ3: 公開URLを確認

数分後、以下のURLでアクセスできます：

**公開URL**: `https://shimonaka.github.io/loto6/`

## 注意事項

### データファイルのサイズ

`loto6_data.js` は約328KBと大きいため、GitHub Pagesで読み込むのに時間がかかる場合があります。

### データの更新

GitHub PagesではPythonスクリプト（`update_loto6.py`）を実行できないため、データを更新するには：

1. ローカルで `update_loto6.py` を実行
2. 更新された `loto6_data.js` をコミット&プッシュ
3. GitHub Pagesが自動的に更新される

### 自動更新（オプション）

GitHub Actionsで定期的にデータを更新するワークフローを追加することもできます。

## トラブルシューティング

### データが読み込まれない

- `loto6_data.js` が正しくコミットされているか確認
- ブラウザのコンソールでエラーを確認
- ファイルパスが正しいか確認（`<script src="loto6_data.js"></script>`）

### ページが表示されない

- GitHub Pagesの設定を確認
- Actionsタブでエラーがないか確認
- 数分待ってから再度アクセス

## 確認方法

1. 公開URLにアクセス: https://shimonaka.github.io/loto6/
2. ページが正しく表示されるか確認
3. データが読み込まれているか確認（最新データ日が表示されるか）
4. 予想生成機能が動作するか確認

