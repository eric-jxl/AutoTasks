import csv
import io
from datetime import datetime, date


def to_text(source):
    if source is None or source is False:
        return ''
    if isinstance(source, bytes):
        return source.decode('utf-8')
    if isinstance(source, str):
        return source
    return str(source)


class ExportCsvWriter:

    def __init__(self, field_names):
        """
        初始化CSV导出工具
        :param field_names: 列名列表
        """
        self.field_names = field_names
        self.output = io.StringIO()
        self.writer = csv.DictWriter(self.output, fieldnames=self.field_names)
        self.value = None

    def __enter__(self):
        self.write_header()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def write_header(self):
        """
        写入CSV文件的表头
        """
        self.writer.writeheader()

    def write_row(self, row_data):
        """
        写入单行数据
        :param row_data: 字典形式的一行数据
        """
        processed_row = {key: self.process_cell(value)
                         for key, value in row_data.items()}
        self.writer.writerow(processed_row)

    def close(self):
        """
        关闭并保存到输出
        """
        self.value = self.output.getvalue()
        self.output.close()

    def process_cell(self, cell_value):
        """
        处理单元格数据
        :param cell_value: 单元格的值
        :return: 处理后的值
        """
        if isinstance(cell_value, bytes):
            try:
                return to_text(cell_value)
            except UnicodeDecodeError:
                raise ValueError(f"Binary fields cannot be exported to CSV unless their content is base64-encoded.")
        if isinstance(cell_value, (date, datetime)):
            return cell_value.isoformat()
        return to_text(cell_value)


class CsvExport:
    @property
    def content_type(self):
        """
        内容类型
        """
        return 'text/csv'

    @property
    def extension(self):
        """
        文件扩展名
        """
        return '.csv'

    def from_data(self, fields, rows):
        """
        从数据中生成CSV内容
        :param fields: 列名列表
        :param rows: 数据行列表，每行是一个字典
        :return: CSV文件内容
        """
        with ExportCsvWriter(fields) as csv_writer:
            for row in rows:
                csv_writer.write_row(row)

        return csv_writer.value

if __name__ == '__main__':
    fields = ['name', 'age', 'gender']
    rows = [
        {'name': 'Alice', 'age': 25, 'gender': 'Female'},
        {'name': 'Bob', 'age': 30, 'gender': 'Male'},
        {'name': 'Charlie', 'age': 35, 'gender': 'Male'}
    ]
    CsvExport().from_data(fields, rows)