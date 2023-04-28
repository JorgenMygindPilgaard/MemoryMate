# Memory Mate
## Memories are dear
How happy I always get when turning an old photo finding some written words like..
*Our trip to Rome in 1948. This was the year we first met. In the photo you can see my beloved Lisa and I at "La Scalinata di Trinità dei Monti"*
Greetings from passed times. I want to put these greetings on "the back" of our digital family photos and videos in the same way. To be sure the greetings will always follow the photos, it needs to be put in metadata, so that it is readable (almost) everywhere. This can be combersome. There are so many different filetypes and even more types of metadata-tags. The goal of this python windows-application is to encapsulate the complexity, so that you can focus on enriching *your* dear memories for future to come...

## How does it look

![The UI is kept simple...](MemoryMateUI.jpg)

## How does it work
The application wrappes the amazing [ExifTool by Phil Harvey. ](https://exiftool.org/)
The application works with *logical tags*. These are tags that only the application knows of. The defaults are:
* Tille
* Date
* Description
* People
* Photographer
* Source
* Original Filename
* Full Description

First time program launches, it generates a settings.json file in "\Windows\ProgramData\Memeory Mate"-folder on your computer. At future launches, the program will use settings.json file. You can add or remove logical tags in the settings.json, if you would like the program to work with other logical tags that the defaults.
In settings.json, logical tags are mapped to one or more physical image-tags per image/video file type. Here is a snipit from the settings.json showing in which physical tags the program stores the Title:
    "file_type_tags": {
        "jpg": {
            "title": [
                "XMP:Title",
                "EXIF:XPTitle",
                "IPTC:ObjectName"
            ],
            "date": [
                "XMP:Date",...........
               
### Functionalities
#### Edit Logical Tags
Just select a file and start typing. The data is saved when you navigate away from image or close application,
#### Consolidate metadata
Do you have images with Title, description etc. not written to all logical tags. No problem. Right-click the selected file/files/filder/folders and select "Consolidate metadata. The program will then make sure to "spread" the logical tags to all corresponding logical tags. It will also find files with same filename (e.g my_file,jpg and my_file.cr2 or my_file.jpg in folder and subfolder) and and synchronize logical and physical tags across files, filling gaps.
#### Copy metadata
Right-click source-image and select "Copy Metadata". Then select target file/files/filder/folders, right-click, tick the tags you want to paste (take care not pasting all tags. Can't be regretted), and select "Paste Metadata".
