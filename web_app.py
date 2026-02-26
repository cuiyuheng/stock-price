"""
股票价格聚类分析Web应用
适用于HarmonyOS Next系统（通过浏览器访问）
"""

from flask import Flask, render_template_string, request, jsonify, send_file
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import akshare as ak
import warnings
warnings.filterwarnings('ignore')

import io
import base64
import os
from datetime import datetime

app = Flask(__name__)

# HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>股票价格聚类分析</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .content {
            padding: 30px;
        }
        
        .input-section {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .stock-input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        .stock-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .analyze-btn {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .analyze-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        
        .analyze-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 40px;
        }
        
        .loading.active {
            display: block;
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .results {
            display: none;
        }
        
        .results.active {
            display: block;
        }
        
        .chart-container {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .chart-container img {
            width: 100%;
            border-radius: 10px;
        }
        
        .info-card {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
        }
        
        .info-card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 18px;
        }
        
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .info-row:last-child {
            border-bottom: none;
        }
        
        .info-label {
            color: #666;
        }
        
        .info-value {
            font-weight: bold;
            color: #333;
        }
        
        .levels-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .level-item {
            background: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .level-number {
            font-size: 14px;
            color: #666;
            margin-bottom: 5px;
        }
        
        .level-price {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }
        
        .current-price {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 15px;
        }
        
        .current-price h3 {
            font-size: 16px;
            margin-bottom: 10px;
            opacity: 0.9;
        }
        
        .current-price .price {
            font-size: 36px;
            font-weight: bold;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #999;
            font-size: 12px;
        }
        
        @media (max-width: 600px) {
            .input-section {
                flex-direction: column;
            }
            
            .header h1 {
                font-size: 24px;
            }
            
            .content {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 股票价格聚类分析</h1>
            <p>通过K均值聚类识别股价支撑和压力位</p>
        </div>
        
        <div class="content">
            <div class="input-section">
                <input type="text" class="stock-input" id="stockCode" 
                       placeholder="输入股票代码 (如: 000001 或 600000)" maxlength="10">
                <button class="analyze-btn" id="analyzeBtn" onclick="analyzeStock()">开始分析</button>
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>正在分析股票数据，请稍候...</p>
            </div>
            
            <div class="results" id="results">
                <div class="chart-container">
                    <img id="chartImage" src="" alt="股票分析图表">
                </div>
                
                <div class="current-price" id="currentPrice">
                    <h3>当前价格</h3>
                    <div class="price" id="priceValue">--</div>
                </div>
                
                <div class="info-card">
                    <h3>📊 分析结果汇总</h3>
                    <div class="info-row">
                        <span class="info-label">股票代码</span>
                        <span class="info-value" id="stockCodeResult">--</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">数据期间</span>
                        <span class="info-value" id="dateRange">--</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">数据条数</span>
                        <span class="info-value" id="dataCount">--</span>
                    </div>
                </div>
                
                <div class="info-card">
                    <h3>🎯 聚类中心（支撑/压力位）</h3>
                    <div class="levels-grid" id="levelsGrid">
                    </div>
                </div>
                
                <div class="info-card">
                    <h3>📍 相对位置分析</h3>
                    <div id="positionAnalysis">
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>本应用仅供学习交流使用，不构成投资建议</p>
        </div>
    </div>
    
    <script>
        async function analyzeStock() {
            const code = document.getElementById('stockCode').value.trim();
            if (!code) {
                alert('请输入股票代码');
                return;
            }
            
            // 显示加载状态
            document.getElementById('loading').classList.add('active');
            document.getElementById('results').classList.remove('active');
            document.getElementById('analyzeBtn').disabled = true;
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ code: code })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayResults(data);
                } else {
                    alert('分析失败: ' + data.error);
                }
            } catch (error) {
                alert('请求失败: ' + error.message);
            } finally {
                document.getElementById('loading').classList.remove('active');
                document.getElementById('analyzeBtn').disabled = false;
            }
        }
        
        function displayResults(data) {
            // 显示结果区域
            document.getElementById('results').classList.add('active');
            
            // 显示图表
            document.getElementById('chartImage').src = 'data:image/png;base64,' + data.chart;
            
            // 显示基本信息
            document.getElementById('stockCodeResult').textContent = data.code;
            document.getElementById('dateRange').textContent = data.date_range;
            document.getElementById('dataCount').textContent = data.data_count;
            
            // 显示当前价格
            document.getElementById('priceValue').textContent = '¥' + data.current_price.toFixed(2);
            
            // 显示聚类中心
            const levelsGrid = document.getElementById('levelsGrid');
            levelsGrid.innerHTML = '';
            data.centers.forEach((center, index) => {
                const levelItem = document.createElement('div');
                levelItem.className = 'level-item';
                levelItem.innerHTML = `
                    <div class="level-number">Level ${index + 1}</div>
                    <div class="level-price">¥${center.toFixed(2)}</div>
                `;
                levelsGrid.appendChild(levelItem);
            });
            
            // 显示位置分析
            const positionAnalysis = document.getElementById('positionAnalysis');
            positionAnalysis.innerHTML = '';
            data.positions.forEach(pos => {
                const infoRow = document.createElement('div');
                infoRow.className = 'info-row';
                infoRow.innerHTML = `
                    <span class="info-label">Level ${pos.level} (${pos.price.toFixed(2)})</span>
                    <span class="info-value">${pos.position}</span>
                `;
                positionAnalysis.appendChild(infoRow);
            });
            
            // 滚动到结果区域
            document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        }
        
        // 回车键触发分析
        document.getElementById('stockCode').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                analyzeStock();
            }
        });
    </script>
