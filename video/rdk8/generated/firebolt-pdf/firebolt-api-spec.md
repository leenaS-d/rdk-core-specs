# Extracted firebolt-api-spec

Source: `Firebolt 8 API Spec.pdf`
SHA-256: `cd97b2e5df8e85cf2aad43804346b189a22382422cb0d4ebf375f5785a20f578`

> This file is generated from the PDF for review. It is not a replacement for the curated JSON.

## Page 1

```text
Firebolt®  8.0 API  Specification                                            
                                                                                    
        Document status ARCHIVED                                                    
                                                                                    
        Author    Andrew Bennett                                                    
                                                                                    
                                                                                    
       Note: this is an archived version - please refer to the latest version of this
       page at Firebolt 9 API Specification                                         
                                                                                    
                                                                                    
                                                                                    
        API version Link Summary                                                    
       8.0.1   213     Device.hdr - fixed typo: hd10Plus should be hdr10Plus        
       8.0.0   180     8.0.0                                                        
                                                                                    
                           This is the approved version for RDK8                    
                                                                                    
                                                                                    
                                                                                    
       Key                                                                          
                                                                                    
                                                                                    
        Color Meaning                                                               
       Green Approved - ready for development                                       
       Red  Not approved - not ready for development                                
                                                                                    
                                                                                    
       Types                                                                        
                                                                                    
           Type Definition                                                          
       1  unsigned 32-bit unsigned integer                                          
                                                                                    
       2  double 64-bit double-precision floating point number                      
                                                                                    
       Errors                                                                       
                                                                                    
           Class Value Name  Description              Examples          Open        
                                                                        issues      
       1  Generic -32601 Method not known The method is not known to the version of Firebolt on this Device.foo
                            device                                                  
       2       -40300 Method not The app does not have permission to call this method
                   permitted                                                        
       3       -32602 Arguments invalid The set of arguments is not valid           
       4       -32100 Unspecified error Any unexpected error Memory allocation failure, transport
                                                      failure                       
       5  Specific -50100 Method not A non-mandatory method that is not implemented on this SecureStorage.get on a non-Comcast
                   supported device                   device                        
       6           App state invalid The app is not in an appropriate lifecycle state to call this
                            method                                                  
       Methods
```

### Table 1

```text
Document status | ARCHIVED
Author | Andrew Bennett
```

### Table 2

```text
API version | Link | Summary
8.0.1 | 213 | Device.hdr - fixed typo: hd10Plus should be hdr10Plus
8.0.0 | 180 | 8.0.0
This is the approved version for RDK8
```

### Table 3

```text
Color | Meaning
Green | Approved - ready for development
Red | Not approved - not ready for development
```

### Table 4

```text
 | Type | Definition
1 | unsigned | 32-bit unsigned integer
2 | double | 64-bit double-precision floating point number
```

### Table 5

```text
 | Class | Value | Name | Description | Examples | Open
issues
1 | Generic | -32601 | Method not known | The method is not known to the version of Firebolt on this
device | Device.foo | 
2 |  | -40300 | Method not
permitted | The app does not have permission to call this method |  | 
3 |  | -32602 | Arguments invalid | The set of arguments is not valid |  | 
4 |  | -32100 | Unspecified error | Any unexpected error | Memory allocation failure, transport
failure | 
5 | Specific | -50100 | Method not
supported | A non-mandatory method that is not implemented on this
device | SecureStorage.get on a non-Comcast
device | 
6 |  |  | App state invalid | The app is not in an appropriate lifecycle state to call this
method |  | 
```

## Page 2

