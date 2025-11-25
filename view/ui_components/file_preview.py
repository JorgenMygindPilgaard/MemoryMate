import os
import time
from configuration.paths import Paths

import cv2
import pillow_heif
from PIL import ImageQt
import rawpy
from PIL import Image
from PyQt6.QtCore import QObject, Qt, QMutex, QMutexLocker
from PyQt6.QtGui import QPixmap, QTransform, QImage, QImageReader
from controller.events.emitters.file_preview_ready_emitter import FilePreviewReadyEmitter
from services.metadata_services.metadata import FileMetadata


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
                self.image = self.__default_to_qimage(self.file_name)
                self.original_image_rotated = False  # Conversion does not takes rotation-metadata into account. Returned QImage is not rotated
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

    def __heic_to_qimage(self,file_name):
        if self.image == None:
            if pillow_heif.is_supported(file_name):
                pillow_heif.register_heif_opener()
                pil_image = Image.open(file_name)
                if pil_image.mode != "RGB":
                    pil_image = pil_image.convert("RGB")
                image = ImageQt.toqimage(pil_image)
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
            video = cv2.VideoCapture(file_name)

            if not video.isOpened():
                image = self.__default_to_qimage(os.path.join(Paths.get('resources'), "no_preview.png"))
            else:

                # Get total frame count and FPS
                total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = video.get(cv2.CAP_PROP_FPS)
                duration = total_frames / fps  # Total duration in seconds

                # Calculate the time (in seconds) at the given percentage
                frame_time = duration * (3.0 / 100.0)

                # Set the video position to that time
                video.set(cv2.CAP_PROP_POS_MSEC, frame_time * 1000)

                # Read the frame
                success, frame = video.read()
                if not success:
                    image = self.__default_to_qimage(os.path.join(Paths.get('resources'), "no_preview.png"))
                    video.release()
                else:
                    # Convert the frame (BGR to RGB for QImage)
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Get frame dimensions
                    height, width, channel = rgb_frame.shape

                    # Create QImage
                    image = QImage(rgb_frame.data, width, height, 3 * width, QImage.Format.Format_RGB888)
                    video.release()


            # try:
            #     # Attempt to create a VideoFileClip object
            #     video_clip = VideoFileClip(file_name)
            #     fps = video_clip.fps
            #     duration = video_clip.duration
            #     # Get frame 3% into the video. The first seconds are often black or blurry/shaked
            #     frame = int(duration * 3 / 100 * fps)  # Frame
            #     thumbnail = video_clip.get_frame(frame)  # Get the first frame as the thumbnail
            #
            #     # If recorded in portrait-mode, swap height and width
            #     #            if hasattr(video_clip, 'rotation'):
            #     #                rotation = video_clip.rotation
            #     #                if rotation in [90, 270]:
            #     #                    original_width, original_height = video_clip.size
            #     #                    thumbnail = cv2.resize(thumbnail, (original_height, original_width))  # Swap hight and width
            #     video_clip.close()
            #
            #     height, width, channel = thumbnail.shape
            #     bytes_per_line = 3 * width
            #
            #     image = QImage(
            #         thumbnail.data,
            #         width,
            #         height,
            #         bytes_per_line,
            #         QImage.Format.Format_RGB888,
            #     )
            #     video_clip.close()
            # except OSError as e:
            #     image = self.__default_to_qimage(os.path.join(Path.get('resources'), "no_preview.png"))
            #     # Handle specific OSError from ffmpeg
            #     print(f"Error loading video file {file_name}: {e}")
            # except Exception as e:
            #     image = self.__default_to_qimage(os.path.join(Path.get('resources'), "no_preview.png"))
            #     # Catch all other exceptions
            #     print(f"An unexpected error occurred with file {file_name}: {e}")


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


    def updatePixmap(self):
        self.__setPixmap(FilePreview.latest_panel_width)


    def updateFilename(self, new_file_name):
        old_file_name = self.file_name
        self.file_name = new_file_name
        FilePreview.instance_index[new_file_name] = self
        del FilePreview.instance_index[old_file_name]