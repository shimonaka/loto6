/**
 * LOTO6 データ更新スクリプト (Node.js版)
 * Python版のupdate_loto6.pyをJavaScriptに変換
 */

const https = require('https');
const http = require('http');
const { URL } = require('url');
const fs = require('fs');
const { JSDOM } = require('jsdom');

const BASE_URL = "https://www.ohtashp.com/topics/takarakuji/loto6/";
const MAX_RETRIES = 3;

/**
 * 年ごとのURLを取得
 */
function getUrlForYear(year) {
  const currentYear = new Date().getFullYear();
  if (year === currentYear) {
    return BASE_URL;
  } else {
    return `${BASE_URL}index_${year}.html`;
  }
}

/**
 * HTTPリクエストを送信
 */
function fetchUrl(url) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const client = urlObj.protocol === 'https:' ? https : http;
    
    const options = {
      hostname: urlObj.hostname,
      path: urlObj.pathname + urlObj.search,
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    };

    const req = client.request(options, (res) => {
      let data = '';
      
      // エンコーディングを検出
      let encoding = 'utf8';
      if (res.headers['content-type']) {
        const charsetMatch = res.headers['content-type'].match(/charset=([^;]+)/i);
        if (charsetMatch) {
          encoding = charsetMatch[1].toLowerCase();
        }
      }

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        // エンコーディング変換（簡易版）
        if (encoding.includes('shift') || encoding.includes('sjis')) {
          // Shift-JISの場合はiconv-liteが必要だが、多くの場合はUTF-8で問題ない
          console.warn(`Warning: Encoding ${encoding} may not be handled correctly`);
        }
        resolve({ statusCode: res.statusCode, data });
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    req.setTimeout(15000, () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });

    req.end();
  });
}

/**
 * HTMLをパースしてデータを抽出
 */
function parseHtml(html, year) {
  const dom = new JSDOM(html);
  const document = dom.window.document;
  const results = [];
  const tables = document.querySelectorAll('table');
  
  const currentYearResults = [];
  
  tables.forEach((table) => {
    const rows = table.querySelectorAll('tr');
    
    rows.forEach((row) => {
      const cols = row.querySelectorAll('td, th');
      if (cols.length < 8) {
        return;
      }
      
      const data = Array.from(cols).map(col => col.textContent.trim());
      
      // 回号のパターンチェック（第\d+回）
      if (!/第\d+回/.test(data[0])) {
        return;
      }
      
      // 日付のパターンチェック
      if (!/\d+/.test(data[1])) {
        return;
      }
      
      try {
        // 回号を抽出
        const roundMatch = data[0].match(/(\d+)/);
        if (!roundMatch) {
          return;
        }
        const roundNum = parseInt(roundMatch[1], 10);
        
        // 日付
        const dateStr = data[1];
        
        // 数字を抽出（Cols 2-7）
        const numbers = [];
        let validRow = true;
        
        for (let i = 2; i < 8; i++) {
          const textVal = data[i].replace(/\D/g, '');
          if (!textVal) {
            validRow = false;
            break;
          }
          numbers.push(parseInt(textVal, 10));
        }
        
        if (!validRow) {
          return;
        }
        
        // ボーナス数字（Col 8）
        const bonusText = data[8] ? data[8].replace(/\D/g, '') : '';
        const bonus = bonusText ? parseInt(bonusText, 10) : 0;
        
        const item = {
          round: roundNum,
          date: dateStr,
          numbers: numbers,
          bonus: bonus
        };
        
        // 重複チェック
        if (!currentYearResults.some(r => r.round === roundNum)) {
          currentYearResults.push(item);
        }
      } catch (error) {
        // パースエラーは無視
        return;
      }
    });
  });
  
  console.log(`  Parsed ${currentYearResults.length} records for ${year}.`);
  return currentYearResults;
}

/**
 * 年ごとのデータを取得
 */
async function fetchAndParse(year) {
  const url = getUrlForYear(year);
  console.log(`Fetching data for ${year} from ${url}...`);
  
  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      const response = await fetchUrl(url);
      
      if (response.statusCode === 404) {
        console.log(`  404 Not Found for ${year}. Skipping.`);
        return [];
      }
      
      if (response.statusCode !== 200) {
        console.log(`  Status ${response.statusCode} for ${year}. Retrying...`);
        await sleep(2000);
        continue;
      }
      
      return parseHtml(response.data, year);
    } catch (error) {
      console.log(`  Error fetching ${year} (Attempt ${attempt + 1}): ${error.message}`);
      await sleep(2000);
    }
  }
  
  return [];
}

/**
 * 既存のデータを読み込み
 */
function loadExistingData() {
  if (!fs.existsSync('loto6_data.js')) {
    return [];
  }
  
  try {
    const content = fs.readFileSync('loto6_data.js', 'utf8');
    const jsonStr = content.replace('const LOTO6_DATA = ', '').trim().replace(/;$/, '');
    return JSON.parse(jsonStr);
  } catch (error) {
    console.log(`Error loading existing data: ${error.message}`);
    return [];
  }
}

/**
 * スリープ関数
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * メイン処理
 */
async function main() {
  const existingData = loadExistingData();
  console.log(`Loaded ${existingData.length} existing records.`);
  
  const today = new Date();
  const currentYear = today.getFullYear();
  let startYear = 2000;
  
  // 既存データから開始年を決定
  if (existingData.length > 0) {
    const latestDateStr = existingData[0].date; // 降順ソート済み
    try {
      const latestYear = parseInt(latestDateStr.split('/')[0], 10);
      startYear = latestYear;
      console.log(`Incremental update: Starting from ${startYear}`);
    } catch (error) {
      // エラーは無視
    }
  }
  
  console.log(`Starting scrape from ${startYear} to ${currentYear}...`);
  
  const fetchedData = [];
  for (let y = startYear; y <= currentYear; y++) {
    const yearData = await fetchAndParse(y);
    fetchedData.push(...yearData);
    await sleep(1000); // レート制限対策
  }
  
  // マージ: 既存データ + 取得データ（重複排除）
  const uniqueMap = {};
  existingData.forEach(item => {
    uniqueMap[item.round] = item;
  });
  
  fetchedData.forEach(item => {
    uniqueMap[item.round] = item;
  });
  
  const uniqueData = Object.values(uniqueMap);
  
  // 回号で降順ソート
  uniqueData.sort((a, b) => b.round - a.round);
  
  console.log(`Total unique records: ${uniqueData.length}`);
  
  if (uniqueData.length > 0) {
    console.log(`Latest: Round ${uniqueData[0].round} (${uniqueData[0].date})`);
  }
  
  // JSファイルに保存
  const jsContent = `const LOTO6_DATA = ${JSON.stringify(uniqueData, null, 2)};`;
  
  fs.writeFileSync('loto6_data.js', jsContent, 'utf8');
  
  console.log('Successfully saved to loto6_data.js');
}

// 実行
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

module.exports = { main };