```text
Module Method Parameters Returns Specific API C++ JS Description         
                                            errors version                          
       1  Accessibility audioDescrip None bool None 8.0.0   Returns the audio description setting of the
               tion                                         device                  
               onAudioDesc                                                          
               riptionChang                                                         
               ed                                                                   
       2  Accessibility closedCaptio None  None   8.0.0     Returns captions settings: enabled, and a list
               nsSettings       enabled - bool              of zero or more languages in order of
                                preferredLanguages - list   decreasing preference   
               onClosedCa       of strings                                          
               ptionsSetting      [] (if not initialized)                           
               sChanged           list of one or more                               
                                  ISO 639-2/B                                       
       3  Accessibility highContrast None bool None 8.0.0   Returns the high contrast UI device setting
               UI                                                                   
               onHighContr                                                          
               astUIChanged                                                         
       4  Accessibility voiceGuidan None   None   8.0.0     Returns voice guidance settings: enabled,
               ceSettings       enabled - bool              rate, and verbosity     
                                rate - double                                       
               onVoiceGuid        1 (normal rate)                                   
               anceSettings       0.1 to 10 inclusive                               
               Changed          navigationHints - bool                              
       5  Actions start intent - string None None ???       Send an intent to the platform
                                                            Argument is a JSON document
       6  Actions intent None string       None   ???       Returns the intent that was most recently
                                                            received from the platform, as a JSON
               onIntent                                     document. Getter is typically called by an
                                                            app after transitioning to the active lifecycle
                                                            state                   
       7  Advertising advertisingId None   None   8.0.0     Returns the IFA         
                                ifa - string - a UUID                               
                                ifa_type - string, one of                           
                                  "dpid" - device                                   
                                  provided ID                                       
                                  "sspid" - SSP                                     
                                  provided ID                                       
                                  "sessionid" - session                             
                                  /synthetic ID                                     
                                lmt - string, one of                                
                                  "0"                                               
                                  "1"                                               
       8  Device uid None     string - a UUID None 8.0.0    Returns a persistent unique UUID for the
                                                            current app and device. The UUID is reset
                                                            when the app or device is reset
       9  Device deviceClass None enum     None   ???       Returns the class of the device
                                ott - no tuner/demod, no                            
                                integrated display                                  
                                stb - with tuner/demod, no                          
                                integrated display                                  
                                tv - possibly tuner/demod,                          
                                with integrated display                             
       10 Device uptime None  unsigned     None   ???       Returns the number of seconds since most
                                                            recent device boot, including any time spent
                                                            during deep sleep       
       11 Device timeInActive None unsigned App state ???   Returns the number of seconds since the
               State                       invalid          device transitioned to the ON power state
       12 Device chipsetId None string - (see Chipset Id in None ??? Returns chipset ID as a printable string, e.g.
                              Devices table)                "BCM72180"              
       13 Device hdr None                  None   8.0.0     Returns the HDR standards that are suported
                                hdr10 - bool                by the attached TV or the integral display
               onHdrChang       hdr10Plus - bool                                    
               ed               dolbyVision - bool             OTT/STB device: supported by the
                                hlg - bool                     device and indicated by the EDID of
                                                               the attached TV      
                                                               TV: supported by the device
```

### Table 1

```text
 | Module | Method | Parameters | Returns | Specific
errors | API
version | C++ | JS | Description
1 | Accessibility | audioDescrip
tion
onAudioDesc
riptionChang
ed | None | bool | None | 8.0.0 |  |  | Returns the audio description setting of the
device
2 | Accessibility | closedCaptio
nsSettings
onClosedCa
ptionsSetting
sChanged | None | enabled - bool
preferredLanguages - list
of strings
[] (if not initialized)
list of one or more
ISO 639-2/B | None | 8.0.0 |  |  | Returns captions settings: enabled, and a list
of zero or more languages in order of
decreasing preference
3 | Accessibility | highContrast
UI
onHighContr
astUIChanged | None | bool | None | 8.0.0 |  |  | Returns the high contrast UI device setting
4 | Accessibility | voiceGuidan
ceSettings
onVoiceGuid
anceSettings
Changed | None | enabled - bool
rate - double
1 (normal rate)
0.1 to 10 inclusive
navigationHints - bool | None | 8.0.0 |  |  | Returns voice guidance settings: enabled,
rate, and verbosity
5 | Actions | start | intent - string | None | None | ??? |  |  | Send an intent to the platform
Argument is a JSON document
6 | Actions | intent
onIntent | None | string | None | ??? |  |  | Returns the intent that was most recently
received from the platform, as a JSON
document. Getter is typically called by an
app after transitioning to the active lifecycle
state
7 | Advertising | advertisingId | None | ifa - string - a UUID
ifa_type - string, one of
"dpid" - device
provided ID
"sspid" - SSP
provided ID
"sessionid" - session
/synthetic ID
lmt - string, one of
"0"
"1" | None | 8.0.0 |  |  | Returns the IFA
8 | Device | uid | None | string - a UUID | None | 8.0.0 |  |  | Returns a persistent unique UUID for the
current app and device. The UUID is reset
when the app or device is reset
9 | Device | deviceClass | None | enum
ott - no tuner/demod, no
integrated display
stb - with tuner/demod, no
integrated display
tv - possibly tuner/demod,
with integrated display | None | ??? |  |  | Returns the class of the device
10 | Device | uptime | None | unsigned | None | ??? |  |  | Returns the number of seconds since most
recent device boot, including any time spent
during deep sleep
11 | Device | timeInActive
State | None | unsigned | App state
invalid | ??? |  |  | Returns the number of seconds since the
device transitioned to the ON power state
12 | Device | chipsetId | None | string - (see Chipset Id in
Devices table) | None | ??? |  |  | Returns chipset ID as a printable string, e.g.
"BCM72180"
13 | Device | hdr
onHdrChang
ed | None | hdr10 - bool
hdr10Plus - bool
dolbyVision - bool
hlg - bool | None | 8.0.0 |  |  | Returns the HDR standards that are suported
by the attached TV or the integral display
OTT/STB device: supported by the
device and indicated by the EDID of
the attached TV
TV: supported by the device
```

