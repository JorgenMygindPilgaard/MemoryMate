from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import pillow_heif
import file_util
import rawpy
from PIL import Image
from moviepy.video.io.VideoFileClip import VideoFileClip


class FilePreview():
    instance_index = {}

    def __init__(self,file_name,width):
        self.file_name = file_name
        file_type = file_util.splitFileName(file_name)[2].lower()
        if file_type == 'heic':
            pixmap = self.__heic_to_qpixmap(file_name)
        elif file_type == 'cr2' or file_type == 'cr3' or file_type == 'arw' or file_type == 'nef' or file_type == 'dng':
             pixmap = self.__raw_to_qpixmap(file_name)
        elif file_type == 'mov' or file_type == 'mp4':
            pixmap = self.__movie_to_qpixmap(file_name)
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
        image = QImage(image_data, width, height, image_format)
        return QPixmap.fromImage(image)

    def __raw_to_qpixmap(self,file_name):
        with rawpy.imread(file_name) as raw:
            try:
                thumb = raw.extract_thumb()
            except rawpy.LibRawNoThumbnailError:
                print('no thumbnail found')
            else:
                if thumb.format in [rawpy.ThumbFormat.JPEG, rawpy.ThumbFormat.BITMAP]:
                    if thumb.format is rawpy.ThumbFormat.JPEG:
                        thumb_image = QImage.fromData(thumb.data)

                    else:
                        thumb_pil = Image.fromarray(thumb.data)
                        thumb_data = thumb_pil.tobytes()
                        thumb_image = QImage(thumb_data, thumb_pil.width, thumb_pil.height, QImage.Format_RGB888)
                return QPixmap.fromImage(thumb_image)
    def __movie_to_qpixmap(self,file_name):
        video_clip = VideoFileClip(file_name)
        thumbnail = video_clip.get_frame(0)  # Get the first frame as the thumbnail
        video_clip.close()

        height, width, channel = thumbnail.shape
        bytes_per_line = 3 * width

        q_image = QImage(
            thumbnail.data,
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_RGB888,
        )

        thumbnail_pixmap = QPixmap.fromImage(q_image)
        return thumbnail_pixmap


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
