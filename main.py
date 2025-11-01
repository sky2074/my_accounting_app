import sys
from enum import Enum
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QListWidget,
                             QComboBox, QMessageBox, QWidget, QSizePolicy, QListWidgetItem,
                             QDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPainter, QColor
from PyQt5.QtChart import QChart, QChartView, QPieSeries


class Tag(Enum):
    SALARY = "工资"
    AWARD = "奖金"
    FOOD = "食物"
    CLOTHES = "衣物"
    HOUSE = "住房"
    TRAFFIC = "交通"
    CUSTOM = "自定义标签"


class Record:
    def __init__(self, in_or_out: bool, number: float, tag: Tag, time: str = None, custom_tag: str = ""):
        self.in_or_out = in_or_out
        self.number = number
        self.time = time if time else datetime.now().strftime("%Y-%m-%d %H:%M")
        self.tag = tag
        self.custom_tag = custom_tag

    def get_display_text(self):
        """返回格式化的显示文本"""
        direction = "收入" if self.in_or_out else "支出"
        tag_display = self.custom_tag if self.tag == Tag.CUSTOM and self.custom_tag else self.tag.value
        # 使用固定宽度格式化，确保所有金额占用相同宽度
        return f"{self.time:<16} {direction:>4} {int(self.number):>6}元 {tag_display:>8}"


class AddRecordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("添加记录")
        self.setModal(True)
        self.setGeometry(200, 200, 500, 400)  # 增大子窗口尺寸
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 类型选择
        type_layout = QHBoxLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["收入", "支出"])
        self.type_combo.currentIndexChanged.connect(self.update_tags)
        type_layout.addWidget(QLabel("类型:"))
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # 标签选择
        tag_layout = QHBoxLayout()
        self.tag_combo = QComboBox()
        self.update_tags()
        self.tag_combo.currentIndexChanged.connect(self.on_tag_changed)
        tag_layout.addWidget(QLabel("标签:"))
        tag_layout.addWidget(self.tag_combo)
        layout.addLayout(tag_layout)

        # 自定义标签输入（初始隐藏）
        self.custom_tag_label = QLabel("自定义标签:")
        self.custom_tag_input = QLineEdit()
        self.custom_tag_input.setPlaceholderText("输入自定义标签...")
        self.custom_tag_label.setVisible(False)
        self.custom_tag_input.setVisible(False)
        layout.addWidget(self.custom_tag_label)
        layout.addWidget(self.custom_tag_input)

        # 金额输入
        amount_layout = QHBoxLayout()
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("1-999999")
        amount_layout.addWidget(QLabel("金额(元):"))
        amount_layout.addWidget(self.amount_input)
        layout.addLayout(amount_layout)

        # 时间输入
        time_layout = QHBoxLayout()
        self.time_input = QLineEdit()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.time_input.setText(current_time)
        self.time_input.setPlaceholderText("格式: YYYY-MM-DD HH:MM")
        time_layout.addWidget(QLabel("时间:"))
        time_layout.addWidget(self.time_input)
        layout.addLayout(time_layout)

        # 按钮布局
        button_layout = QHBoxLayout()
        add_button = QPushButton("添加")
        add_button.clicked.connect(self.add_record)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def update_tags(self):
        """更新标签选项"""
        selected_type = self.type_combo.currentText()
        self.tag_combo.clear()

        if selected_type == "收入":
            income_tags = [Tag.SALARY.value, Tag.AWARD.value, Tag.CUSTOM.value]
            self.tag_combo.addItems(income_tags)
        else:
            expense_tags = [Tag.FOOD.value, Tag.CLOTHES.value, Tag.HOUSE.value, Tag.TRAFFIC.value, Tag.CUSTOM.value]
            self.tag_combo.addItems(expense_tags)

    def on_tag_changed(self):
        """标签选择改变时的处理"""
        selected_tag = self.tag_combo.currentText()
        if selected_tag == Tag.CUSTOM.value:
            self.custom_tag_label.setVisible(True)
            self.custom_tag_input.setVisible(True)
        else:
            self.custom_tag_label.setVisible(False)
            self.custom_tag_input.setVisible(False)

    def add_record(self):
        """添加记录"""
        amount_text = self.amount_input.text().strip()
        if not amount_text:
            QMessageBox.warning(self, "输入错误", "请输入金额")
            return

        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
            amount = int(amount)
            if amount > 999999:
                QMessageBox.warning(self, "输入错误", "金额不能超过999999元")
                return
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的正数金额(1-999999)")
            return

        in_or_out = (self.type_combo.currentText() == "收入")
        tag_text = self.tag_combo.currentText()
        if not tag_text:
            QMessageBox.warning(self, "输入错误", "请选择标签")
            return
        tag = self.parent.tag_map.get(tag_text)
        if not tag:
            QMessageBox.warning(self, "输入错误", "无效标签")
            return

        # 处理自定义标签
        custom_tag = ""
        if tag == Tag.CUSTOM:
            custom_tag = self.custom_tag_input.text().strip()
            if not custom_tag:
                QMessageBox.warning(self, "输入错误", "请输入自定义标签")
                return

        time_text = self.time_input.text().strip()
        try:
            if time_text:
                datetime.strptime(time_text, "%Y-%m-%d %H:%M")
            time = time_text if time_text else datetime.now().strftime("%Y-%m-%d %H:%M")
        except ValueError:
            QMessageBox.warning(self, "输入错误", "时间格式应为YYYY-MM-DD HH:MM")
            return

        record = Record(in_or_out, amount, tag, time, custom_tag)
        self.parent.records.append(record)

        # 关闭对话框
        self.accept()