## Page 3

```text
14 Discovery watched   None         None   8.0.0     Notify the platform that content has been
                       entityId - string                    partially or completely watched
                       progress -                                                   
                       double -                             progress: VOD: 0 to 0.99, live: number of
                       optional                             seconds                 
                       completed -                                                  
                       bool - optional                      watchedOn: "YYYY-MM-DDThh:mm:ss.sssZ"
                       watchedOn -                                                  
                       ISO 8601 date                        agePolicy: app:adult, app:child, app:teen
                       and time in                                                  
                       UTC - optional                                               
                       agePolicy -                                                  
                       string - optional                                            
       15 Display size None                None   ???       Returns the physical dimensions of the
                                width - unsigned            connected or integral display, in centimeters
                                height - unsigned                                   
                                                            Returns 0, 0 on a OTT/STB device when a
                                                            display is not connected over HDMI
                                                            Typical values          
                                                               43" - 97, 56         
                                                               55" - 123, 71        
                                                               65" - 145, 83        
       16 Display maxResoluti None         None   ???       Returns the physical/native resolution of the
               on               width - unsigned            connected or integral display, in pixels
                                height - unsigned                                   
                                                            Returns 0, 0 on a OTT/STB device when a
                                                            display is not connected over HDMI
                                                            Typical values          
                                                               HD Ready - 1280, 720 
                                                               Full HD - 1920, 1080 
                                                               UHD - 3840, 2160     
       17 Display edid None   string - Base64 None ???      Returns the EDID (and extensions) of the
                                                            connected or integral display, as a Base64
                                                            encoded string          
                                                            Returns an empty string, "", on a OTT/STB
                                                            device when a display is not connected over
                                                            HDMI                    
       18 Firebolt apiVersion None         None   ???       Returns the Firebolt API version of the client
                                version - string            library as a semantic versioning string, and
                                major - unsigned            unsigned numbers representing the same
                                minor - unsigned            version                 
                                patch - unsigned                                    
                                                            Note: the version returned is of the client
                                                            library, not the platform
       19 Lifecycle2 close type - enum None None  8.0.0     Request the platform to deactivate the app,
                                                            and possibly take further action
                       deactivate                                                   
                       unload                               type                    
                       killReload                                                   
                       killReactivate                          deactivate - app is deactivated (if
                                                               active) - typically a user closing an app
                                                               unload - app is deactivated (if active)
                                                               and terminated - typically an app has
                                                               detected an error    
                                                               killReload - app is killed, then reloaded
                                                               to paused or suspended (by policy)
                                                               killReactivate - app is killed, reloaded,
                                                               then activated       
                                                            window.close() maps to unload
                                                            window.minimize() maps to deactivate
                                                            Module is named Lifecycle in C++ Client
                                                            Library                 
       20 Lifecycle2 state None enum       None   8.0.0     Returns the current lifecycle state of the
                                                            app. The first lifecycle state that can be
                                initializing                observed by an app/runtime is the initializing
                                active                      state                   
                                paused                                              
                                suspended                   Apps/runtimes should ordinarily use state
                                hibernated                  change notifications rather than this method
                                terminating
```

### Table 1

