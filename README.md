# Memory Mate
## Memories are dear
How happy I always get when turning an old photo finding some written words like..
*Our trip to Rome in 1948. this was the year we first met. In the photo you can see my beloved Lisa an I at  La Scalinata di Trinità dei Monti*
Greatings from passed times. I want to put these greetings on "the back" of our digital family photos and videos in the same way. To be sure the greatings will always follow the photos, it needs to be put in metadata, so that it is readable (almost) everywhere. This can be combersome. There are so many different filetypes and even more types of metadata-tags. This goal of this python windows-application is encapsulate the complexity, so that you can focus on enriching *your* dear memories for future to come...

## How does it look

![The UI is kept simple...](MemoryMateUI.jpg)

## How does it work
The application wrappes the amazing [ExifTool by Phil Harvey](https://exiftool.org/)
The application works with *logical tags*. The defaults are:
* Tille
* Date
* Description
* People
* Photographer
* Source
* Original Filename
* Full Description

First time program launches, it generates a settings.json file in \ProgramData\Memeory Mate folder on your computer. Future launches, the program will use settings.json file. You can create a new logical tags in the settings.json, if you would like the program to have more tags in addition to the defaults.
In settings.json, logical tags are mapped to one or more physical image-tags per image/video file type. 
