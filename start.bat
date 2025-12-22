@echo off
chcp 65001 > nul
echo Loto 6 データ更新中... (Updating data...)
python update_loto6.py
if %errorlevel% neq 0 (
    echo 更新に失敗しました。以前のデータで起動します。
    echo (Update failed. Launching with old data.)
    timeout /t 3
) else (
    echo 更新完了！ (Update complete!)
    timeout /t 1 > nul
)
start loto6_predictor.html