```text
14 | Discovery | watched | entityId - string
progress -
double -
optional
completed -
bool - optional
watchedOn -
ISO 8601 date
and time in
UTC - optional
agePolicy -
string - optional | None | None | 8.0.0 |  |  | Notify the platform that content has been
partially or completely watched
progress: VOD: 0 to 0.99, live: number of
seconds
watchedOn: "YYYY-MM-DDThh:mm:ss.sssZ"
agePolicy: app:adult, app:child, app:teen
15 | Display | size | None | width - unsigned
height - unsigned | None | ??? |  |  | Returns the physical dimensions of the
connected or integral display, in centimeters
Returns 0, 0 on a OTT/STB device when a
display is not connected over HDMI
Typical values
43" - 97, 56
55" - 123, 71
65" - 145, 83
16 | Display | maxResoluti
on | None | width - unsigned
height - unsigned | None | ??? |  |  | Returns the physical/native resolution of the
connected or integral display, in pixels
Returns 0, 0 on a OTT/STB device when a
display is not connected over HDMI
Typical values
HD Ready - 1280, 720
Full HD - 1920, 1080
UHD - 3840, 2160
17 | Display | edid | None | string - Base64 | None | ??? |  |  | Returns the EDID (and extensions) of the
connected or integral display, as a Base64
encoded string
Returns an empty string, "", on a OTT/STB
device when a display is not connected over
HDMI
18 | Firebolt | apiVersion | None | version - string
major - unsigned
minor - unsigned
patch - unsigned | None | ??? |  |  | Returns the Firebolt API version of the client
library as a semantic versioning string, and
unsigned numbers representing the same
version
Note: the version returned is of the client
library, not the platform
19 | Lifecycle2 | close | type - enum
deactivate
unload
killReload
killReactivate | None | None | 8.0.0 |  |  | Request the platform to deactivate the app,
and possibly take further action
type
deactivate - app is deactivated (if
active) - typically a user closing an app
unload - app is deactivated (if active)
and terminated - typically an app has
detected an error
killReload - app is killed, then reloaded
to paused or suspended (by policy)
killReactivate - app is killed, reloaded,
then activated
window.close() maps to unload
window.minimize() maps to deactivate
Module is named Lifecycle in C++ Client
Library
20 | Lifecycle2 | state | None | enum
initializing
active
paused
suspended
hibernated
terminating | None | 8.0.0 |  |  | Returns the current lifecycle state of the
app. The first lifecycle state that can be
observed by an app/runtime is the initializing
state
Apps/runtimes should ordinarily use state
change notifications rather than this method
```

## Page 4

```text
21 Lifecycle2 onStateChan List, of length one, of N/A N/A 8.0.0 Subscribe to/unsubscribe from lifecycle state
               ged   the lifecycle state                    changes. The app/runtime remains in the
                     change                                 initializing state until the subscribe call is
                                                            made to the platform    
                       oldState - enum                                              
                       newState -                           Notification of lifecycle state change, raised
                       enum                                 after the platform has transitioned the app
                                                            /runtime to the new lifecycle state
                                                            Note: the list always carries exactly one
                                                            lifecycle state change  
                                                            Valid transitions       
                                                              1. initializing to paused
                                                              2. initializing to suspended
                                                              3. paused to active   
                                                              4. active to paused   
                                                              5. paused to suspended
                                                              6. suspended to paused
                                                              7. suspended to hibernated
                                                              8. hibernated to suspended
                                                              9. any to terminating 
       22 Localization country None string, either None 8.0.0 Return the country, e.g. US, CA, GB, BE
               onCountryCh      "" (if not initialized)                             
               anged            ISO 3166-1 alpha-2 (see                             
                                Country in Devices table)                           
       23 Localization preferredAud None list of strings, either None 8.0.0 A list of zero or more languages in order of
               ioLanguages                                  decreasing preference. Typically two
                                [] (if not initialized)     languages are present. A language may be
               onPreferredA     list of one or more ISO     repeated in the list    
               udioLanguag      639-2/B (see Secondary                              
               esChanged        Audio Language in                                   
                                Devices table)                                      
       24 Localization presentation None string, either None 8.0.0 The presentation language of the device, e.g.
               Language                                     en-US                   
                                "" (if not initialized)                             
               onPresentati     BCP 47 (see Presentation                            
               onLanguage       Languages in Devices                                
               Changed          table)                                              
       25 Metrics ready None  None         None   8.0.0     Inform the platform that the app is minimally
                                                            usable. This method is called automatically
                                                            by Lifecycle.ready()    
       26 Metrics signIn None None         None   8.0.0     Log a sign in event, called by Discovery.
                                                            signIn()                
       27 Metrics signOut None None        None   8.0.0     Log a sign out event, called by Discovery.
                                                            signOut()               
       28 Metrics startContent None        None   8.0.0     Inform the platform that your user has started
                       entityId - string                    content                 
                       - optional                                                   
                       agePolicy -                                                  
                       string - optional                                            
       29 Metrics stopContent None         None   8.0.0     Inform the platform that your user has
                       entityId - string                    stopped content         
                       - optional                                                   
                       agePolicy -                                                  
                       string - optional                                            
       30 Metrics page        None         None   8.0.0     Inform the platform that your user has
                       pageId - string                      navigated to a page or view
                       agePolicy -                                                  
                       string - optional                                            
       31 Metrics error       None         None   8.0.0     Inform the platform of an error that has
                       type - enum                          occurred in your app    
                         network                                                    
                         media                                                      
                         restriction                                                
                         entitleme                                                  
                         nt                                                         
                         other                                                      
                       code - string                                                
                       description -                                                
                       string                                                       
                       visible - bool                                               
                       parameters -                                                 
                       arg list -                                                   
                       optional                                                     
                       agePolicy -                                                  
                       string - optional
```

