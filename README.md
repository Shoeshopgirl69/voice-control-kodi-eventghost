# Voice Control for Kodi
## Requirements:
- Google Home
- IFTTT account linked to your Google Home
- Nvidia Shield (This should work on any Android box.)
- Tasker App
- Tasker Network Event Server App
- Secure Settings App
- These Tasker profiles, tasks, scenes, and javascripts files

 ## Steps:
 - Install the "Tasker", "Tasker Network Event Server", and "Secure Settings" apps on the Nvidia Shield, all can be found on Google Play
 - Configure your Nvidia Shield so you can access the storage remotely
 - Save the following javascript file under the Tasker folder on the Nvidia Shield https://raw.githubusercontent.com/brianf21/Voice-Control-for-Kodi/master/setupVoiceControl.js  (You should be able to do this on your PC after you mount the Nvidia Shield storage)
 - In tasker create a new Tasks called "Setup Task"
 - Add a "Code"/"JavaScript" action then navigate to the javascript from above by clicking on the magnify glass. Go to the Tasker folder then click on setupVoiceControl.js
 - Click on the back button on the top left corner of the screen to go back to the Task Edit screen
 - Press the play button on the bottom left corner to download the profiles and the rest of the javascripts files
 - After it completes, click the back button on the top left corner to return to the Tasks list
 - Click on the profiles tab to go to the Profiles list
 - Long press on the Profiles tab and import all of the profiles, the profiles are saved under Tasker/profiles
 - There should be a total of 4 profiles: Perform, Launch, Download, and Play
 - After all the profiles are imported, click the check mark on the top right corner to save everything
 - Open up port 8765 on your router to the private IP of your Nvidia Shield
 - On the Nvidia Shield, launch Kodi and turn on the web server ("Setting > Service Settings > Control"; set username and password)
 - On another computer, install and configure Radarr
 - Edit the javascript files and replace the IP's and API keys where needed
 - Email me if you need help. gmail brian.faris
  
## Create four IFTTT applets
  
### First IFTTT applet: (This issues commands)
- Choose "Say a phrase with a text ingredient"
- For "THIS" choose "Google Assistant"
- For "THAT" choose "Maker Webhook"
- Google Assistant
- What do you want to say?: press $ (You can chose any phrase you want, just make it unique.)
- (Current commands: Look at the perform.js to see a full list of the commands..)
- What do you want the Assistant to say in response? okay
- Maker Webhook
```
http://YourPublicIP:8765?perform=<<<Textfield>>>
```
- For Textfield, click your text ingredient.
- Method: Get
- Content Type: text/plain
  
### Second IFTTT applet: (This launches apps)
- Choose "Say a phrase with a text ingredient"
- For "THIS" choose "Google Assistant"
- For "THAT" choose "Maker Webhook"
- Google Assistant
- What do you want to say?: please launch $ (Google Home ignores the word "please", so you can just say "launch app name".)
- What do you want the Assistant to say in response? launching $
- Maker Webhook
```
http://YourPublicIP:8765?launch=<<<Textfield>>>
```
- For Textfield, click your text ingredient.
- Method: Get
- Content Type: text/plain
 
### Third IFTTT applet: (This plays movies or shows)
- Choose "Say a phrase with a text ingredient"
- For "THIS" choose "Google Assistant"
- For "THAT" choose "Maker Webhook"
- Google Assistant
- What do you want to say?: please play $ (Google Home ignores the word "please", so you can just say "play movie name" or "play TV show name".)
- What do you want the Assistant to say in response? showing $
- Maker Webhook
```
http://YourPublicIP:8765?play=<<<Textfield>>>
```
- For Textfield, click your text ingredient.
- Method: Get
- Content Type: text/plain

### Fourth IFTTT applet: (This wakes the shield)
- Choose "Say a phrase with a text ingredient"
- For "THIS" choose "Google Assistant"
- For "THAT" choose "Maker Webhook"
- Google Assistant
- What do you want to say?: please wake up 
- What do you want the Assistant to say in response? Okay, I'm awake
- Maker Webhook
```
http://YourPublicIP:8765?wake
```
- For Textfield, click your text ingredient.
- Method: Get
- Content Type: text/plain
