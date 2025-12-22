# LOTO6 Predictor

LOTO6（ロト6）の抽選結果を分析し、統計的な予想を生成するStreamlitアプリケーションです。

## 機能

- 📊 過去の抽選結果の統計分析
- 🎯 複数の予想アルゴリズム（ハイブリッド、ホット、コールド、バランス、出現間隔、パターン分析）
- 📈 数字別出現回数と出現間隔の可視化
- 📜 直近の抽選結果履歴表示
- 🔄 データ自動更新機能

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. データの更新

#### 方法1: Node.jsを使用（推奨）

```bash
npm install
npm run update
```

#### 方法2: Pythonを使用

```bash
pip install -r requirements.txt
python update_loto6.py
```

### 3. アプリケーションの起動

```bash
streamlit run loto6_app.py
```

または、バッチファイルを使用：

```bash
# Windows
start.bat
# または
run_app.bat
```

## 使用方法

1. アプリケーションを起動
2. サイドバーから「データ更新」ボタンをクリック（初回または最新データが必要な場合）
3. 予想アルゴリズムを選択
4. 「予想を生成」ボタンをクリック
5. 生成された予想数字を確認

## 予想アルゴリズム

- **ハイブリッド法**: ホット・コールド・ランダムを組み合わせたバランス型
- **ホットナンバー法**: 最近よく出ている数字を重視
- **コールドナンバー法**: 最近出ていない数字を重視
- **バランス法**: 小さい数字と大きい数字をバランスよく選択
- **出現間隔法**: 出現間隔が空いている数字を狙い撃ち
- **パターン分析法**: 過去の傾向に基づくパターンで生成

## ファイル構成

- `loto6_app.py`: メインアプリケーション（Streamlit）
- `update_loto6.py`: データ更新スクリプト
- `loto6_data.js`: 抽選結果データ（JSON形式）
- `loto6_predictor.html`: HTML版の予想ツール（参考実装）
- `requirements.txt`: Python依存パッケージ
- `start.bat`: 起動用バッチファイル
- `run_app.bat`: アプリ実行用バッチファイル

## 技術スタック

### フロントエンド
- HTML/CSS/JavaScript（`loto6_predictor.html` / `index.html`）
- Streamlit（`loto6_app.py`）

### データ更新
- **Node.js版**（推奨）: `update_loto6.js` - GitHub Actionsで自動実行可能
- **Python版**: `update_loto6.py` - ローカル実行用

### 依存パッケージ
- Python: Streamlit, Pandas, Requests, BeautifulSoup4
- Node.js: jsdom

## 注意事項

- このアプリケーションは統計的な分析に基づく予想を提供しますが、当選を保証するものではありません
- 宝くじは運の要素が大きいため、予想結果は参考程度にご利用ください
- データは公式サイトから取得していますが、最新情報は公式サイトでご確認ください

## ライセンス

MIT License