### Table 1

```text
21 | Lifecycle2 | onStateChan
ged | List, of length one, of
the lifecycle state
change
oldState - enum
newState -
enum | N/A | N/A | 8.0.0 |  |  | Subscribe to/unsubscribe from lifecycle state
changes. The app/runtime remains in the
initializing state until the subscribe call is
made to the platform
Notification of lifecycle state change, raised
after the platform has transitioned the app
/runtime to the new lifecycle state
Note: the list always carries exactly one
lifecycle state change
Valid transitions
1. initializing to paused
2. initializing to suspended
3. paused to active
4. active to paused
5. paused to suspended
6. suspended to paused
7. suspended to hibernated
8. hibernated to suspended
9. any to terminating
22 | Localization | country
onCountryCh
anged | None | string, either
"" (if not initialized)
ISO 3166-1 alpha-2 (see
Country in Devices table) | None | 8.0.0 |  |  | Return the country, e.g. US, CA, GB, BE
23 | Localization | preferredAud
ioLanguages
onPreferredA
udioLanguag
esChanged | None | list of strings, either
[] (if not initialized)
list of one or more ISO
639-2/B (see Secondary
Audio Language in
Devices table) | None | 8.0.0 |  |  | A list of zero or more languages in order of
decreasing preference. Typically two
languages are present. A language may be
repeated in the list
24 | Localization | presentation
Language
onPresentati
onLanguage
Changed | None | string, either
"" (if not initialized)
BCP 47 (see Presentation
Languages in Devices
table) | None | 8.0.0 |  |  | The presentation language of the device, e.g.
en-US
25 | Metrics | ready | None | None | None | 8.0.0 |  |  | Inform the platform that the app is minimally
usable. This method is called automatically
by Lifecycle.ready()
26 | Metrics | signIn | None | None | None | 8.0.0 |  |  | Log a sign in event, called by Discovery.
signIn()
27 | Metrics | signOut | None | None | None | 8.0.0 |  |  | Log a sign out event, called by Discovery.
signOut()
28 | Metrics | startContent | entityId - string
- optional
agePolicy -
string - optional | None | None | 8.0.0 |  |  | Inform the platform that your user has started
content
29 | Metrics | stopContent | entityId - string
- optional
agePolicy -
string - optional | None | None | 8.0.0 |  |  | Inform the platform that your user has
stopped content
30 | Metrics | page | pageId - string
agePolicy -
string - optional | None | None | 8.0.0 |  |  | Inform the platform that your user has
navigated to a page or view
31 | Metrics | error | type - enum
network
media
restriction
entitleme
nt
other
code - string
description -
string
visible - bool
parameters -
arg list -
optional
agePolicy -
string - optional | None | None | 8.0.0 |  |  | Inform the platform of an error that has
occurred in your app
```

## Page 5