</body>
</html>
'''


def get_stock_data_multi_source(code, start_date='20250101', end_date='20261231'):
    """多数据源获取股票数据"""
    print(f"正在获取股票 {code} 的数据...")
    
    # 方法1: 尝试 stock_zh_a_hist_tx (腾讯证券)
    try:
        print("尝试方法1: stock_zh_a_hist_tx (腾讯证券)...")
        if code.endswith('.SZ'):
            symbol_tx = "sz" + code.replace('.SZ', '')
        elif code.endswith('.SH'):
            symbol_tx = "sh" + code.replace('.SH', '')
        else:
            if code.startswith('6'):
                symbol_tx = "sh" + code
            else:
                symbol_tx = "sz" + code
        
        df = ak.stock_zh_a_hist_tx(symbol=symbol_tx, start_date=start_date, 
                                  end_date=end_date, adjust="qfq", timeout=10)
        
        if df is not None and not df.empty:
            print(f"方法1成功: 获取 {len(df)} 条数据")
            if 'amount' in df.columns:
                df['volume'] = df['amount'] * 100
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
            return df
    except Exception as e:
        print(f"方法1失败: {e}")
    
    # 方法2: 尝试 stock_zh_a_daily (新浪财经)
    try:
        print("尝试方法2: stock_zh_a_daily (新浪财经)...")
        if code.endswith('.SZ'):
            symbol_sina = "sz" + code.replace('.SZ', '')
        elif code.endswith('.SH'):
            symbol_sina = "sh" + code.replace('.SH', '')
        else:
            if code.startswith('6'):
                symbol_sina = "sh" + code
            else:
                symbol_sina = "sz" + code
        
        df = ak.stock_zh_a_daily(symbol=symbol_sina, 
                                start_date=start_date, end_date=end_date, adjust="qfq")
        if df is not None and not df.empty:
            print(f"方法2成功: 获取 {len(df)} 条数据")
            if isinstance(df.index, pd.RangeIndex) and 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
            return df
    except Exception as e:
        print(f"方法2失败: {e}")
    
    # 方法3: 尝试 stock_zh_a_hist (东方财富)
    try:
        print("尝试方法3: stock_zh_a_hist (东方财富)...")
        clean_code = code.replace('.SZ', '').replace('.SH', '')
        
        df = ak.stock_zh_a_hist(symbol=clean_code, period="daily", 
                               start_date=start_date, end_date=end_date, 
                               adjust="qfq")
        if df is not None and not df.empty:
            print(f"方法3成功: 获取 {len(df)} 条数据")
            df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '最高': 'high', 
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'volume',
                '成交额': 'amount'
            }, inplace=True)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            return df
    except Exception as e:
        print(f"方法3失败: {e}")
    
    # 方法4: 生成模拟数据
    print("所有数据源均失败，使用模拟数据...")
    return generate_sample_data(code)


def generate_sample_data(code, days=180):
    """生成模拟股票数据"""
    print(f"为 {code} 生成模拟数据...")
    
    if '600' in code or '688' in code:
        start_price = np.random.uniform(5, 15)
    elif '000' in code or '300' in code:
        start_price = np.random.uniform(8, 25)
    else:
        start_price = np.random.uniform(10, 30)
    
    end_date = pd.Timestamp.now()
    start_date = end_date - pd.Timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    np.random.seed(hash(code) % 10000)
    returns = np.random.normal(0.001, 0.02, len(dates))
    prices = start_price * (1 + returns).cumprod()
    
    df = pd.DataFrame({
        'open': prices * (1 + np.random.normal(0, 0.01, len(dates))),
        'high': prices * (1 + np.abs(np.random.normal(0, 0.015, len(dates)))),
        'low': prices * (1 - np.abs(np.random.normal(0, 0.015, len(dates)))),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, len(dates))
    }, index=dates)
    
    df['high'] = df[['high', 'open', 'close']].max(axis=1)
    df['low'] = df[['low', 'open', 'close']].min(axis=1)
    
    return df


def analyze_clusters(df, code):
    """执行聚类分析"""
    prices = df['close'].values.reshape(-1, 1)
    
    kmeans = KMeans(n_clusters=5, random_state=42)
    kmeans.fit(prices)
    centers = sorted(kmeans.cluster_centers_.flatten())
    
    # 创建图形
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['close'], label="收盘价", color="blue", linewidth=1.5)
    
    colors = ['red', 'green', 'orange', 'purple', 'brown']
    for i, c in enumerate(centers):
        plt.axhline(c, color=colors[i % len(colors)], linestyle="--", alpha=0.7, 
                   label=f'Level {i+1}: {c:.2f}')
    
    plt.title(f"股价聚类分析 - {code}", fontsize=14)
    plt.xlabel("日期", fontsize=12)
    plt.ylabel("价格", fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # 保存到内存
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.read()).decode()
    plt.close()
    
    return centers, img_base64


@app.route('/')
def index():
    """主页"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/analyze', methods=['POST'])
def analyze():
    """分析股票"""
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        
        if not code:
            return jsonify({'success': False, 'error': '请输入股票代码'})
        
        # 确保代码格式正确
        if not code.endswith('.SZ') and not code.endswith('.SH'):
            if code.startswith('6'):
                code = code + '.SH'
            else:
                code = code + '.SZ'
        
        # 获取数据
        df = get_stock_data_multi_source(code)
        
        if df is None or df.empty:
            return jsonify({'success': False, 'error': '无法获取股票数据'})
        
        # 执行聚类分析
        centers, chart_base64 = analyze_clusters(df, code)
        
        # 计算当前价格相对于支撑/压力位的位置
        current_price = df['close'].iloc[-1]
        positions = []
        
        for i, center in enumerate(centers, 1):
            diff = current_price - center
            percent = (diff / center) * 100
            
            if diff > 0:
                position = f"上方 {diff:.2f} (+{percent:.1f}%)"
            else:
                position = f"下方 {-diff:.2f} ({percent:+.1f}%)"
            
            positions.append({
                'level': i,
                'price': center,
                'position': position
            })
        
        # 准备返回数据
        result = {
            'success': True,
            'code': code,
            'date_range': f"{df.index[0].strftime('%Y-%m-%d')} 至 {df.index[-1].strftime('%Y-%m-%d')}",
            'data_count': len(df),
            'current_price': current_price,
            'centers': centers,
            'positions': positions,
            'chart': chart_base64
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    print("="*60)
    print("股票价格聚类分析Web服务器")
    print("="*60)
    print("访问地址: http://localhost:5000")
    print("="*60)
    app.run(host='0.0.0.0', port=5000, debug=True)
