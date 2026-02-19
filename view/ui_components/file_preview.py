import os
import time

from configuration.language import Texts
from configuration.paths import Paths

import cv2
import pillow_heif
from PIL import ImageQt
import rawpy
from PIL import Image
from PyQt6.QtCore import QObject, Qt, QMutex, QMutexLocker, QRect
from PyQt6.QtGui import QPixmap, QTransform, QImage, QImageReader, QPainter, QFont, QFontMetrics, QColor
from controller.events.emitters.file_preview_ready_emitter import FilePreviewReadyEmitter
from services.metadata_services.metadata import FileMetadata
from configuration.settings import Settings


class FilePreview(QObject):
    instance_index = {}
    latest_panel_width = 0
    get_instance_active = False
    get_instance_mutex = QMutex()

    def __init__(self,file_name):
        super().__init__()
        # Check that instantiation is called from getInstance-method
        if not FilePreview.get_instance_active:
            raise Exception('Please use getInstance method')
        self.sleep = 0.1
        self.file_name = file_name
        self.panel_width = 0
        self.image = None
        self.pixmap = None
        self.current_rotation = None
        self.status = 'PENDING_READ'   # A lock telling status of metadata-variables: PENDING_READ, READING, WRITING, <blank>
        FilePreview.instance_index[file_name] = self
        self.web_server = None

    @staticmethod
    def getInstance(file_name):
        file_preview = FilePreview.instance_index.get(file_name)
        if file_preview is None:
            with QMutexLocker(FilePreview.get_instance_mutex):
                file_preview = FilePreview.instance_index.get(file_name)
                if file_preview is None:
                    FilePreview.get_instance_active = True
                    file_preview = FilePreview(file_name)
                    FilePreview.get_instance_active = False
        return file_preview

    @staticmethod
    def processReadStackEntry(stack_entry):
        FilePreview.getInstance(stack_entry).readImage()
        FilePreviewReadyEmitter.getInstance().emit(stack_entry)


    def readImage(self):
        if self.status != 'PENDING_READ':
            return 'NOTHING DONE'
        file_metadata = FileMetadata.getInstance(self.file_name)
        while file_metadata.getStatus() != '':
            time.sleep(self.sleep)

        file_type = FileMetadata.getInstance(self.file_name).getFileType()
        # Read image from file
        if self.image == None:     # Only read image from file once
            if file_type == 'heic':
                self.image = self.__heic_to_qimage(self.file_name)
                self.original_image_rotated = True  # Conversion from HEIC takes rotation-metadata into account. Returned QImage is already rotated
            elif file_type == 'cr2' or file_type == 'cr3' or file_type == 'arw' or file_type == 'nef' or file_type == 'dng':
                 self.image = self.__raw_to_qimage(self.file_name)
                 self.original_image_rotated = False # Conversion does not takes rotation-metadata into account. Returned QImage is not rotated
            elif file_type == 'mov' or file_type == 'mp4' or file_type == 'm4v' or file_type == 'm2t' or file_type == 'm2ts' or file_type == 'mts':
                self.image = self.__movie_to_qimage(self.file_name)
                self.original_image_rotated = False  # Conversion does not takes rotation-metadata into account. Returned QImage is not rotated
            else:
                if Settings.get("file_type_tags").get(file_type) is None:  # This happens if metadata tells that filetype is not the same as ending
                    self.image = self.__textToQimage("⚠️\t\t\t\t" + Texts.get("file_preview_incorrect_type").replace("<file_type>",file_type) + ":\n\t\t\t\t\t\t\t\t\t" + self.file_name)
                    self.original_image_rotated = False  # Conversion does not takes rotation-metadata into account. Returned QImage is not rotated
                else:
                    self.image = self.__default_to_qimage(self.file_name)
                    self.original_image_rotated = False  # Conversion does not takes rotation-metadata into account. Returned QImage is not rotated
            if self.image is None:
                self.image = self.__textToQimage("⚠️\t\t\t\t"+Texts.get("file_preview_file_corrupted")+":\n\t\t\t\t\t\t\t\t\t"+self.file_name)
            if self.image != None:
                if self.image.height()>1500 or self.image.width()>1500:
                    try:
                        scaled_image = self.image.scaled(1500,1500,Qt.AspectRatioMode.KeepAspectRatio)
                        self.image = scaled_image
                    except Exception as e:
                        print(f"An error offurred: {e}")
        if FilePreview.latest_panel_width != 0:
            self.__setPixmap(FilePreview.latest_panel_width)
        self.status = ''
        return 'IMAGE READ'


    def getStatus(self):
        return self.status
    def getPixmap(self,panel_width):
        if self.status != '':
            raise Exception('Preview pixmap not ready yet. Status is '+ self.status)
        if panel_width != self.panel_width:
            self.__setPixmap(panel_width)
        return self.pixmap

    def __textToQimage(self,text, width=1500, height=300, font_size=22):
        img = QImage(width, height, QImage.Format.Format_RGB32)
        img.fill(Qt.GlobalColor.white)

        painter = QPainter(img)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        font = QFont("Arial", font_size)
        painter.setFont(font)
        painter.setPen(QColor("black"))

        # Define drawing rectangle
        rect = QRect(10, 10, width - 20, height - 20)

        # Allow multiline + word wrap
        flags = Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap

        painter.drawText(rect, flags, text)
        painter.end()

        return img


    def __setPixmap(self,panel_width):
        self.panel_width = panel_width
        FilePreview.latest_panel_width = panel_width
        # Set right rotation/orientation
        image = self.getImage()

        if image != None:
            if image.width() > 0:
                ratio_width  = panel_width / image.width()
                ratio_height = panel_width / image.height() / 16 * 9   # Image same height as a 9/16 landscape filling screen-width
                ratio = min(ratio_width,ratio_height)

                width = int(image.width() * ratio)
                height = int(image.height() * ratio)

                self.pixmap = QPixmap.fromImage(image)
                self.pixmap = self.pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
            else:
                self.pixmap = None
        else:
            self.pixmap = None

    def getImage(self):
        file_type = FileMetadata.getInstance(self.file_name).type

        # Set right rotation/orientation
        if file_type ==  'm2t' or file_type == 'm2ts' or file_type == 'mts':
            image = self.image
        else:
            image = self.__rotatedImage()
        return image

    def __rotatedImage(self):
        if self.image == None:
            return None
        else:
            rotation_instance = FileMetadata.getInstance(self.file_name).logical_tag_instances.get("rotation")
            saved_rotation_instance = FileMetadata.getInstance(self.file_name).saved_logical_tag_instances.get("rotation")
            if rotation_instance == None:
                rotation = 0
            else:
                rotation = rotation_instance.getValue()
                if rotation is None:
                    rotation = 0
            if saved_rotation_instance == None:
                saved_rotation = 0
            else:
                saved_rotation = saved_rotation_instance.getValue()
                if saved_rotation is None:
                    saved_rotation = 0

            if self.current_rotation is None:
                if self.original_image_rotated:
                    self.current_rotation = saved_rotation
                else:
                    self.current_rotation = 0

            rotation_change = self.current_rotation - rotation
            if rotation_change != 0:
                transform = QTransform()
                transform.rotate(rotation_change)
                rotated_image = self.image.transformed(transform)
                return rotated_image
            else:
                return self.image

    def __heic_to_qimage(self, file_name):
        # If the image is already set, just return it
        if self.image is not None:
            return self.image

        try:
            # Check if HEIC support exists for this file
            if not pillow_heif.is_supported(file_name):
                return None

            pillow_heif.register_heif_opener()

            # Try opening the image
            pil_image = Image.open(file_name)

            # Force full image decoding — *this is key*
            pil_image.load()

            # Ensure correct RGB format
            if pil_image.mode != "RGB":
                pil_image = pil_image.convert("RGB")

            # Convert to QImage — safe now
            qimage = ImageQt.toqimage(pil_image)
            return qimage

        except Exception as e:
            return None  # or return a fallback image here

    def __raw_to_qimage(self, file_name):
        # If image already loaded, reuse it
        if self.image is not None:
            return self.image

        # Default: no image
        image = None

        try:
            # rawpy can throw exceptions on corrupt or unsupported files
            with rawpy.imread(file_name) as raw:

                try:
                    thumb = raw.extract_thumb()
                except rawpy.LibRawNoThumbnailError:
                    print(f"No thumbnail found in RAW file: {file_name}")
                    return None

                # Thumbnail extracted, now decode based on format
                if thumb.format == rawpy.ThumbFormat.JPEG:
                    # QImage.fromData handles JPEG safely
                    image = QImage.fromData(thumb.data)

                elif thumb.format == rawpy.ThumbFormat.BITMAP:
                    try:
                        # Convert bitmap (numpy array) → PIL → bytes → QImage
                        thumb_pil = Image.fromarray(thumb.data)
                        rgb_image = thumb_pil.convert("RGB")  # ensure RGB888
                        width, height = rgb_image.size
                        data = rgb_image.tobytes("raw", "RGB")

                        # QImage requires memory that stays alive, so copy it:
                        image = QImage(data, width, height, QImage.Format.Format_RGB888).copy()

                    except Exception as e:
                        print(f"Error converting RAW bitmap thumbnail: {e}")
                        return None

                else:
                    # Unknown / unsupported thumbnail format
                    print(f"Unsupported RAW thumbnail format: {thumb.format}")
                    return None

        except Exception as e:
            # rawpy.imread or extract may fail on corrupted files
            print(f"Failed loading RAW file '{file_name}': {e}")
            return None

        return image

    def __movie_to_qimage(self, file_name):
        # If already loaded, return existing result
        if self.image is not None:
            return self.image

        try:
            video = cv2.VideoCapture(file_name)

            if not video.isOpened():
                return None

            # Retrieve video metadata safely
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = float(video.get(cv2.CAP_PROP_FPS))

            if fps <= 0 or total_frames <= 0:
                video.release()
                return None

            # Total duration
            duration = total_frames / fps

            # Pick a frame at 3% of the video
            frame_time = duration * 0.03
            video.set(cv2.CAP_PROP_POS_MSEC, frame_time * 1000)

            # Read the frame
            success, frame = video.read()
            if not success or frame is None:
                video.release()
                return None

            # Convert BGR → RGB
            try:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            except Exception:
                video.release()
                return None

            height, width, channels = rgb_frame.shape
            if channels != 3:
                video.release()
                return None

            # Create QImage
            # IMPORTANT: copy() ensures memory stays valid after function exits
            image = QImage(rgb_frame.data, width, height, width * 3, QImage.Format.Format_RGB888).copy()

            video.release()
            return image

        except Exception as e:
            print(f"Error reading video preview from '{file_name}': {e}")
            try:
                video.release()
            except:
                pass
            return None

    def __default_to_qimage(self, file_name):
        # Reuse cached image if available
        if self.image is not None:
            return self.image

        try:
            reader = QImageReader(file_name)

            # Optional safety: don't try reading unsupported types
            if not reader.canRead():
                return None

            image = reader.read()

            if image.isNull():
                # Occurs on corrupt or unreadable images
                return None  # empty fallback

            return image

        except Exception as e:
            return None  # safe empty fallback

    # def __default_to_qimage(self,file_name):
    #     if self.image == None:
    #         image_reader = QImageReader(file_name)
    #         image = image_reader.read()
    #     else:
    #         image = self.image
    #     return image


    def updatePixmap(self):
        self.__setPixmap(FilePreview.latest_panel_width)


    def updateFilename(self, new_file_name):
        old_file_name = self.file_name
        self.file_name = new_file_name
        FilePreview.instance_index[new_file_name] = self
        del FilePreview.instance_index[old_file_name]