```text
32 Metrics mediaLoadSt None         None   8.0.0     Called when setting the URL of a media
               art     entityId - string                    asset to play, in order to infer load time
                       agePolicy -                                                  
                       string - optional                                            
       33 Metrics mediaPlay   None         None   8.0.0     Called when media playback should start due
                       entityId - string                    to autoplay, user-initiated play, or unpausing
                       agePolicy -                                                  
                       string - optional                                            
       34 Metrics mediaPlaying None        None   8.0.0     Called when media playback actually starts
                       entityId - string                    due to autoplay, user-initiated play,
                       agePolicy -                          unpausing, or recovering from a buffering
                       string - optional                    interruption            
       35 Metrics mediaPause  None         None   8.0.0     Called when media playback will pause due
                       entityId - string                    to an intentional pause operation
                       agePolicy -                                                  
                       string - optional                                            
       36 Metrics mediaWaiting None        None   8.0.0     Called when media playback will halt due to a
                       entityId - string                    network, buffer, or other unintentional
                       agePolicy -                          constraint              
                       string - optional                                            
       37 Metrics mediaSeeking None        None   8.0.0     Called when a seek is initiated during media
                       entityId - string                    playback                
                       target - double                                              
                       agePolicy -                                                  
                       string - optional                                            
       38 Metrics mediaSeeked None         None   8.0.0     Called when a seek is completed during
                       entityId - string                    media playback          
                       position -                                                   
                       double                                                       
                       agePolicy -                                                  
                       string - optional                                            
       39 Metrics mediaRateC  None         None   8.0.0     Called when the playback rate of media is
               hanged  entityId - string                    changed                 
                       rate - double                                                
                       agePolicy -                                                  
                       string - optional                                            
       40 Metrics mediaRenditi None        None   8.0.0     Called when the playback rendition (e.g.
               onChanged entityId - string                  bitrate, dimensions, profile, etc) is changed
                       bitrate -                                                    
                       unsigned                                                     
                       width -                                                      
                       unsigned                                                     
                       height -                                                     
                       unsigned                                                     
                       profile - string -                                           
                       optional                                                     
                       agePolicy -                                                  
                       string - optional                                            
       41 Metrics mediaEnded  None         None   8.0.0     Called when playback has stopped because
                       entityId - string                    the end of the media was reached
                       agePolicy -                                                  
                       string - optional                                            
       42 Metrics event       None         None   8.0.0     Inform the platform of 1st party distributor
                       schema - uri                         metrics                 
                       data - string                                                
                       agePolicy -                          data parameter is a JSON document
                       string - optional                                            
       43 Metrics appInfo     None         None   8.0.0     Inform the platform about an app's build info
                       build - string                                               
       44 Network connected None bool      None   8.0.0     Returns whether the device has a useable
                                                            network connection      
               onConnected                                                          
               Changed                                                              
       45 ParentalCo pinControl None bool  -50100 / Not ??? Returns whether PIN blocking is enabled, or
          ntrol                            supported        an error if this setting is not exposed to apps
       46 ParentalC blockNotRate None bool -50100 / Not ??? Returns whether content that is not rated
          ontrol dContent                  supported        should be blocked, or an error if this setting is
                                                            not exposed to apps     
       47 ParentalC viewingRestri None string -50100 / Not ??? Returns a JSON document describing the
          ontrol ctions                    supported        ratings schemes configured for the device
                                                            and any ratings that are blocked for that
                                                            scheme, or an error if this setting is not
                                                            exposed to apps
```

### Table 1

```text
32 | Metrics | mediaLoadSt
art | entityId - string
agePolicy -
string - optional | None | None | 8.0.0 |  |  | Called when setting the URL of a media
asset to play, in order to infer load time
33 | Metrics | mediaPlay | entityId - string
agePolicy -
string - optional | None | None | 8.0.0 |  |  | Called when media playback should start due
to autoplay, user-initiated play, or unpausing
34 | Metrics | mediaPlaying | entityId - string
agePolicy -
string - optional | None | None | 8.0.0 |  |  | Called when media playback actually starts
due to autoplay, user-initiated play,
unpausing, or recovering from a buffering
interruption
35 | Metrics | mediaPause | entityId - string
agePolicy -
string - optional | None | None | 8.0.0 |  |  | Called when media playback will pause due
to an intentional pause operation
36 | Metrics | mediaWaiting | entityId - string
agePolicy -
string - optional | None | None | 8.0.0 |  |  | Called when media playback will halt due to a
network, buffer, or other unintentional
constraint
37 | Metrics | mediaSeeking | entityId - string
target - double
agePolicy -
string - optional | None | None | 8.0.0 |  |  | Called when a seek is initiated during media
playback
38 | Metrics | mediaSeeked | entityId - string
position -
double
agePolicy -
string - optional | None | None | 8.0.0 |  |  | Called when a seek is completed during
media playback
39 | Metrics | mediaRateC
hanged | entityId - string
rate - double
agePolicy -
string - optional | None | None | 8.0.0 |  |  | Called when the playback rate of media is
changed
40 | Metrics | mediaRenditi
onChanged | entityId - string
bitrate -
unsigned
width -
unsigned
height -
unsigned
profile - string -
optional
agePolicy -
string - optional | None | None | 8.0.0 |  |  | Called when the playback rendition (e.g.
bitrate, dimensions, profile, etc) is changed
41 | Metrics | mediaEnded | entityId - string
agePolicy -
string - optional | None | None | 8.0.0 |  |  | Called when playback has stopped because
the end of the media was reached
42 | Metrics | event | schema - uri
data - string
agePolicy -
string - optional | None | None | 8.0.0 |  |  | Inform the platform of 1st party distributor
metrics
data parameter is a JSON document
43 | Metrics | appInfo | build - string | None | None | 8.0.0 |  |  | Inform the platform about an app's build info
44 | Network | connected
onConnected
Changed | None | bool | None | 8.0.0 |  |  | Returns whether the device has a useable
network connection
45 | ParentalCo
ntrol | pinControl | None | bool | -50100 / Not
supported | ??? |  |  | Returns whether PIN blocking is enabled, or
an error if this setting is not exposed to apps
46 | ParentalC
ontrol | blockNotRate
dContent | None | bool | -50100 / Not
supported | ??? |  |  | Returns whether content that is not rated
should be blocked, or an error if this setting is
not exposed to apps
47 | ParentalC
ontrol | viewingRestri
ctions | None | string | -50100 / Not
supported | ??? |  |  | Returns a JSON document describing the
ratings schemes configured for the device
and any ratings that are blocked for that
scheme, or an error if this setting is not
exposed to apps
```

