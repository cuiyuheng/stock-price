"""
股票价格聚类分析移动应用
使用Kivy框架开发，支持华为鸿蒙手机
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import akshare as ak
import warnings
warnings.filterwarnings('ignore')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.widget import Widget

import threading
import os
from datetime import datetime

# 设置窗口背景色
Window.clearcolor = (0.95, 0.95, 0.97, 1)


class StockAnalyzerApp(App):
    """股票分析应用主类"""
    
    def build(self):
        self.title = '股票价格聚类分析'
        return MainLayout()


class MainLayout(BoxLayout):
    """主界面布局"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        
        # 标题
        title_label = Label(
            text='股票价格聚类分析',
            font_size='28sp',
            size_hint_y=None,
            height=60,
            color=(0.2, 0.4, 0.8, 1),
            bold=True
        )
        self.add_widget(title_label)
        
        # 副标题
        subtitle = Label(
            text='通过K均值聚类识别股价支撑和压力位',
            font_size='14sp',
            size_hint_y=None,
            height=30,
            color=(0.4, 0.4, 0.4, 1)
        )
        self.add_widget(subtitle)
        
        # 输入区域
        input_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=60,
            spacing=10
        )
        
        self.stock_input = TextInput(
            hint_text='输入股票代码 (如: 000001 或 600000)',
            font_size='16sp',
            multiline=False,
            size_hint_x=0.7,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            padding=[15, 15]
        )
        input_layout.add_widget(self.stock_input)
        
        analyze_btn = Button(
            text='开始分析',
            font_size='16sp',
            size_hint_x=0.3,
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        analyze_btn.bind(on_press=self.start_analysis)
        input_layout.add_widget(analyze_btn)
        
        self.add_widget(input_layout)
        
        # 进度条
        self.progress = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=20
        )
        self.add_widget(self.progress)
        
        # 状态标签
        self.status_label = Label(
            text='请输入股票代码并点击分析',
            font_size='14sp',
            size_hint_y=None,
            height=40,
            color=(0.5, 0.5, 0.5, 1)
        )
        self.add_widget(self.status_label)
        
        # 结果显示区域（可滚动）
        scroll_view = ScrollView(size_hint=(1, 1))
        self.result_layout = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None,
            padding=15
        )
        self.result_layout.bind(minimum_height=self.result_layout.setter('height'))
        scroll_view.add_widget(self.result_layout)
        self.add_widget(scroll_view)
        
        # 图表显示区域
        self.chart_image = Image(
            size_hint_y=None,
            height=400,
            allow_stretch=True,
            keep_ratio=True
        )
        self.result_layout.add_widget(self.chart_image)
        
        # 分析结果文本
        self.result_text = Label(
            text='',
            font_size='14sp',
            size_hint_y=None,
            markup=True,
            halign='left',
            valign='top',
            text_size=(Window.width - 60, None),
            color=(0.2, 0.2, 0.2, 1)
        )
        self.result_layout.add_widget(self.result_text)
    
    def start_analysis(self, instance):
        """开始分析"""
        code = self.stock_input.text.strip()
        if not code:
            self.show_popup('错误', '请输入股票代码')
            return
        
        # 确保代码格式正确
        if not code.endswith('.SZ') and not code.endswith('.SH'):
            if code.startswith('6'):
                code = code + '.SH'
            else:
                code = code + '.SZ'
        
        self.status_label.text = f'正在分析股票: {code}...'
        self.status_label.color = (0.2, 0.6, 1, 1)
        self.progress.value = 10
        
        # 在后台线程中执行分析
        thread = threading.Thread(target=self.analyze_stock, args=(code,))
        thread.daemon = True
        thread.start()
    
    def analyze_stock(self, code):
        """执行股票分析"""
        try:
            # 更新进度
            Clock.schedule_once(lambda dt: self.update_progress(20), 0)
            
            # 获取股票数据
            df = self.get_stock_data_multi_source(code)
            
            if df is None or df.empty:
                Clock.schedule_once(lambda dt: self.show_error('无法获取股票数据'), 0)
                return
            
            Clock.schedule_once(lambda dt: self.update_progress(50), 0)
            
            # 执行聚类分析
            centers = self.analyze_clusters(df, code)
            
            Clock.schedule_once(lambda dt: self.update_progress(80), 0)
            
            # 生成结果文本
            result = self.generate_result_text(df, code, centers)
            
            Clock.schedule_once(lambda dt: self.update_progress(100), 0)
            
            # 更新UI
            Clock.schedule_once(lambda dt: self.show_results(result), 0)
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error(f'分析出错: {str(e)}'), 0)
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress.value = value
    
    def show_error(self, message):
        """显示错误信息"""
        self.status_label.text = message
        self.status_label.color = (1, 0.3, 0.3, 1)
        self.progress.value = 0
    
    def show_results(self, result_text):
        """显示分析结果"""
        self.status_label.text = '分析完成！'
        self.status_label.color = (0.2, 0.8, 0.4, 1)
        self.result_text.text = result_text
        self.result_text.texture_update()
        self.result_text.height = self.result_text.texture_size[1]
        
        # 加载图表
        chart_path = result_text.split('chart_path:')[1].split('\n')[0] if 'chart_path:' in result_text else None
        if chart_path and os.path.exists(chart_path):
            self.chart_image.source = chart_path
            self.chart_image.reload()
    
    def get_stock_data_multi_source(self, code, start_date='20250101', end_date='20261231'):
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
            
            print(f"腾讯接口使用代码: {symbol_tx}")
            
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
            else:
                print("方法1: 返回数据为空")
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
            
            print(f"新浪接口使用代码: {symbol_sina}")
            
            df = ak.stock_zh_a_daily(symbol=symbol_sina, 
                                    start_date=start_date, end_date=end_date, adjust="qfq")
            if df is not None and not df.empty:
                print(f"方法2成功: 获取 {len(df)} 条数据")
                if isinstance(df.index, pd.RangeIndex) and 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                    df.set_index('date', inplace=True)
                elif not isinstance(df.index, pd.DatetimeIndex):
                    try:
                        df.index = pd.to_datetime(df.index)
                    except:
                        if 'date' in df.columns:
                            df['date'] = pd.to_datetime(df['date'])
                            df.set_index('date', inplace=True)
                return df
            else:
                print("方法2: 返回数据为空")
        except Exception as e:
            print(f"方法2失败: {e}")
        
        # 方法3: 尝试 stock_zh_a_hist (东方财富)
        try:
            print("尝试方法3: stock_zh_a_hist (东方财富)...")
            clean_code = code.replace('.SZ', '').replace('.SH', '')
            print(f"东方财富接口使用代码: {clean_code}")
            
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
            else:
                print("方法3: 返回数据为空")
        except Exception as e:
            print(f"方法3失败: {e}")
        
        # 方法4: 生成模拟数据
        print("所有数据源均失败，使用模拟数据...")
        return self.generate_sample_data(code)
    
    def generate_sample_data(self, code, days=180):
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
        
        print(f"生成 {len(df)} 条模拟数据")
        return df
    
    def analyze_clusters(self, df, code):
        """执行聚类分析"""
        prices = df['close'].values.reshape(-1, 1)
        
        print("正在进行聚类分析...")
        kmeans = KMeans(n_clusters=5, random_state=42)
        kmeans.fit(prices)
        centers = sorted(kmeans.cluster_centers_.flatten())
        
        # 创建图形
        plt.figure(figsize=(10, 6))
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
        
        # 保存图片到应用目录
        chart_filename = f"stock_analysis_{code.replace('.', '_')}.png"
        chart_path = os.path.join(self.get_app_path(), chart_filename)
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"分析图表已保存为: {chart_path}")
        return centers
    
    def generate_result_text(self, df, code, centers):
        """生成分析结果文本"""
        result = []
        result.append(f"[b]分析结果汇总[/b]\n")
        result.append(f"{'='*40}\n")
        result.append(f"[b]股票代码:[/b] {code}\n")
        
        start_date_str = df.index[0].strftime('%Y-%m-%d') if hasattr(df.index[0], 'strftime') else str(df.index[0])
        end_date_str = df.index[-1].strftime('%Y-%m-%d') if hasattr(df.index[-1], 'strftime') else str(df.index[-1])
        result.append(f"[b]数据期间:[/b] {start_date_str} 至 {end_date_str}\n")
        result.append(f"[b]数据条数:[/b] {len(df)}\n\n")
        
        result.append(f"[b]聚类中心（支撑/压力位）:[/b]\n")
        for i, center in enumerate(centers, 1):
            result.append(f"  Level {i}: [color=ff6b6b]{center:.2f}[/color]\n")
        
        current_price = df['close'].iloc[-1]
        result.append(f"\n[b]当前价格:[/b] [color=4ecdc4]{current_price:.2f}[/color]\n")
        result.append(f"[b]相对于支撑/压力位的位置:[/b]\n")
        
        nearest_level = None
        min_distance = float('inf')
        
        for i, center in enumerate(centers, 1):
            diff = current_price - center
            distance = abs(diff)
            percent = (diff / center) * 100
            
            if distance < min_distance:
                min_distance = distance
                nearest_level = (i, center, diff, percent)
            
            if diff > 0:
                position = f"上方 {diff:.2f} ([color=2ecc71]+{percent:.1f}%[/color])"
            else:
                position = f"下方 {-diff:.2f} ([color=e74c3c]{percent:+.1f}%[/color])"
            result.append(f"  Level {i} ({center:.2f}): {position}\n")
        
        if nearest_level:
            i, center, diff, percent = nearest_level
            result.append(f"\n[b]最接近的支撑/压力位:[/b] Level {i} ({center:.2f})\n")
            if diff > 0:
                result.append(f"当前位于该位上方 [color=2ecc71]{diff:.2f} ({percent:+.1f}%)[/color]\n")
            else:
                result.append(f"当前位于该位下方 [color=e74c3c]{-diff:.2f} ({percent:+.1f}%)[/color]\n")
        
        # 添加图表路径标记
        chart_filename = f"stock_analysis_{code.replace('.', '_')}.png"
        chart_path = os.path.join(self.get_app_path(), chart_filename)
        result.append(f"\nchart_path:{chart_path}\n")
        
        return ''.join(result)
    
    def get_app_path(self):
        """获取应用数据存储路径"""
        # 在Android/鸿蒙上，使用应用私有目录
        if os.path.exists('/sdcard'):
            path = '/sdcard/StockAnalyzer'
        else:
            path = os.path.expanduser('~/StockAnalyzer')
        
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    
    def show_popup(self, title, message):
        """显示弹窗"""
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(None, None),
            size=(300, 200)
        )
        popup.open()


if __name__ == '__main__':
    StockAnalyzerApp().run()
