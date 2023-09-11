from PyQt6.QtCore import QObject, Qt
from PyQt6.QtGui import QPixmap, QImage,QTransform, QImageReader
import pillow_heif
import file_util
import rawpy
from PIL import Image
from moviepy.video.io.VideoFileClip import VideoFileClip
from file_metadata_util import FileMetadata

class FilePreview(QObject):
    instance_index = {}

    def __init__(self,file_name,width):
        super().__init__()
        self.file_name = file_name
        self.width = width
        self.image = None
        self.pixmap = None
        self.original_rotation = None
        self.__setPixmap()
        FilePreview.instance_index[file_name] = self

    def __setPixmap(self):
        file_type = file_util.splitFileName(self.file_name)[2].lower()

        # Read image from file
        if self.image == None:     # Only read image from file once
            if file_type == 'heic':
                self.image = self.__heic_to_qimage(self.file_name)
            elif file_type == 'cr2' or file_type == 'cr3' or file_type == 'arw' or file_type == 'nef' or file_type == 'dng':
                 self.image = self.__raw_to_qimage(self.file_name)
            elif file_type == 'mov' or file_type == 'mp4':
                self.image = self.__movie_to_qimage(self.file_name)
            else:
                self.image = self.__default_to_qimage(self.file_name)

        # Set right rotation/orientation
        if file_type == 'mov' or file_type == 'mp4':
            image = self.image
        elif file_type == 'heic':
            image = self.__rotatedImage()
        else:
            image = self.__orientedImage()

        # Set pixmap
        if image != None:
            height = int(self.width * 9 / 16)
            self.pixmap = QPixmap.fromImage(image).scaled(self.width, height, Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
        else:
            self.pixmap = None

    def __orientedImage(self):
        # Apply transformations based on EXIF orientation
        if self.image == None:
            return None
        else:
            orientation = FileMetadata.getInstance(self.file_name).logical_tag_values.get("orientation")
            transform = QTransform()
            if orientation == None:
                orientation = 1             #Horizontal (normal), Default orientation
            if orientation == 1:            #Horizontal (normal)'
                transform.rotate(0)
            if orientation == 3:            #Rotate 180'
                transform.rotate(180)
            elif orientation == 6:          #Rotate 90 CW':
                transform.rotate(90)
            elif orientation == 8:          #Rotate 270 CW'
                transform.rotate(270)

            # Apply transformation to the QImage
            oriented_image = self.image.transformed(transform)
            return oriented_image

    def __rotatedImage(self):
        if self.image == None:
            return None
        else:
            rotation = FileMetadata.getInstance(self.file_name).logical_tag_values.get("rotation")
            if rotation == None:
                rotation = 0.
            if self.original_rotation == None:
                self.original_rotation = rotation

            rotation_change = self.original_rotation - rotation
            if rotation_change != 0:
                transform = QTransform()
                transform.rotate(rotation_change)
                rotated_image = self.image.transformed(transform)
                return rotated_image
            else:
                return self.image

    def __heic_to_qimage(self,file_name):
        if self.image == None:
            if pillow_heif.is_supported(file_name):
                pillow_heif.register_heif_opener()
                pil_image = Image.open(file_name)
                if pil_image.mode != "RGB":
                    pil_image = pil_image.convert("RGB")
                image_data = pil_image.tobytes()
                width, height = pil_image.size
                image_format = QImage.Format.Format_RGB888
                image = QImage(image_data, width, height, image_format)
            else:
                image = None
        else:
            image = self.image
        return image

    def __raw_to_qimage(self,file_name):
        if self.image == None:
            with rawpy.imread(file_name) as raw:
                try:
                    thumb = raw.extract_thumb()
                except rawpy.LibRawNoThumbnailError:
                    print('no thumbnail found')
                else:
                    if thumb.format in [rawpy.ThumbFormat.JPEG, rawpy.ThumbFormat.BITMAP]:
                        if thumb.format is rawpy.ThumbFormat.JPEG:
                            image = QImage.fromData(thumb.data)
                        else:
                            thumb_pil = Image.fromarray(thumb.data)
                            thumb_data = thumb_pil.tobytes()
                            image = QImage(thumb_data, thumb_pil.width, thumb_pil.height, QImage.Format.Format_RGB888)
        else:
            image = self.image

        return image
    def __movie_to_qimage(self,file_name):
        if self.image == None:
            video_clip = VideoFileClip(file_name)
            thumbnail = video_clip.get_frame(0)  # Get the first frame as the thumbnail
            video_clip.close()

            height, width, channel = thumbnail.shape
            bytes_per_line = 3 * width

            image = QImage(
                thumbnail.data,
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_RGB888,
            )
        else:
            image = self.image
        return image

    def __default_to_qimage(self,file_name):
        if self.image == None:
            image_reader = QImageReader(file_name)
            image = image_reader.read()
        else:
            image = self.image
        return image

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

    def updatePixmap(self):
        self.__setPixmap()


    def updateFilename(self, new_file_name):
        old_file_name = self.file_name
        self.file_name = new_file_name
        FilePreview.instance_index[new_file_name] = self
        del FilePreview.instance_index[old_file_name]



