## Page 6

```text
48 Presentation focused None bool   None   8.0.0     Whether the app is in focus, i.e. receiving key
                                                            presses. Provided for those apps/runtimes
               onFocusedC                                   that cannot use Wayland 
               hanged                                                               
       49 Stats memoryUsageNone            None   ???       Returns information about container memory
                                userMemoryUsed -            usage, in bytes         
                                unsigned                                            
                                userMemoryLimit -                                   
                                unsigned                                            
                                gpuMemoryUsed -                                     
                                unsigned                                            
                                gpuMemoryLimit -                                    
                                unsigned                                            
       50 TextToSpe speak text - string    None   8.0.0     Speak the utterance immediately. Any
          ech                   speechid - unsigned         ongoing speech is interrupted
                                TTS_Status - 0...3                                  
                                success - bool              Text argument is either plain text or a well-
                                                            formed SSML document    
                                                            TTS_Status, not success attribute, to be
                                                            used by caller to indicate success of call
                                                            0 OK, 1 Fail, 2 not enabled, 3 invalid
                                                            configuration           
                                                            Raises onSpeechinterrupted if speaking is
                                                            interrupted             
       51 TextToSpe pause speechid - unsigned None 8.0.0    Pauses the utterance    
          ech                   TTS_Status - 0...3                                  
                                success - bool              Raises onSpeechpause if ongoing speech is
                                                            paused                  
                                                            Does nothing if utterance is already paused
       52 TextToSpe resume speechid - unsigned None 8.0.0   Continue the paused utterance
          ech                   TTS_Status - 0...3                                  
                                success - bool              Raises onSpeechresume if paused speech is
                                                            resumed                 
                                                            Does nothing if the utterance is not paused
       53 TextToSpe cancel speechid - unsigned None 8.0.0   Stop speaking if utterance is currently being
          ech                   TTS_Status - 0...3          spoken                  
                                success - bool                                      
                                                            Raises onSpeechinterrupted if speaking was
                                                            interrupted             
       54 TextToSpe getspeechsta speechid - unsigned None 8.0.0 Returns the state of the utterance
          ech  te               speechstate - enum                                  
                                  SPEECH_PENDING                                    
                                  SPEECH_IN_PROG                                    
                                  RESS                                              
                                  SPEECH_PAUSED                                     
                                  SPEECH_NOT_FO                                     
                                  UND                                               
                                TTS_Status - 0...3                                  
                                success - bool                                      
       55 TextToSpe onWillspeak speechid - unsigned N/A N/A 8.0.0 Text to speech conversion is about to start
          ech                                                                       
       56 TextToSpe onSpeechsta speechid - unsigned N/A N/A 8.0.0 Utterance is about to be spoken
          ech  rt                                                                   
       57 TextToSpe onSpeechpa speechid - unsigned N/A N/A 8.0.0 Ongoing speech was paused
          ech  use                                                                  
       58 TextToSpe onSpeechres speechid - unsigned N/A N/A 8.0.0 Paused speech was resumed
          ech  ume                                                                  
       59 TextToSpe onSpeechco speechid - unsigned N/A N/A 8.0.0 Speech completed successfully
          ech  mplete                                                               
       60 TextToSpe onSpeechint speechid - unsigned N/A N/A 8.0.0 Speech was stopped, due to another call to
          ech  errupted                                     speak or cancel         
       61 TextToSpe onNetworker speechid - unsigned N/A N/A 8.0.0 Utterance failed due to network
          ech  ror                                                                  
       62 TextToSpe onPlaybacke speechid - unsigned N/A N/A 8.0.0 Utterance failed during playback
          ech  rror                                                                 
       63 TextToSpe listvoices language - string - None 8.0.0 Returns the list of available voices as human-
          ech        BCP 47     TTS_Status - 0...3          readable strings, e.g. "ava", "amelie",
                                voices - list of one or     "angelica"              
                                more strings
```

