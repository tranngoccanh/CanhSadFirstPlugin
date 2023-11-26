from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from qgis.core import QgsRectangle, QgsFeatureRequest, QgsVectorLayer, QgsVectorFileWriter, QgsProject

# Tên của lớp plugin
class MyPlugin:

    def __init__(self, iface):
        # Lưu trữ tham chiếu đến giao diện QGIS
        self.iface = iface

    # Phương thức chính được gọi khi plugin được kích hoạt
    def initGui(self):
        # Tạo một action để kích hoạt plugin
        self.action = QAction("My Plugin", self.iface.mainWindow())
        self.action.triggered.connect(self.run)

        # Thêm action vào thanh công cụ
        self.iface.addToolBarIcon(self.action)

    # Phương thức được gọi khi plugin bị tắt
    def unload(self):
        # Loại bỏ action khỏi thanh công cụ
        self.iface.removeToolBarIcon(self.action)

    # Phương thức chính thực hiện chức năng của plugin
    def run(self):
        # Lấy lớp dữ liệu hiện tại
        current_layer = self.iface.activeLayer()

        # Kiểm tra xem lớp có tồn tại và là lớp vector không
        if current_layer is None or not current_layer.isValid() or not current_layer.isVector():
            self.iface.messageBar().pushMessage("Lỗi", "Chọn một lớp vector hợp lệ.", level=Qgis.Critical)
            return

        # Vẽ hình chữ nhật và lấy kích thước
        rect = self.iface.mapCanvas().sceneRect()
        xmin, ymin, xmax, ymax = rect.x(), rect.y(), rect.x() + rect.width(), rect.y() + rect.height()

        # Tạo hình chữ nhật từ kích thước đã lấy
        rectangle = QgsRectangle(xmin, ymin, xmax, ymax)

        # Tạo yêu cầu truy vấn với hình chữ nhật
        request = QgsFeatureRequest().setFilterRect(rectangle)

        # Lấy tất cả các đối tượng trong hình chữ nhật
        features = [f for f in current_layer.getFeatures(request)]

        if not features:
            self.iface.messageBar().pushMessage("Thông báo", "Không có đối tượng trong hình chữ nhật.", level=Qgis.Info)
            return

        # Tạo lớp dữ liệu mới
        new_layer = QgsVectorLayer("Point?crs=" + current_layer.crs().authid(), "result_layer", "memory")
        new_layer.startEditing()

        # Thêm các đối tượng vào lớp dữ liệu mới
        for feature in features:
            new_layer.addFeature(feature)

        new_layer.commitChanges()

        # Lưu lớp dữ liệu mới thành một tệp shapefile
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(None, "Save Shapefile", "", "Shapefiles (*.shp)")

        if file_path:
            QgsVectorFileWriter.writeAsVectorFormat(new_layer, file_path, "UTF-8", new_layer.crs(), "ESRI Shapefile")

        # Thêm lớp dữ liệu mới vào dự án QGIS
        QgsProject.instance().addMapLayer(new_layer)

        self.iface.messageBar().pushMessage("Thông báo", "Kết quả được xuất ra thành công.", level=Qgis.Success)