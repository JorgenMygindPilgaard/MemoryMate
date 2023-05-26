from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import Image
import pillow_heif
import file_util

class FilePreview():
    instance_index = {}

    def __init__(self,file_name,width):
        file_type = file_util.splitFileName(file_name)[2].lower()
        if file_type == 'heic':
            pixmap = self.__heic_to_qpixmap(file_name)
        else:
            pixmap = QPixmap(file_name)

        height = int(width * 9 / 16)
        self.pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio,Qt.SmoothTransformation)
        self.width = width
        FilePreview.instance_index[file_name] = self

    def __heic_to_qpixmap(self,file_name):
        heic_image = pillow_heif.read_heif(file_name)
        pil_image = heic_image.to_pillow()
#       pil_image.show()

        # Convert PIL Image to RGB mode if it's not already
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        image_data = pil_image.tobytes()
        width, height = pil_image.size
        image_format = QImage.Format_RGB888
        qimage = QImage(image_data, width, height, image_format)
        return QPixmap.fromImage(qimage)

    @staticmethod
    def getInstance(file_name,width):
        new_needed = False

        file_preview = FilePreview.instance_index.get(file_name)
        if file_preview is None:
            new_needed = True
        elif file_preview.width != width:
            del FilePreview.instance_index[file_name]
            new_needed = True
        if new_needed:
            file_preview =  FilePreview(file_name,width)

        return file_preview