### Table 1

```text
48 | Presentation | focused
onFocusedC
hanged | None | bool | None | 8.0.0 |  |  | Whether the app is in focus, i.e. receiving key
presses. Provided for those apps/runtimes
that cannot use Wayland
49 | Stats | memoryUsage | None | userMemoryUsed -
unsigned
userMemoryLimit -
unsigned
gpuMemoryUsed -
unsigned
gpuMemoryLimit -
unsigned | None | ??? |  |  | Returns information about container memory
usage, in bytes
50 | TextToSpe
ech | speak | text - string | speechid - unsigned
TTS_Status - 0...3
success - bool | None | 8.0.0 |  |  | Speak the utterance immediately. Any
ongoing speech is interrupted
Text argument is either plain text or a well-
formed SSML document
TTS_Status, not success attribute, to be
used by caller to indicate success of call
0 OK, 1 Fail, 2 not enabled, 3 invalid
configuration
Raises onSpeechinterrupted if speaking is
interrupted
51 | TextToSpe
ech | pause | speechid - unsigned | TTS_Status - 0...3
success - bool | None | 8.0.0 |  |  | Pauses the utterance
Raises onSpeechpause if ongoing speech is
paused
Does nothing if utterance is already paused
52 | TextToSpe
ech | resume | speechid - unsigned | TTS_Status - 0...3
success - bool | None | 8.0.0 |  |  | Continue the paused utterance
Raises onSpeechresume if paused speech is
resumed
Does nothing if the utterance is not paused
53 | TextToSpe
ech | cancel | speechid - unsigned | TTS_Status - 0...3
success - bool | None | 8.0.0 |  |  | Stop speaking if utterance is currently being
spoken
Raises onSpeechinterrupted if speaking was
interrupted
54 | TextToSpe
ech | getspeechsta
te | speechid - unsigned | speechstate - enum
SPEECH_PENDING
SPEECH_IN_PROG
RESS
SPEECH_PAUSED
SPEECH_NOT_FO
UND
TTS_Status - 0...3
success - bool | None | 8.0.0 |  |  | Returns the state of the utterance
55 | TextToSpe
ech | onWillspeak | speechid - unsigned | N/A | N/A | 8.0.0 |  |  | Text to speech conversion is about to start
56 | TextToSpe
ech | onSpeechsta
rt | speechid - unsigned | N/A | N/A | 8.0.0 |  |  | Utterance is about to be spoken
57 | TextToSpe
ech | onSpeechpa
use | speechid - unsigned | N/A | N/A | 8.0.0 |  |  | Ongoing speech was paused
58 | TextToSpe
ech | onSpeechres
ume | speechid - unsigned | N/A | N/A | 8.0.0 |  |  | Paused speech was resumed
59 | TextToSpe
ech | onSpeechco
mplete | speechid - unsigned | N/A | N/A | 8.0.0 |  |  | Speech completed successfully
60 | TextToSpe
ech | onSpeechint
errupted | speechid - unsigned | N/A | N/A | 8.0.0 |  |  | Speech was stopped, due to another call to
speak or cancel
61 | TextToSpe
ech | onNetworker
ror | speechid - unsigned | N/A | N/A | 8.0.0 |  |  | Utterance failed due to network
62 | TextToSpe
ech | onPlaybacke
rror | speechid - unsigned | N/A | N/A | 8.0.0 |  |  | Utterance failed during playback
63 | TextToSpe
ech | listvoices | language - string -
BCP 47 | TTS_Status - 0...3
voices - list of one or
more strings | None | 8.0.0 |  |  | Returns the list of available voices as human-
readable strings, e.g. "ava", "amelie",
"angelica"
```