class PieChartDialog(QDialog):
    def __init__(self, records, parent=None):
        super().__init__(parent)
        self.records = records
        self.setWindowTitle("支出占比饼状图")
        self.setModal(True)
        self.setGeometry(100, 100, 800, 600)  # 设置较大的窗口尺寸
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 创建饼图
        chart = QChart()
        chart.setTitle("支出占比饼状图")
        chart.setTitleFont(QFont("Arial", 16, QFont.Bold))

        # 创建饼图系列
        series = QPieSeries()

        # 筛选支出记录并统计
        expense_records = [r for r in self.records if not r.in_or_out]

        if not expense_records:
            # 如果没有支出记录，显示提示
            no_data_label = QLabel("暂无支出数据")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("font-size: 16px; color: gray;")
            layout.addWidget(no_data_label)
        else:
            # 按标签分类统计支出
            tag_expenses = {}
            for record in expense_records:
                tag_name = record.custom_tag if record.tag == Tag.CUSTOM and record.custom_tag else record.tag.value
                if tag_name in tag_expenses:
                    tag_expenses[tag_name] += record.number
                else:
                    tag_expenses[tag_name] = record.number

            # 添加数据到饼图
            colors = [QColor(255, 99, 132), QColor(54, 162, 235), QColor(255, 205, 86),
                      QColor(75, 192, 192), QColor(153, 102, 255), QColor(255, 159, 64),
                      QColor(199, 199, 199), QColor(83, 102, 255), QColor(40, 159, 64)]

            for i, (tag_name, amount) in enumerate(tag_expenses.items()):
                slice = series.append(f"{tag_name}\n{int(amount)}元", amount)
                slice.setColor(colors[i % len(colors)])
                slice.setLabelVisible(True)

            # 设置饼图样式
            series.setHoleSize(0.3)  # 设置空心，形成环形图效果
            chart.addSeries(series)
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignRight)

        # 创建图表视图
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(chart_view)

        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout)


class AccountingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # 先初始化属性
        self.records = []
        self.tag_map = {tag.value: tag for tag in Tag}
        self.current_sort = "time"
        self.sort_asc = True

        # 然后初始化UI
        self.initUI()

        # 设置定时器自动排序
        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_sort_and_filter)
        self.timer.start(200)

    def initUI(self):
        self.setWindowTitle('简易记账本')
        # 增大窗口尺寸
        self.setGeometry(100, 100, 900, 700)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()

        # 本月总盈亏显示 - 增大字体
        self.balance_label = QLabel("本月总盈亏: 计算中...")
        self.balance_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)
        self.balance_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.balance_label)

        # 筛选部分
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("金额筛选:"))

        self.min_amount_input = QLineEdit()
        self.min_amount_input.setPlaceholderText("最小金额")
        self.min_amount_input.textChanged.connect(self.auto_sort_and_filter)
        filter_layout.addWidget(self.min_amount_input)

        filter_layout.addWidget(QLabel("-"))

        self.max_amount_input = QLineEdit()
        self.max_amount_input.setPlaceholderText("最大金额")
        self.max_amount_input.textChanged.connect(self.auto_sort_and_filter)
        filter_layout.addWidget(self.max_amount_input)

        clear_filter_btn = QPushButton("清除筛选")
        clear_filter_btn.clicked.connect(self.clear_filter)
        filter_layout.addWidget(clear_filter_btn)

        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)

        # 排序选项
        sort_layout = QHBoxLayout()
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["按时间排序", "按金额排序"])
        self.sort_combo.currentIndexChanged.connect(self.update_sort)

        self.sort_order_combo = QComboBox()
        self.sort_order_combo.addItems(["升序", "降序"])
        self.sort_order_combo.currentIndexChanged.connect(self.update_sort)

        sort_layout.addWidget(QLabel("排序方式:"))
        sort_layout.addWidget(self.sort_combo)
        sort_layout.addWidget(self.sort_order_combo)

        # 添加饼状图按钮到排序行的右边
        self.pie_chart_btn = QPushButton("饼状图支出占比")
        self.pie_chart_btn.clicked.connect(self.show_pie_chart)
        sort_layout.addWidget(self.pie_chart_btn)

        sort_layout.addStretch()
        main_layout.addLayout(sort_layout)

        # 记录显示部分
        self.record_list = QListWidget()
        font = QFont("Courier New", 9)
        self.record_list.setFont(font)
        self.record_list.setStyleSheet("""
            QListWidget::item { 
                height: 25px; 
                padding: 2px;
            }
        """)
        main_layout.addWidget(self.record_list)

        # 添加记录按钮（底部）
        add_button_layout = QHBoxLayout()
        add_button = QPushButton("+")
        add_button.setFixedSize(60, 60)
        add_button.setStyleSheet("""
            QPushButton {
                font-size: 24px;
                font-weight: bold;
                background-color: #4CAF50;
                color: white;
                border-radius: 30px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_button.clicked.connect(self.open_add_record_dialog)
        add_button_layout.addStretch()
        add_button_layout.addWidget(add_button)
        add_button_layout.addStretch()
        main_layout.addLayout(add_button_layout)

        # 添加表头
        self.refresh_display()

        main_widget.setLayout(main_layout)

    def open_add_record_dialog(self):
        """打开添加记录对话框"""
        dialog = AddRecordDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # 添加成功后刷新显示
            self.auto_sort_and_filter()
            self.update_balance()

    def show_pie_chart(self):
        """显示饼状图对话框"""
        dialog = PieChartDialog(self.records, self)
        dialog.exec_()

    def update_sort(self):
        """排序选项变更时直接触发排序"""
        pass

    def auto_sort_and_filter(self):
        """自动排序和筛选"""
        if not self.records:
            self.refresh_display()
            self.update_balance()
            return

        # 先筛选
        filtered_records = self.filter_records()

        # 再排序
        sort_key = "time" if self.sort_combo.currentIndex() == 0 else "number"
        reverse = self.sort_order_combo.currentIndex() == 1

        if sort_key == "time":
            filtered_records.sort(key=lambda x: x.time, reverse=reverse)
        else:
            filtered_records.sort(key=lambda x: x.number, reverse=reverse)

        self.refresh_display(filtered_records)
        self.update_balance()

    def filter_records(self):
        """根据金额范围筛选记录"""
        min_amount = self.min_amount_input.text().strip()
        max_amount = self.max_amount_input.text().strip()

        filtered = self.records.copy()

        if min_amount:
            try:
                min_val = int(min_amount)
                filtered = [r for r in filtered if r.number >= min_val]
            except ValueError:
                pass

        if max_amount:
            try:
                max_val = int(max_amount)
                filtered = [r for r in filtered if r.number <= max_val]
            except ValueError:
                pass

        return filtered

    def clear_filter(self):
        """清除筛选条件"""
        self.min_amount_input.clear()
        self.max_amount_input.clear()

    def update_balance(self):
        """更新本月总盈亏显示"""
        current_month = datetime.now().strftime("%Y-%m")
        total_income = 0
        total_expense = 0

        for record in self.records:
            if record.time.startswith(current_month):
                if record.in_or_out:
                    total_income += record.number
                else:
                    total_expense += record.number

        balance = total_income - total_expense
        balance_text = f"本月总盈亏: 收入{int(total_income)}元 - 支出{int(total_expense)}元 = {int(balance)}元"

        # 根据盈亏设置颜色
        if balance > 0:
            color = "green"
        elif balance < 0:
            color = "red"
        else:
            color = "black"

        self.balance_label.setText(balance_text)
        self.balance_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
                color: {color};
            }}
        """)

    def refresh_display(self, records=None):
        """刷新显示"""
        if records is None:
            records = self.records

        self.record_list.clear()

        # 添加表头
        header = QListWidgetItem()
        header.setText("时间              类型  金额        标签")
        header.setTextAlignment(Qt.AlignLeft)
        header.setBackground(Qt.lightGray)
        header.setFlags(header.flags() & ~Qt.ItemIsSelectable & ~Qt.ItemIsEnabled)
        self.record_list.addItem(header)

        for record in records:
            item = QListWidgetItem(record.get_display_text())
            item.setTextAlignment(Qt.AlignLeft)
            self.record_list.addItem(item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("Courier New", 9)
    app.setFont(font)
    ex = AccountingApp()
    ex.show()
    sys.exit(app.exec_())