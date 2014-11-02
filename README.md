Overview
---

**service.subtitles.subsunacs** is an addon for XBMC 13.2 to download subtitles from http://subsunacs.net/.

Currently the only supported language is Bulgarian.

The plugin will retrieve raiting information as well downloads count, however the site does not maintain metadata information for synchronization or hearing impaired features.

Since the file storage of subsunacs.net is a RAR the first .srt/.sub file available within will be used.

Dependencies
---
- Requires python 2.7 built into XBMC
- Requires add-on [script.module.beautifulsoup] which you can download from [SuperRepo]

Installation
---
1. Use the Download Zip button to download.

2. Unzip the folder under your addons folder (sibling to the [XBMC userdata] folder)

3. Restart XBMC might be needed

4. Use XBMC subtitles picker to choose this plugin as service provider during video playback

Troubleshooting
---

In case of errors downloading an archive on linux, check if the archive contains files in cyrillic. If yes install unrar and it will be used as a workaround.  

License
---

[GPLv2]

**Free Software, Hell Yeah!**

[GPLv2]:http://www.gnu.org/licenses/gpl-2.0.html
[SuperRepo]:http://superrepo.org/
[script.module.beautifulsoup]:http://superrepo.org/script.module.beautifulsoup/
[XBMC userdata]:http://kodi.wiki/view/Userdata