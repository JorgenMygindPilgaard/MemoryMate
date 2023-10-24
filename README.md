# Memory Mate
## Memories are dear
How happy I always get when turning an old photo finding some written words like..
*Our trip to Rome in 1948. This was the year we first met. In the photo you can see my beloved Lisa and I at "La Scalinata di Trinità dei Monti"*
Greetings from passed times. I want to put greetings on "the back" of our digital family photos and videos in the same way. To be sure the greetings will always follow the photos, it needs to be put in metadata, so that it is readable (almost) everywhere. This can be combersome. There are so many different filetypes and even more types of metadata-tags. The goal of this python windows-application is to encapsulate the complexity, so that you can focus on enriching *your* dear memories for times to come...

## How does it look

![The UI is kept simple...](MemoryMateUI.jpg)
## Installation
### Installation package
The easiest way to get the application running on your computer is to use the installation-package......will follow later....
### Get Source-code
You can use the souce-code from repsitory freely, suggest changes etc. The application is created using Python 3.11 and PyQt5 5.17.7. 

## How does it work
The application wrappes the amazing [ExifTool by Phil Harvey. ](https://exiftool.org/)
The application works with what I have chosen to call *logical tags*. These are tags that only the application knows of. The defaults are:
* Tille
* Date
* Description
* People
* Geo-location
* Photographer
* Source
* Original Filename
* Full Description
These logical tags are all visible in the right hand section of the UI below the image preview.

When you use Memory Mate to change the content of one of the logical tags (e.g. if you change the title of a photo), the program writes the changed value to one or more physical tags in the file metadata. 
The *Full Description* is a special type of logical tag called a *reference tag.* In the default settings, *all* other logical tags are referenced in the *Full Description*. The *Full Description* reference tag is saved to commenly used physical tags for image-description, so that you will be sure to be able to see all information, also in programs only capable of showing one of the physical tags for description.
### Functionalities
#### Edit Logical Tags
Just select a file and start typing. The data is saved when you navigate away from image or close application.
#### Consolidate metadata
Do you have images with title, description etc. not written to all logical tags. No problem. Select the file/files/folder/folders, right-click and select "Consolidate metadata". The program will then make sure to "spread" the logical tags to all corresponding physical tags in the selected images.
#### Copy metadata
Mark the file/files/folder/folders. Then right-click the selection and select "Copy Metadata". Then select target file/files/filder/folders, right-click, tick the tags you want to paste (take care not pasting all tags. Can't be regretted), and select "Paste Metadata". If you have chosen more than one source-file, the "Paste Metadata" option is greyed out, and can't be used. You can in stead chose "Paste Metadata by Filename". When you paste using that option, Memory Mate will copy metadata from files in the selected source to metadata of files *with the same filename* in the target (ignoring the file type). That is very handy, if you store your original, raw files in a separate folder, and have edited metadata for all the corresponding edited jpg-files. You can then simply paste by filename to your original raw-files in one go.

## How to configure the application
First time program launches, the language is set to english. You can change that to danish (only additional language prepared so far) by clicking the settings-wheel in the top right corner. After changing the language, relaunch the program.
Also at first launch the program generates a settings.json file in "\ProgramData\Memeory Mate"-folder on your computer. At future launches, the program will use the existing settings.json file. You can add or remove logical tags in the settings.json, if you would like the program to work with other logical tags that the defaults.
If you want to revert to defaults after editing settings.json, then simply delete the file from "\ProgramData\Memeory Mate"-folder. At next program-launch, the default settings.json will be generated again.
In settings.json, logical tags are mapped to one or more physical image-tags per image/video file type. Here is a snipit from the settings.json showing in which physical tags the program stores the Title in jpg-files.:
```json
    "file_type_tags": {
        "jpg": {
            "title": [
                "XMP:Title",
                "EXIF:XPTitle",
                "IPTC:ObjectName"
            ],
            "date": [
                "XMP:Date"
               
```
#### Reference tags
The *Full description* logical tag is a special type of tag called a reference-tag in the application. The reference tag is *always* a read-only tag on the screen, but it is still mapped to one or more physical tags, just like the normal logical tags.
The content of a reference tag is defined in the settings.json file. You can configure the reference tag to one or more of the following components:
* A logical tag with label
* A logical tag without label
* A fixed text (can be an empty string, if you need a blank line)

Here you see the default-configuration of content for the *Full description* reference tag:
```json
    "reference_tag_content": {
        "description": [
            {
                "type": "tag",
                "tag_name": "title",
                "tag_label": false
            },
            {
                "type": "tag",
                "tag_name": "description_only",
                "tag_label": false
            },
            {
                "type": "text_line",
                "text": ""
            },
            {
                "type": "tag",
                "tag_name": "persons",
                "tag_label": true
            },
            {
                "type": "tag",
                "tag_name": "source",
                "tag_label": true
            },
            {
                "type": "tag",
                "tag_name": "photographer",
                "tag_label": true
            },
            {
                "type": "tag",
                "tag_name": "original_filename",
                "tag_label": true
            }
        ]
    },
```



