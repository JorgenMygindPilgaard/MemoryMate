from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from PIL import Image
import rawpy
import pillow_heif
import file_util

class FilePreview():
    instance_index = {}

    def __init__(self,file_name,width):
        self.file_name = file_name
        file_type = file_util.splitFileName(file_name)[2].lower()
        if file_type == 'heic':
            pixmap = self.__heic_to_qpixmap(file_name)
#        elif file_type == 'cr2' or file_type == 'cr3' or file_type == 'arw' or file_type == 'nef':   # Dosen' work
#            pixmap = self.__raw_to_qpixmap(file_name)
        else:
            pixmap = QPixmap(file_name)

        height = int(width * 9 / 16)
        self.pixmap = pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
        self.width = width
        FilePreview.instance_index[file_name] = self

    def __heic_to_qpixmap(self,file_name):
        pil_image = pillow_heif.read_heif(file_name).to_pillow()
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")
        image_data = pil_image.tobytes()
        width, height = pil_image.size
        image_format = QImage.Format.Format_RGB888
        qimage = QImage(image_data, width, height, image_format)
        return QPixmap.fromImage(qimage)

    def __raw_to_qpixmap(self,file_name):
        raw = rawpy.imread(file_name)

        raw_image = raw.raw_image  # numpy array
        pil_image = Image.fromarray(raw_image)
        pil_image.show()
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")
        image_data = pil_image.tobytes()
        width, height = pil_image.size
        image_format = QImage.Format_RGB888
        qimage = QImage(image_data, width, height, image_format)
        return QPixmap.fromImage(qimage)

    @staticmethod
    def getInstance(file_name,width=None):
        new_needed = False

        file_preview = FilePreview.instance_index.get(file_name)
        if file_preview is None:
            new_needed = True
        elif file_preview.width != width and width != None:
            del FilePreview.instance_index[file_name]
            new_needed = True
        if new_needed:
            if width == None:
                file_preview = None
            else:
                file_preview =  FilePreview(file_name,width)

        return file_preview

    def updateFilename(self, new_file_name):
        old_file_name = self.file_name
        self.file_name = new_file_name
        FilePreview.instance_index[new_file_name] = self
        del FilePreview.instance_index[old_file_name]
