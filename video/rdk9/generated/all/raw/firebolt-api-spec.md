# Extracted firebolt-api-spec

Source: `Firebolt 9 API Specifications.pdf`
SHA-256: `8fde64f796a393013fe4bed659b8cf74d3b746e9b693b55071db078cd164990e`

> This file is generated from the PDF for review. It is not a replacement for the curated JSON.

## Page 1

```text
Firebolt®  9 API  Specification                                              
                                                                                    
        Document status DRAFT                                                       
                                                                                    
        Author    Andrew Bennett                                                    
                                                                                    
                                                                                    
       Note: this is a draft of the latest Firebolt spec                            
                                                                                    
                                                                                    
        API version Link Summary                                                    
                                                                                    
       internal draft                                                               
                                                                                    
       Interpretation                                                               
                                                                                    
       This page is an abstract, language-independent definition of the Firebolt Core API. The following terms are used:
                                                                                    
           Term    Meaning                                                          
       1  enum     an instance of a type that can have one of a pre-defined set of values. Typically represented by a string in JSON-RPC, but an
                   integer in C++                                                   
       2  list of  an ordered collection of values                                  
       3  list of... an unordered collection of values                              
          unordered                                                                 
       4  one of   an instance of a primitive type, such as unsigned or string, that can have one of a pre-defined set of values. Not an enum
                                                                                    
       5  monotonic a numeric value that is greater than the last instance of that attribute
       6  generic error an error that can be returned by any method call, documented in the Errors section
       7  specific error an error that can be returned by specific methods, documented along with the method
                                                                                    
                                                                                    
       Key                                                                          
                                                                                    
        Color Meaning                                                               
       Green Approved - ready for development                                       
                                                                                    
       Red  Not approved - not ready for development                                
                                                                                    
       Types                                                                        
                                                                                    
           Type Definition                                                          
                                                                                    
       1  unsigned 32-bit unsigned integer                                          
       2  double 64-bit double-precision floating point number                      
                                                                                    
                                                                                    
       Errors                                                                       
                                                                                    
           Class Value Name  Description           Examples          Open issues    
       1  Generic -32601 Method not known The method is not known to the version of Device.foo
                             Firebolt on this device                                
       2       -40300 Method not The app does not have permission to call this      
                   permitted method
```

### Table 1

```text
Document status | DRAFT
Author | Andrew Bennett
```

### Table 2

```text
API version | Link | Summary
internal draft |  | 
```

### Table 3

```text
 | Term | Meaning
1 | enum | an instance of a type that can have one of a pre-defined set of values. Typically represented by a string in JSON-RPC, but an
integer in C++
2 | list of | an ordered collection of values
3 | list of...
unordered | an unordered collection of values
4 | one of | an instance of a primitive type, such as unsigned or string, that can have one of a pre-defined set of values. Not an enum
5 | monotonic | a numeric value that is greater than the last instance of that attribute
6 | generic error | an error that can be returned by any method call, documented in the Errors section
7 | specific error | an error that can be returned by specific methods, documented along with the method
```

### Table 4

```text
Color | Meaning
Green | Approved - ready for development
Red | Not approved - not ready for development
```

### Table 5

```text
 | Type | Definition
1 | unsigned | 32-bit unsigned integer
2 | double | 64-bit double-precision floating point number
```

### Table 6

```text
 | Class | Value | Name | Description | Examples | Open issues
1 | Generic | -32601 | Method not known | The method is not known to the version of
Firebolt on this device | Device.foo | 
2 |  | -40300 | Method not
permitted | The app does not have permission to call this
method |  | 
```

## Page 2

```text
3       -32602 Arguments invalid The set of arguments is not valid           
       4       -32100 Unspecified error Any unexpected error Memory allocation failure, transport
                                                  failure                           
       5  Specific -50100 Method not A non-mandatory method that is not SecureStorage.get on a non-Comcast
                   supported implemented on this device device                      
       6       -xxxxx App state invalid The app is not in an appropriate lifecycle state to Sathish to assign
                             call this method                       the error value 
       7       -xxxxx Speech synthesis No speech synthesis engine is available or the Sathish to assign
                   engine error engine rejected the request         the error value 
       8       -xxxxx Wrong device class The method is not appropriate for this class of App is incorrectly calling VideoOutput. Sathish to assign
                             device               cecState on a TV device the error value
       Methods                                                                      
                                                                                    
           Module Method Parameters Returns Specific API Deprecated C++17 JS Description
                                   errors version API version                       
       1  Accessibility audioDescri None bool None 8.0.0  Returns the audio description setting of the device
               ption                                                                
               onAudioDes                                                           
               criptionChan                                                         
               ged                                                                  
       2  Accessibility closedCapti None None 8.0.0       Returns captions settings: enabled, and a list of zero or more
               onsSettings  enabled - bool                languages in order of decreasing preference
                            preferredLangua                                         
               onClosedCa   ges - list of                                           
               ptionsSettin strings                                                 
               gsChanged      [] (if not                                            
                              initialized)                                          
                              list of one                                           
                              or more                                               
                              ISO 639-2                                             
                              /B                                                    
       3  Accessibility highContrast None bool None 8.0.0 Returns the high contrast UI device setting
               UI                                                                   
               onHighContr                                                          
               astUIChang                                                           
               ed                                                                   
       4  Accessibility voiceGuidan None None 8.0.0       Returns voice guidance settings: enabled, rate, and verbosity
               ceSettings   enabled - bool                                          
                            rate - double                                           
               onVoiceGui     1 (normal                                             
               danceSettin    rate)                                                 
               gsChanged      0.1 to 10                                             
                              inclusive                                             
                            navigationHints                                         
                            - bool                                                  
       5  Actions start   None    None  9.0.0             Send an intent to the platform
                      intent -                                                      
                      json                                Argument is a JSON document
                      handlerA                                                      
                      ppId -                                                        
                      string -                                                      
                      optional                                                      
       6  Actions intent None     None  9.0.0             Returns the intent that was most recently received from the
                            intentId -                    platform, as a JSON document. Getter is typically called by
               onIntent     unsigned -                    an app after transitioning to the active lifecycle state
                            monotonic                                               
                            intent - json                                           
       7  Advertising advertisingId None None 8.0.0       Returns the IFA           
                            ifa - string - a                                        
                            UUID                                                    
                            ifa_type - string,                                      
                            one of                                                  
                              "dpid" -                                              
                              device                                                
                              provided                                              
                              ID                                                    
                              "sspid" -                                             
                              SSP                                                   
                              provided                                              
                              ID                                                    
                              "sessionid                                            
                              " -                                                   
                              session                                               
                              /synthetic                                            
                              ID                                                    
                            lmt - string, one                                       
                            of                                                      
                              "0"                                                   
                              "1"                                                   
       8  Audio volume None unsigned -xxxxx / 9.0.0       Returns the current volume level of the device or HDMI-
                                  Wrong                   connected audio output device. Range is 0 to 100 inclusive
               onVolumeC          device class                                      
               hanged                                     OTT/STB device: returns Wrong device class error
```

### Table 1

```text
 |  |  |  |  |  | 
3 |  | -32602 | Arguments invalid | The set of arguments is not valid |  | 
4 |  | -32100 | Unspecified error | Any unexpected error | Memory allocation failure, transport
failure | 
5 | Specific | -50100 | Method not
supported | A non-mandatory method that is not
implemented on this device | SecureStorage.get on a non-Comcast
device | 
6 |  | -xxxxx | App state invalid | The app is not in an appropriate lifecycle state to
call this method |  | Sathish to assign
the error value
7 |  | -xxxxx | Speech synthesis
engine error | No speech synthesis engine is available or the
engine rejected the request |  | Sathish to assign
the error value
8 |  | -xxxxx | Wrong device class | The method is not appropriate for this class of
device | App is incorrectly calling VideoOutput.
cecState on a TV device | Sathish to assign
the error value
```

### Table 2

```text
 | Module | Method | Parameters | Returns | Specific
errors | API
version | Deprecated
API version | C++17 | JS | Description
1 | Accessibility | audioDescri
ption
onAudioDes
criptionChan
ged | None | bool | None | 8.0.0 |  |  |  | Returns the audio description setting of the device
2 | Accessibility | closedCapti
onsSettings
onClosedCa
ptionsSettin
gsChanged | None | enabled - bool
preferredLangua
ges - list of
strings
[] (if not
initialized)
list of one
or more
ISO 639-2
/B | None | 8.0.0 |  |  |  | Returns captions settings: enabled, and a list of zero or more
languages in order of decreasing preference
3 | Accessibility | highContrast
UI
onHighContr
astUIChang
ed | None | bool | None | 8.0.0 |  |  |  | Returns the high contrast UI device setting
4 | Accessibility | voiceGuidan
ceSettings
onVoiceGui
danceSettin
gsChanged | None | enabled - bool
rate - double
1 (normal
rate)
0.1 to 10
inclusive
navigationHints
- bool | None | 8.0.0 |  |  |  | Returns voice guidance settings: enabled, rate, and verbosity
5 | Actions | start | intent -
json
handlerA
ppId -
string -
optional | None | None | 9.0.0 |  |  |  | Send an intent to the platform
Argument is a JSON document
6 | Actions | intent
onIntent | None | intentId -
unsigned -
monotonic
intent - json | None | 9.0.0 |  |  |  | Returns the intent that was most recently received from the
platform, as a JSON document. Getter is typically called by
an app after transitioning to the active lifecycle state
7 | Advertising | advertisingId | None | ifa - string - a
UUID
ifa_type - string,
one of
"dpid" -
device
provided
ID
"sspid" -
SSP
provided
ID
"sessionid
" -
session
/synthetic
ID
lmt - string, one
of
"0"
"1" | None | 8.0.0 |  |  |  | Returns the IFA
8 | Audio | volume
onVolumeC
hanged | None | unsigned | -xxxxx /
Wrong
device class | 9.0.0 |  |  |  | Returns the current volume level of the device or HDMI-
connected audio output device. Range is 0 to 100 inclusive
OTT/STB device: returns Wrong device class error
```

## Page 3

```text
9  Audio mute None bool    -xxxxx / 9.0.0          Returns the current mute state of the device or HDMI-
                                  Wrong                   connected audio output device. Mute is independent of
               onMuteCha          device class            current volume            
               nged                                                                 
                                                          OTT/STB device: returns Wrong device class error
       10 Device uid None string - a UUID None 8.0.0      Returns a persistent unique UUID for the current app and
                                                          device. The UUID is reset when the app or device is reset
       11 Device deviceClass None enum None 9.0.0         Returns the class of the device
                            ott - no tuner                                          
                            /demod, no                                              
                            integrated                                              
                            display                                                 
                            stb - with tuner                                        
                            /demod, no                                              
                            integrated                                              
                            display                                                 
                            tv - possibly                                           
                            tuner/demod,                                            
                            with integrated                                         
                            display                                                 
       12 Device uptime None unsigned None 9.0.0          Returns the number of seconds since most recent device
                                                          boot, including any time spent during deep sleep
       13 Device timeInActive None unsigned App state 9.0.0 Returns the number of seconds since the device transitioned
               State              invalid                 to the ON power state     
       14 Device chipsetId None string - (see Chipset Id None 9.0.0 Returns chipset ID as a printable string, e.g. "BCM72180"
                          in Devices table)                                         
       15 Device hdr None         None  8.0.0             Returns the HDR standards that are suported by the
                            hdr10 - bool                  attached TV or the integral display
               onHdrChang   hdr10Plus - bool                                        
               ed           dolbyVision -                   OTT/STB device: supported by the device and
                            bool                            indicated by the EDID of the attached TV
                            hlg - bool                      TV: supported by the device
       16 Device dolbyAtmos None bool None 9.0.0          Returns whether the user would get a Dolby Atmos
               ExperienceA                                experience if a Dolby Atmos track were to be played at this
               vailable                                   time                      
               onDolbyAtm                                                           
               osExperienc                                                          
               eAvailableC                                                          
               hanged                                                               
       17 Device manufacture None string None 9.0.0       Returns the manufacturer responsible for building the
               r                                          hardware                  
       18 Device brandName None string, either None 9.0.0 Returns the brand name under which the device was
                                                          marketed to consumers. Typically also shown on the TV
                            "" (if not                    bezel, device label or remote
                            initialized)                                            
                            1 or more                                               
                            characters                                              
       19 Device modelId None string None 9.0.0           Returns the model identifier assigned to the device
                                                          hardware. Typically also shown on the device label or UI
       20 Device osName None string None 9.0.0            Returns the operating system name as defined by the
                                                          operator                  
       21 Device osVersion None string None 9.0.0         Returns the operating system version as defined by the
                                                          operator                  
       22 Device firmware None string None 9.0.0          Returns a string that identifies the firmware image of the
                                                          device                    
       23 Device name None string None  9.0.0             Returns the device friendly name. Used by network services
                                                          (DIAL, Miracast, AirPlay) so that other devices can more
               onNameCha                                  easily identify this device during device discovery
               nged                                                                 
       24 Discovery watched None  None  8.0.0             Notify the platform that content has been partially or
                      entityId -                          completely watched        
                      string                                                        
                      progress                            progress: VOD: 0 to 0.99, live: number of seconds
                      - double                                                      
                      - optional                                                    
                                                          watchedOn: "YYYY-MM-DDThh:mm:ss.sssZ"
                      complete                                                      
                      d - bool -                                                    
                      optional                            agePolicy: app:adult, app:child, app:teen
                      watched                                                       
                      On - ISO                                                      
                      8601                                                          
                      date and                                                      
                      time in                                                       
                      UTC -                                                         
                      optional                                                      
                      agePolicy                                                     
                      - string -                                                    
                      optional                                                      
       25 Display size None       None  9.0.0             Returns the physical dimensions of the connected or integral
                            width - unsigned              display, in centimeters   
                            height - unsigned                                       
                                                          Returns 0, 0 on a OTT/STB device when a display is not
                                                          connected over HDMI       
                                                          Typical values            
                                                            43" - 97, 56            
                                                            55" - 123, 71           
                                                            65" - 145, 83
```

### Table 1

```text
9 | Audio | mute
onMuteCha
nged | None | bool | -xxxxx /
Wrong
device class | 9.0.0 |  |  |  | Returns the current mute state of the device or HDMI-
connected audio output device. Mute is independent of
current volume
OTT/STB device: returns Wrong device class error
10 | Device | uid | None | string - a UUID | None | 8.0.0 |  |  |  | Returns a persistent unique UUID for the current app and
device. The UUID is reset when the app or device is reset
11 | Device | deviceClass | None | enum
ott - no tuner
/demod, no
integrated
display
stb - with tuner
/demod, no
integrated
display
tv - possibly
tuner/demod,
with integrated
display | None | 9.0.0 |  |  |  | Returns the class of the device
12 | Device | uptime | None | unsigned | None | 9.0.0 |  |  |  | Returns the number of seconds since most recent device
boot, including any time spent during deep sleep
13 | Device | timeInActive
State | None | unsigned | App state
invalid | 9.0.0 |  |  |  | Returns the number of seconds since the device transitioned
to the ON power state
14 | Device | chipsetId | None | string - (see Chipset Id
in Devices table) | None | 9.0.0 |  |  |  | Returns chipset ID as a printable string, e.g. "BCM72180"
15 | Device | hdr
onHdrChang
ed | None | hdr10 - bool
hdr10Plus - bool
dolbyVision -
bool
hlg - bool | None | 8.0.0 |  |  |  | Returns the HDR standards that are suported by the
attached TV or the integral display
OTT/STB device: supported by the device and
indicated by the EDID of the attached TV
TV: supported by the device
16 | Device | dolbyAtmos
ExperienceA
vailable
onDolbyAtm
osExperienc
eAvailableC
hanged | None | bool | None | 9.0.0 |  |  |  | Returns whether the user would get a Dolby Atmos
experience if a Dolby Atmos track were to be played at this
time
17 | Device | manufacture
r | None | string | None | 9.0.0 |  |  |  | Returns the manufacturer responsible for building the
hardware
18 | Device | brandName | None | string, either
"" (if not
initialized)
1 or more
characters | None | 9.0.0 |  |  |  | Returns the brand name under which the device was
marketed to consumers. Typically also shown on the TV
bezel, device label or remote
19 | Device | modelId | None | string | None | 9.0.0 |  |  |  | Returns the model identifier assigned to the device
hardware. Typically also shown on the device label or UI
20 | Device | osName | None | string | None | 9.0.0 |  |  |  | Returns the operating system name as defined by the
operator
21 | Device | osVersion | None | string | None | 9.0.0 |  |  |  | Returns the operating system version as defined by the
operator
22 | Device | firmware | None | string | None | 9.0.0 |  |  |  | Returns a string that identifies the firmware image of the
device
23 | Device | name
onNameCha
nged | None | string | None | 9.0.0 |  |  |  | Returns the device friendly name. Used by network services
(DIAL, Miracast, AirPlay) so that other devices can more
easily identify this device during device discovery
24 | Discovery | watched | entityId -
string
progress
- double
- optional
complete
d - bool -
optional
watched
On - ISO
8601
date and
time in
UTC -
optional
agePolicy
- string -
optional | None | None | 8.0.0 |  |  |  | Notify the platform that content has been partially or
completely watched
progress: VOD: 0 to 0.99, live: number of seconds
watchedOn: "YYYY-MM-DDThh:mm:ss.sssZ"
agePolicy: app:adult, app:child, app:teen
25 | Display | size | None | width - unsigned
height - unsigned | None | 9.0.0 |  |  |  | Returns the physical dimensions of the connected or integral
display, in centimeters
Returns 0, 0 on a OTT/STB device when a display is not
connected over HDMI
Typical values
43" - 97, 56
55" - 123, 71
65" - 145, 83
```

## Page 4

```text
26 Display maxResoluti None None 9.0.0             Returns the physical/native resolution of the connected or
               on           width - unsigned              integral display, in pixels
                            height - unsigned                                       
                                                          Returns 0, 0 on a OTT/STB device when a display is not
                                                          connected over HDMI       
                                                          Typical values            
                                                            HD Ready - 1280, 720    
                                                            Full HD - 1920, 1080    
                                                            UHD - 3840, 2160        
       27 Display edid None string - Base64 None 9.0.0    Returns the EDID (and extensions) of the connected or
                                                          integral display, as a Base64 encoded string
                                                          Returns an empty string, "", on a OTT/STB device when a
                                                          display is not connected over HDMI
       28 Display colorimetry None list of enum, unordered None 9.0.0 Returns an unordered list of colorimetry values supported by
                                                          the attached TV or integral display. Returns an empty list if
                            bt709                         no TV is attached         
                            bt2020                                                  
       29 Display videoResolu None list of enum, unordered None 9.0.0 Returns an unordered list of HD video resolutions and frame
               tions                                      rates supported by the attached TV or integral
                            720p50                        display. Returns an empty list if no TV is attached
                            720p60                                                  
                            1080p50                                                 
                            1080p60                                                 
                            2160p50                                                 
                            2160p60                                                 
       30 Display connected None bool None 9.0.0          Returns whether the device is currently connected to an
                                                          external or integrated display
               onConnecte                                                           
               dChanged                                   Most apps should instead use VideoOutput.hdcp for display
                                                          connectivity              
                                                          OTT/STB device: returns true if a TV is connected over
                                                          HDMI (by hot plug detect pin 19), otherwise returns false
                                                          TV device: returns true   
       31 Lifecycle2 close type - enum None None 8.0.0    Request the platform to deactivate the app, and possibly take
                                                          further action            
                      deactivate                                                    
                      unload                              type                      
                      killReload                                                    
                      killReacti                            deactivate - app is deactivated (if active) - typically a
                      vate                                  user closing an app     
                                                            unload - app is deactivated (if active) and terminated -
                                                            typically an app has detected an error
                                                            killReload - app is killed, then reloaded to paused or
                                                            suspended (by policy)   
                                                            killReactivate - app is killed, reloaded, then activated
                                                          window.close() maps to unload
                                                          window.minimize() maps to deactivate
                                                          Module is named Lifecycle in C++ Client Library
       32 Lifecycle2 state None enum None 8.0.0           Returns the current lifecycle state of the app. The first
                                                          lifecycle state that can be observed by an app/runtime is the
                            initializing                  initializing state        
                            active                                                  
                            paused                        Apps/runtimes should ordinarily use state change
                            suspended                     notifications rather than this method
                            hibernated                                              
                            terminating                                             
       33 Lifecycle2 onStateCha List, of length N/A N/A 8.0.0 Subscribe to/unsubscribe from lifecycle state changes. The
               nged one, of the                           app/runtime remains in the initializing state until the
                   lifecycle state                        subscribe call is made to the platform
                   change                                                           
                                                          Notification of lifecycle state change, raised after the platform
                      oldState                            has transitioned the app/runtime to the new lifecycle state
                      - enum                                                        
                      newState                            Note: the list always carries exactly one lifecycle state change
                      - enum                                                        
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
       34 Localization country None string, either None 8.0.0 Return the country, e.g. US, CA, GB, BE
               onCountryC   "" (if not                                              
               hanged       initialized)                                            
                            ISO 3166-1                                              
                            alpha-2 (see                                            
                            Country in                                              
                            Devices table)
```

### Table 1

```text
26 | Display | maxResoluti
on | None | width - unsigned
height - unsigned | None | 9.0.0 |  |  |  | Returns the physical/native resolution of the connected or
integral display, in pixels
Returns 0, 0 on a OTT/STB device when a display is not
connected over HDMI
Typical values
HD Ready - 1280, 720
Full HD - 1920, 1080
UHD - 3840, 2160
27 | Display | edid | None | string - Base64 | None | 9.0.0 |  |  |  | Returns the EDID (and extensions) of the connected or
integral display, as a Base64 encoded string
Returns an empty string, "", on a OTT/STB device when a
display is not connected over HDMI
28 | Display | colorimetry | None | list of enum, unordered
bt709
bt2020 | None | 9.0.0 |  |  |  | Returns an unordered list of colorimetry values supported by
the attached TV or integral display. Returns an empty list if
no TV is attached
29 | Display | videoResolu
tions | None | list of enum, unordered
720p50
720p60
1080p50
1080p60
2160p50
2160p60 | None | 9.0.0 |  |  |  | Returns an unordered list of HD video resolutions and frame
rates supported by the attached TV or integral
display. Returns an empty list if no TV is attached
30 | Display | connected
onConnecte
dChanged | None | bool | None | 9.0.0 |  |  |  | Returns whether the device is currently connected to an
external or integrated display
Most apps should instead use VideoOutput.hdcp for display
connectivity
OTT/STB device: returns true if a TV is connected over
HDMI (by hot plug detect pin 19), otherwise returns false
TV device: returns true
31 | Lifecycle2 | close | type - enum
deactivate
unload
killReload
killReacti
vate | None | None | 8.0.0 |  |  |  | Request the platform to deactivate the app, and possibly take
further action
type
deactivate - app is deactivated (if active) - typically a
user closing an app
unload - app is deactivated (if active) and terminated -
typically an app has detected an error
killReload - app is killed, then reloaded to paused or
suspended (by policy)
killReactivate - app is killed, reloaded, then activated
window.close() maps to unload
window.minimize() maps to deactivate
Module is named Lifecycle in C++ Client Library
32 | Lifecycle2 | state | None | enum
initializing
active
paused
suspended
hibernated
terminating | None | 8.0.0 |  |  |  | Returns the current lifecycle state of the app. The first
lifecycle state that can be observed by an app/runtime is the
initializing state
Apps/runtimes should ordinarily use state change
notifications rather than this method
33 | Lifecycle2 | onStateCha
nged | List, of length
one, of the
lifecycle state
change
oldState
- enum
newState
- enum | N/A | N/A | 8.0.0 |  |  |  | Subscribe to/unsubscribe from lifecycle state changes. The
app/runtime remains in the initializing state until the
subscribe call is made to the platform
Notification of lifecycle state change, raised after the platform
has transitioned the app/runtime to the new lifecycle state
Note: the list always carries exactly one lifecycle state change
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
34 | Localization | country
onCountryC
hanged | None | string, either
"" (if not
initialized)
ISO 3166-1
alpha-2 (see
Country in
Devices table) | None | 8.0.0 |  |  |  | Return the country, e.g. US, CA, GB, BE
```

## Page 5

```text
35 Localization preferredAu None list of strings, either None 8.0.0 A list of zero or more languages in order of decreasing
               dioLanguag                                 preference. Typically two languages are present. A
               es           [] (if not                    language may be repeated in the list
                            initialized)                                            
               onPreferred  list of one or                                          
               AudioLangu   more ISO 639-2                                          
               agesChanged  /B (see                                                 
                            Secondary                                               
                            Audio Language                                          
                            in Devices table)                                       
       36 Localization presentation None string, either None 8.0.0 The presentation language of the device, e.g. en-US
               Language                                                             
                            "" (if not                                              
               onPresentati initialized)                                            
               onLanguage   BCP 47 (see                                             
               Changed      Presentation                                            
                            Languages in                                            
                            Devices table)                                          
       37 Localization timeZone None string None 9.0.0    Returns the current time zone in IANA format, e.g. America
                                                          /New_York                 
               onTimeZone                                                           
               Changed                                                              
       38 Metrics ready None None None  8.0.0             Inform the platform that the app is minimally usable
       39 Metrics signIn None None None 8.0.0             Log a sign in event       
       40 Metrics signOut None None None 8.0.0            Log a sign out event      
       41 Metrics startContent None None 8.0.0            Inform the platform that your user has started content
                      entityId -                                                    
                      string -                                                      
                      optional                                                      
                      agePolicy                                                     
                      - string -                                                    
                      optional                                                      
       42 Metrics stopContent None None 8.0.0             Inform the platform that your user has stopped content
                      entityId -                                                    
                      string -                                                      
                      optional                                                      
                      agePolicy                                                     
                      - string -                                                    
                      optional                                                      
       43 Metrics page    None    None  8.0.0             Inform the platform that your user has navigated to a page or
                      pageId -                            view                      
                      string                                                        
                      agePolicy                                                     
                      - string -                                                    
                      optional                                                      
       44 Metrics error   None    None  8.0.0             Inform the platform of an error that has occurred in your app
                      type -                                                        
                      enum                                                          
                        ne                                                          
                        tw                                                          
                        ork                                                         
                        m                                                           
                        ed                                                          
                        ia                                                          
                        re                                                          
                        str                                                         
                        icti                                                        
                        on                                                          
                        en                                                          
                        titl                                                        
                        e                                                           
                        m                                                           
                        ent                                                         
                        ot                                                          
                        her                                                         
                      code -                                                        
                      string                                                        
                      descriptio                                                    
                      n - string                                                    
                      visible -                                                     
                      bool                                                          
                      paramete                                                      
                      rs - arg                                                      
                      list -                                                        
                      optional                                                      
                      agePolicy                                                     
                      - string -                                                    
                      optional                                                      
       45 Metrics mediaLoadS None None  8.0.0             Called when setting the URL of a media asset to play, in
               tart   entityId -                          order to infer load time  
                      string                                                        
                      agePolicy                                                     
                      - string -                                                    
                      optional                                                      
       46 Metrics mediaPlay None  None  8.0.0             Called when media playback should start due to autoplay,
                      entityId -                          user-initiated play, or unpausing
                      string                                                        
                      agePolicy                                                     
                      - string -                                                    
                      optional
```

### Table 1

```text
35 | Localization | preferredAu
dioLanguag
es
onPreferred
AudioLangu
agesChanged | None | list of strings, either
[] (if not
initialized)
list of one or
more ISO 639-2
/B (see
Secondary
Audio Language
in Devices table) | None | 8.0.0 |  |  |  | A list of zero or more languages in order of decreasing
preference. Typically two languages are present. A
language may be repeated in the list
36 | Localization | presentation
Language
onPresentati
onLanguage
Changed | None | string, either
"" (if not
initialized)
BCP 47 (see
Presentation
Languages in
Devices table) | None | 8.0.0 |  |  |  | The presentation language of the device, e.g. en-US
37 | Localization | timeZone
onTimeZone
Changed | None | string | None | 9.0.0 |  |  |  | Returns the current time zone in IANA format, e.g. America
/New_York
38 | Metrics | ready | None | None | None | 8.0.0 |  |  |  | Inform the platform that the app is minimally usable
39 | Metrics | signIn | None | None | None | 8.0.0 |  |  |  | Log a sign in event
40 | Metrics | signOut | None | None | None | 8.0.0 |  |  |  | Log a sign out event
41 | Metrics | startContent | entityId -
string -
optional
agePolicy
- string -
optional | None | None | 8.0.0 |  |  |  | Inform the platform that your user has started content
42 | Metrics | stopContent | entityId -
string -
optional
agePolicy
- string -
optional | None | None | 8.0.0 |  |  |  | Inform the platform that your user has stopped content
43 | Metrics | page | pageId -
string
agePolicy
- string -
optional | None | None | 8.0.0 |  |  |  | Inform the platform that your user has navigated to a page or
view
44 | Metrics | error | type -
enum
ne
tw
ork
m
ed
ia
re
str
icti
on
en
titl
e
m
ent
ot
her
code -
string
descriptio
n - string
visible -
bool
paramete
rs - arg
list -
optional
agePolicy
- string -
optional | None | None | 8.0.0 |  |  |  | Inform the platform of an error that has occurred in your app
45 | Metrics | mediaLoadS
tart | entityId -
string
agePolicy
- string -
optional | None | None | 8.0.0 |  |  |  | Called when setting the URL of a media asset to play, in
order to infer load time
46 | Metrics | mediaPlay | entityId -
string
agePolicy
- string -
optional | None | None | 8.0.0 |  |  |  | Called when media playback should start due to autoplay,
user-initiated play, or unpausing
```

## Page 6

```text
47 Metrics mediaPlaying None None 8.0.0            Called when media playback actually starts due to autoplay,
                      entityId -                          user-initiated play, unpausing, or recovering from a buffering
                      string                              interruption              
                      agePolicy                                                     
                      - string -                                                    
                      optional                                                      
       48 Metrics mediaPause None None  8.0.0             Called when media playback will pause due to an intentional
                      entityId -                          pause operation           
                      string                                                        
                      agePolicy                                                     
                      - string -                                                    
                      optional                                                      
       49 Metrics mediaWaiting None None 8.0.0            Called when media playback will halt due to a network,
                      entityId -                          buffer, or other unintentional constraint
                      string                                                        
                      agePolicy                                                     
                      - string -                                                    
                      optional                                                      
       50 Metrics mediaSeeki None None  8.0.0             Called when a seek is initiated during media playback
               ng     entityId -                                                    
                      string                                                        
                      target -                                                      
                      double                                                        
                      agePolicy                                                     
                      - string -                                                    
                      optional                                                      
       51 Metrics mediaSeeked None None 8.0.0             Called when a seek is completed during media playback
                      entityId -                                                    
                      string                                                        
                      position -                                                    
                      double                                                        
                      agePolicy                                                     
                      - string -                                                    
                      optional                                                      
       52 Metrics mediaRateC None None  8.0.0             Called when the playback rate of media is changed
               hanged entityId -                                                    
                      string                                                        
                      rate -                                                        
                      double                                                        
                      agePolicy                                                     
                      - string -                                                    
                      optional                                                      
       53 Metrics mediaRendit None None 8.0.0             Called when the playback rendition (e.g. bitrate, dimensions,
               ionChanged entityId -                      profile, etc) is changed  
                      string                                                        
                      bitrate -                                                     
                      unsigned                                                      
                      width -                                                       
                      unsigned                                                      
                      height -                                                      
                      unsigned                                                      
                      profile -                                                     
                      string -                                                      
                      optional                                                      
                      agePolicy                                                     
                      - string -                                                    
                      optional                                                      
       54 Metrics mediaEnded None None  8.0.0             Called when playback has stopped because the end of the
                      entityId -                          media was reached         
                      string                                                        
                      agePolicy                                                     
                      - string -                                                    
                      optional                                                      
       55 Metrics event   None    None  8.0.0             Inform the platform of 1st party distributor metrics
                      schema -                                                      
                      uri                                 data parameter is a JSON document
                      data -                                                        
                      string                                                        
                      agePolicy                                                     
                      - string -                                                    
                      optional                                                      
       56 Metrics appInfo None    None  8.0.0             Inform the platform about an app's build info
                      build -                                                       
                      string                                                        
       57 Network connected None bool None 8.0.0          Returns whether the device has a usable network connection
               onConnecte                                                           
               dChanged
```

### Table 1

```text
47 | Metrics | mediaPlaying | entityId -
string
agePolicy
- string -
optional | None | None | 8.0.0 |  |  |  | Called when media playback actually starts due to autoplay,
user-initiated play, unpausing, or recovering from a buffering
interruption
48 | Metrics | mediaPause | entityId -
string
agePolicy
- string -
optional | None | None | 8.0.0 |  |  |  | Called when media playback will pause due to an intentional
pause operation
49 | Metrics | mediaWaiting | entityId -
string
agePolicy
- string -
optional | None | None | 8.0.0 |  |  |  | Called when media playback will halt due to a network,
buffer, or other unintentional constraint
50 | Metrics | mediaSeeki
ng | entityId -
string
target -
double
agePolicy
- string -
optional | None | None | 8.0.0 |  |  |  | Called when a seek is initiated during media playback
51 | Metrics | mediaSeeked | entityId -
string
position -
double
agePolicy
- string -
optional | None | None | 8.0.0 |  |  |  | Called when a seek is completed during media playback
52 | Metrics | mediaRateC
hanged | entityId -
string
rate -
double
agePolicy
- string -
optional | None | None | 8.0.0 |  |  |  | Called when the playback rate of media is changed
53 | Metrics | mediaRendit
ionChanged | entityId -
string
bitrate -
unsigned
width -
unsigned
height -
unsigned
profile -
string -
optional
agePolicy
- string -
optional | None | None | 8.0.0 |  |  |  | Called when the playback rendition (e.g. bitrate, dimensions,
profile, etc) is changed
54 | Metrics | mediaEnded | entityId -
string
agePolicy
- string -
optional | None | None | 8.0.0 |  |  |  | Called when playback has stopped because the end of the
media was reached
55 | Metrics | event | schema -
uri
data -
string
agePolicy
- string -
optional | None | None | 8.0.0 |  |  |  | Inform the platform of 1st party distributor metrics
data parameter is a JSON document
56 | Metrics | appInfo | build -
string | None | None | 8.0.0 |  |  |  | Inform the platform about an app's build info
57 | Network | connected
onConnecte
dChanged | None | bool | None | 8.0.0 |  |  |  | Returns whether the device has a usable network connection
```

## Page 7

```text
58 Network interfaces None List of one or more None 9.0.0 Returns information about all physical network interfaces of
                          objects, unordered              the device                
                            name - string                 name - e.g. wlan0         
                            type - enum                                             
                              wired                       protocol - physical layer protocol supported by the interface,
                              wifi                        set to unknown by default 
                            protocol - enum                                         
                              unknown                     connected - the link link layer status
                              100base_                                              
                              tx                                                    
                              1000base                    preferred - true if the interface is used for network traffic
                              _t                                                    
                              802_11ac                                              
                              802_11ax                                              
                              802_11be                                              
                            enabled - bool                                          
                            connected - bool                                        
                            preferred - bool                                        
       59 Network interfaceStat interfaceName - -xxxxx / Not 9.0.0 Returns basic information about a network interface
               us  string   name - string found                                     
                            enabled - bool                                          
               onInterfaceS connected - bool                                        
               tatusChanged preferred - bool                                        
       60 Network interfaceCon interfaceName - List of one or more -xxxxx / Not 9.0.0 Returns the IP configuration of an interface
               fig string objects, unordered found                                  
               onInterface  ipv4Address -                                           
               ConfigChan   string                                                  
               ged          ipv4DNSAddress                                          
                            es - list of zero                                       
                            or more strings                                         
                            ipv6Addresses -                                         
                            list of zero or                                         
                            more strings                                            
                            ipv6DNSAddress                                          
                            es - list of zero                                       
                            or more strings                                         
       61 Network interfaceStat interfaceName - -xxxxx / Not 9.0.0 Returns statistics for a network interface
               istics string interfaceStats - found                                 
                            object - optional             interfaceStats - present when an interface is
                              txPackets                   connected. Attributes are set to null if not available
                              -                                                     
                              unsigned                                              
                                                          wirelessStats - present when an interface of type wifi is
                              | null                                                
                                                          connected. Attributes are set to null if not available
                              txError -                                             
                              unsigned                                              
                              | null                      wirelessFrequency - MHz   
                              txDroppe                                              
                              d -                         wirelessSignal - dBm, -96 (weakest) to 0 (strongest) inclusive
                              unsigned                                              
                              | null                      wirelessQuality - current SNR in dB, 0 to 96 inclusive
                              txFifoErro                                            
                              rs -                        wirelessTxBitrate - Tx rate in Mbps
                              unsigned                                              
                              | null                                                
                              txCarrierE                  wirelessRxBitrate - Rx rate in Mbps
                              rrors -                                               
                              unsigned                    wirelessInactiveTime - time in milliseconds since last activity
                              | null                                                
                              rxPackets                                             
                              -                                                     
                              unsigned                                              
                              | null                                                
                              rxError -                                             
                              unsigned                                              
                              | null                                                
                              rxDroppe                                              
                              d -                                                   
                              unsigned                                              
                              | null                                                
                              rxFifoErro                                            
                              rs -                                                  
                              unsigned                                              
                              | null                                                
                              rxFrameE                                              
                              rrors -                                               
                              unsigned                                              
                              | null                                                
                              linkTxBitR                                            
                              ate -                                                 
                              unsigned                                              
                              | null                                                
                              linkRxBit                                             
                              Rate -                                                
                              unsigned                                              
                              | null
```

### Table 1

```text
58 | Network | interfaces | None | List of one or more
objects, unordered
name - string
type - enum
wired
wifi
protocol - enum
unknown
100base_
tx
1000base
_t
802_11ac
802_11ax
802_11be
enabled - bool
connected - bool
preferred - bool | None | 9.0.0 |  |  |  | Returns information about all physical network interfaces of
the device
name - e.g. wlan0
protocol - physical layer protocol supported by the interface,
set to unknown by default
connected - the link link layer status
preferred - true if the interface is used for network traffic
59 | Network | interfaceStat
us
onInterfaceS
tatusChanged | interfaceName -
string | name - string
enabled - bool
connected - bool
preferred - bool | -xxxxx / Not
found | 9.0.0 |  |  |  | Returns basic information about a network interface
60 | Network | interfaceCon
fig
onInterface
ConfigChan
ged | interfaceName -
string | List of one or more
objects, unordered
ipv4Address -
string
ipv4DNSAddress
es - list of zero
or more strings
ipv6Addresses -
list of zero or
more strings
ipv6DNSAddress
es - list of zero
or more strings | -xxxxx / Not
found | 9.0.0 |  |  |  | Returns the IP configuration of an interface
61 | Network | interfaceStat
istics | interfaceName -
string | interfaceStats -
object - optional
txPackets
-
unsigned
| null
txError -
unsigned
| null
txDroppe
d -
unsigned
| null
txFifoErro
rs -
unsigned
| null
txCarrierE
rrors -
unsigned
| null
rxPackets
-
unsigned
| null
rxError -
unsigned
| null
rxDroppe
d -
unsigned
| null
rxFifoErro
rs -
unsigned
| null
rxFrameE
rrors -
unsigned
| null
linkTxBitR
ate -
unsigned
| null
linkRxBit
Rate -
unsigned
| null | -xxxxx / Not
found | 9.0.0 |  |  |  | Returns statistics for a network interface
interfaceStats - present when an interface is
connected. Attributes are set to null if not available
wirelessStats - present when an interface of type wifi is
connected. Attributes are set to null if not available
wirelessFrequency - MHz
wirelessSignal - dBm, -96 (weakest) to 0 (strongest) inclusive
wirelessQuality - current SNR in dB, 0 to 96 inclusive
wirelessTxBitrate - Tx rate in Mbps
wirelessRxBitrate - Rx rate in Mbps
wirelessInactiveTime - time in milliseconds since last activity
 |  |  |  |  |  |  |  |  |  | 
```

## Page 8

```text
wirelessStats -                                         
                            object - optional                                       
                              wirelessF                                             
                              requency                                              
                              -                                                     
                              unsigned                                              
                              | null                                                
                              wirelessQ                                             
                              uality -                                              
                              unsigned                                              
                              | null                                                
                              wirelessSi                                            
                              gnal -                                                
                              integer |                                             
                              null                                                  
                              wirelessT                                             
                              xBitrate -                                            
                              unsigned                                              
                              | null                                                
                              wirelessR                                             
                              xBitrate -                                            
                              unsigned                                              
                              | null                                                
                              wirelessIn                                            
                              activeTim                                             
                              e -                                                   
                              unsigned                                              
                              | null                                                
                              wirelessR                                             
                              xBytes -                                              
                              unsigned                                              
                              | null                                                
                              wirelessR                                             
                              xPackets                                              
                              -                                                     
                              unsigned                                              
                              | null                                                
                              wirelessR                                             
                              xDropped                                              
                              -                                                     
                              unsigned                                              
                              | null                                                
                              wirelessT                                             
                              xBytes -                                              
                              unsigned                                              
                              | null                                                
                              wirelessT                                             
                              xPackets                                              
                              -                                                     
                              unsigned                                              
                              | null                                                
                              wirelessT                                             
                              xRetries -                                            
                              unsigned                                              
                              | null                                                
                              wirelessT                                             
                              xFailed -                                             
                              unsigned                                              
                              | null                                                
                              wirelessE                                             
                              xpectedT                                              
                              hroughput                                             
                              -                                                     
                              unsigned                                              
                              | null                                                
       62 Network interfaceDet interfaceName - -xxxxx / Not 9.0.0 Returns detailed information of a network interface
               ails string  name - string found                                     
                            ssid - string -               Used to convey information which may be sensitive e.g perso
               onInterface  optional                      nally identifiable information
               DetailsChan  bssid - string -                                        
               ged          optional                      ssid - the SSID of the access point, provided for wifi interface
                                                          type if connected         
                                                          bssid - the BSSID of the access point, provided for wifi
                                                          interface type if connected
       63 ParentalCon pinControl None bool -50100 / Not ??? Returns whether PIN blocking is enabled, or an error if this
          trol                    supported               setting is not exposed to apps
       64 ParentalCon blockNotRat None bool -50100 / Not ??? Returns whether content that is not rated should be blocked,
          trol edContent          supported               or an error if this setting is not exposed to apps
       65 ParentalCon viewingRest None string -50100 / Not ??? Returns a JSON document describing the ratings schemes
          trol rictions           supported               configured for the device and any ratings that are blocked
                                                          for that scheme, or an error if this setting is not exposed to
                                                          apps                      
       66 Presentation focused None bool None 8.0.0       Whether the app is in focus, i.e. receiving key
                                                          presses. Provided for those apps/runtimes that cannot use
               onFocusedC                                 Wayland                   
               hanged                                                               
       67 SpeechSynt voices None List of zero or more, None 9.0.0 Returns a list of available voices
          hesis           unordered                                                 
               onVoicesCh                                   name - name of the voice as a human-readable string
               anged        name - string                   lang - the language of the voice in BCP 47
                            lang - string -                 default - true if the voice is the default for the language
                            BCP 47                                                  
                            default - bool                An empty list is returned if a speech synthesis engine is not
                                                          available, or the engine rejected the request
                                                          A particular voice can be repeated in the list, and a language
                                                          can be repeated in the list
                                                          At most one voice is the default for each language
```

### Table 1

```text
 |  |  |  |  |  |  |  |  |  | 
 |  |  |  | wirelessStats -
object - optional
wirelessF
requency
-
unsigned
| null
wirelessQ
uality -
unsigned
| null
wirelessSi
gnal -
integer |
null
wirelessT
xBitrate -
unsigned
| null
wirelessR
xBitrate -
unsigned
| null
wirelessIn
activeTim
e -
unsigned
| null
wirelessR
xBytes -
unsigned
| null
wirelessR
xPackets
-
unsigned
| null
wirelessR
xDropped
-
unsigned
| null
wirelessT
xBytes -
unsigned
| null
wirelessT
xPackets
-
unsigned
| null
wirelessT
xRetries -
unsigned
| null
wirelessT
xFailed -
unsigned
| null
wirelessE
xpectedT
hroughput
-
unsigned
| null |  |  |  |  |  | 
62 | Network | interfaceDet
ails
onInterface
DetailsChan
ged | interfaceName -
string | name - string
ssid - string -
optional
bssid - string -
optional | -xxxxx / Not
found | 9.0.0 |  |  |  | Returns detailed information of a network interface
Used to convey information which may be sensitive e.g perso
nally identifiable information
ssid - the SSID of the access point, provided for wifi interface
type if connected
bssid - the BSSID of the access point, provided for wifi
interface type if connected
63 | ParentalCon
trol | pinControl | None | bool | -50100 / Not
supported | ??? |  |  |  | Returns whether PIN blocking is enabled, or an error if this
setting is not exposed to apps
64 | ParentalCon
trol | blockNotRat
edContent | None | bool | -50100 / Not
supported | ??? |  |  |  | Returns whether content that is not rated should be blocked,
or an error if this setting is not exposed to apps
65 | ParentalCon
trol | viewingRest
rictions | None | string | -50100 / Not
supported | ??? |  |  |  | Returns a JSON document describing the ratings schemes
configured for the device and any ratings that are blocked
for that scheme, or an error if this setting is not exposed to
apps
66 | Presentation | focused
onFocusedC
hanged | None | bool | None | 8.0.0 |  |  |  | Whether the app is in focus, i.e. receiving key
presses. Provided for those apps/runtimes that cannot use
Wayland
67 | SpeechSynt
hesis | voices
onVoicesCh
anged | None | List of zero or more,
unordered
name - string
lang - string -
BCP 47
default - bool | None | 9.0.0 |  |  |  | Returns a list of available voices
name - name of the voice as a human-readable string
lang - the language of the voice in BCP 47
default - true if the voice is the default for the language
An empty list is returned if a speech synthesis engine is not
available, or the engine rejected the request
A particular voice can be repeated in the list, and a language
can be repeated in the list
At most one voice is the default for each language
```

## Page 9

```text
68 SpeechSynt speak unsigned -xxxxx / Spee 9.0.0   Requests the system to speak an utterance. Returns an
          hesis       text -      ch synthesis            utteranceId if the request is accepted, otherwise an error is
                      string      engine error            returned. A successful new request is processed
                      lang -                              asynchronously: any utterance that is currently being spoken
                      string -                            is interrupted and notified by onUtteranceEvent( interrupted ),
                      BCP 47 -                            and events for the new request are raised using
                      optional                            onUtteranceEvent          
                      voice -                                                       
                      string -                              text - plain text or a well-formed SSML document
                      optional                              lang - the language of the text in BCP 47
                      volume -                              voice - as returned by the voices method
                      double -                              volume - the speaking volume, 0 (lowest) to 1
                      optional                              (highest) inclusive     
                      rate - dou                            rate - the speaking rate, 0.1 (slowest) to 10 (fastest)
                      ble -                                 inclusive               
                      optional                              pitch - the speaking pitch, 0 (lowest) to 2 (highest)
                      pitch - do                            inclusive               
                      uble -                                pii - true if the text contains personally identifiable
                      optional                              information, indicating that functionality such as
                      pii - bool -                          logging and telemetry should be restricted, false if not
                      optional                              set                     
                                                          For Voice Guidance, the app SHOULD either supply the text
                                                          parameter as plain text and the lang parameter, or supply
                                                          text as a well-formed SSML document. If text is plain text
                                                          and lang is not supplied then the default speech synthesis
                                                          language is used - this is not recommended usage
       69 SpeechSynt cancel utteranceId - None -xxxxx / Spee 9.0.0 Stop the utterance. If playing, audio is stopped. If
          hesis    unsigned       ch synthesis            synthesizing or paused, the utterance will not be played
                                  engine error                                      
                                                          Raises onUtteranceEvent( interrupted ) if the utterance was s
                                                          ynthesizing, playing or paused
                                                          Returns without error in all utterance states, or if the
                                                          utterance has finished    
       70 SpeechSynt pause utteranceId - None -xxxxx / Spee 9.0.0 Pause the utterance. If playing, audio is stopped. If the
          hesis    unsigned       ch synthesis            utterance was synthesizing, playback will be prevented
                                  engine error                                      
                                                          Raises onUtteranceEvent( paused ) if the utterance was
                                                          synthesizing or playing   
                                                          Returns without error in all utterance states, or if the
                                                          utterance has finished    
       71 SpeechSynt resume utteranceId - None -xxxxx / Spee 9.0.0 Resume an utterance. If paused, audio is resumed. If
          hesis    unsigned       ch synthesis            synthesizing the utterance will be played. If playing no action
                                  engine error            is taken                  
                                                          Raises onUtteranceEvent( resumed ) if the utterance had
                                                          previously been paused while playing
                                                          Returns without error in all utterance states, or if the
                                                          utterance has finished    
       72 SpeechSynt onUtterance N/A N/A 9.0.0            Notifies events related to an utterance
          hesis Event utteranceI                                                    
                      d -                                 Progress events           
                      unsigned                                                      
                      event -                                                       
                                                            synthesisStarting - text to audio conversion is being
                      enum                                                          
                                                            started                 
                        sy                                                          
                                                            playbackStarting - audio playback is being started
                        nt                                                          
                                                            paused - utterance has been paused while playing
                        he                                                          
                                                            resumed - an utterance that had previously been
                        sis                                                         
                                                            paused while playing has resumed playing
                        St                                                          
                                                            completed - the utterance has completed successfully
                        art                                                         
                                                            interrupted - the utterance has been stopped due to a
                        ing                                                         
                                                            call to either the speak or cancel methods
                        pl                                                          
                        ay                                Failure events            
                        ba                                                          
                        ck                                                          
                        St                                  networkFailed - the system was unable to contact the
                        art                                 voice synthesis backend 
                        ing                                 synthesisFailed - the system was unable to
                        pa                                  synthesize some or all of the utterance
                        us                                  playbackFailed - the system was unable to play some
                        ed                                  or all of the utterance 
                        re                                                          
                        su                                                          
                        m                                                           
                        ed                                                          
                        co                                                          
                        m                                                           
                        pl                                                          
                        et                                                          
                        ed                                                          
                        int                                                         
                        err                                                         
                        up                                                          
                        ted                                                         
                        ne                                                          
                        tw                                                          
                        or                                                          
                        kF                                                          
                        ail                                                         
                        ed                                                          
                        sy                                                          
                        nt                                                          
                        he                                                          
                        sis                                                         
                        Fa                                                          
                        iled                                                        
                        pl                                                          
                        ay                                                          
                        ba                                                          
                        ck                                                          
                        Fa                                                          
                        iled
```

### Table 1

```text
68 | SpeechSynt
hesis | speak | text -
string
lang -
string -
BCP 47 -
optional
voice -
string -
optional
volume -
double -
optional
rate - dou
ble -
optional
pitch - do
uble -
optional
pii - bool -
optional | unsigned | -xxxxx / Spee
ch synthesis
engine error | 9.0.0 |  |  |  | Requests the system to speak an utterance. Returns an
utteranceId if the request is accepted, otherwise an error is
returned. A successful new request is processed
asynchronously: any utterance that is currently being spoken
is interrupted and notified by onUtteranceEvent( interrupted ),
and events for the new request are raised using
onUtteranceEvent
text - plain text or a well-formed SSML document
lang - the language of the text in BCP 47
voice - as returned by the voices method
volume - the speaking volume, 0 (lowest) to 1
(highest) inclusive
rate - the speaking rate, 0.1 (slowest) to 10 (fastest)
inclusive
pitch - the speaking pitch, 0 (lowest) to 2 (highest)
inclusive
pii - true if the text contains personally identifiable
information, indicating that functionality such as
logging and telemetry should be restricted, false if not
set
For Voice Guidance, the app SHOULD either supply the text
parameter as plain text and the lang parameter, or supply
text as a well-formed SSML document. If text is plain text
and lang is not supplied then the default speech synthesis
language is used - this is not recommended usage
69 | SpeechSynt
hesis | cancel | utteranceId -
unsigned | None | -xxxxx / Spee
ch synthesis
engine error | 9.0.0 |  |  |  | Stop the utterance. If playing, audio is stopped. If
synthesizing or paused, the utterance will not be played
Raises onUtteranceEvent( interrupted ) if the utterance was s
ynthesizing, playing or paused
Returns without error in all utterance states, or if the
utterance has finished
70 | SpeechSynt
hesis | pause | utteranceId -
unsigned | None | -xxxxx / Spee
ch synthesis
engine error | 9.0.0 |  |  |  | Pause the utterance. If playing, audio is stopped. If the
utterance was synthesizing, playback will be prevented
Raises onUtteranceEvent( paused ) if the utterance was
synthesizing or playing
Returns without error in all utterance states, or if the
utterance has finished
71 | SpeechSynt
hesis | resume | utteranceId -
unsigned | None | -xxxxx / Spee
ch synthesis
engine error | 9.0.0 |  |  |  | Resume an utterance. If paused, audio is resumed. If
synthesizing the utterance will be played. If playing no action
is taken
Raises onUtteranceEvent( resumed ) if the utterance had
previously been paused while playing
Returns without error in all utterance states, or if the
utterance has finished
72 | SpeechSynt
hesis | onUtterance
Event | utteranceI
d -
unsigned
event -
enum
sy
nt
he
sis
St
art
ing
pl
ay
ba
ck
St
art
ing
pa
us
ed
re
su
m
ed
co
m
pl
et
ed
int
err
up
ted
ne
tw
or
kF
ail
ed
sy
nt
he
sis
Fa
iled
pl
ay
ba
ck
Fa
iled | N/A | N/A | 9.0.0 |  |  |  | Notifies events related to an utterance
Progress events
synthesisStarting - text to audio conversion is being
started
playbackStarting - audio playback is being started
paused - utterance has been paused while playing
resumed - an utterance that had previously been
paused while playing has resumed playing
completed - the utterance has completed successfully
interrupted - the utterance has been stopped due to a
call to either the speak or cancel methods
Failure events
networkFailed - the system was unable to contact the
voice synthesis backend
synthesisFailed - the system was unable to
synthesize some or all of the utterance
playbackFailed - the system was unable to play some
or all of the utterance
```

## Page 10

```text
73 Stats memoryUsa None    None  9.0.0             Returns information about container memory usage, in bytes
               ge           userMemoryUse                                           
                            d - unsigned                                            
                            userMemoryLimit                                         
                            - unsigned                                              
                            gpuMemoryUsed                                           
                            - unsigned                                              
                            gpuMemoryLimit                                          
                            - unsigned                                              
       74 TextToSpee speak text - string None 8.0.0 9.0.0 Speak the utterance immediately. Any ongoing speech is
          ch                speechid -                    interrupted               
                            unsigned                                                
                            TTS_Status - 0...             Text argument is either plain text or a well-formed SSML
                            3                             document                  
                            success - bool                                          
                                                          TTS_Status, not success attribute, to be used by caller to
                                                          indicate success of call  
                                                          0 OK, 1 Fail, 2 not enabled, 3 invalid configuration
                                                          Raises onSpeechInterrupted if speaking is interrupted
       75 TextToSpee pause speechid - None 8.0.0 9.0.0    Pauses the utterance      
          ch       unsigned TTS_Status - 0...                                       
                            3                             Raises onSpeechPause if ongoing speech is paused
                            success - bool                                          
                                                          Does nothing if utterance is already paused
       76 TextToSpee resume speechid - None 8.0.0 9.0.0   Continue the paused utterance
          ch       unsigned TTS_Status - 0...                                       
                            3                             Raises onSpeechResume if paused speech is resumed
                            success - bool                                          
                                                          Does nothing if the utterance is not paused
       77 TextToSpee cancel speechid - None 8.0.0 9.0.0   Stop speaking if utterance is currently being spoken
          ch       unsigned TTS_Status - 0...                                       
                            3                             Raises onSpeechInterrupted if speaking was interrupted
                            success - bool                                          
       78 TextToSpee getSpeechS speechid - None 8.0.0 9.0.0 Returns the state of the utterance
          ch   tate unsigned speechstate -                                          
                            enum                                                    
                              SPEECH                                                
                              _PENDING                                              
                              SPEECH                                                
                              _IN_PRO                                               
                              GRESS                                                 
                              SPEECH                                                
                              _PAUSED                                               
                              SPEECH                                                
                              _NOT_F                                                
                              OUND                                                  
                            TTS_Status - 0...                                       
                            3                                                       
                            success - bool                                          
       79 TextToSpee onWillSpeak speechid - N/A N/A 8.0.0 9.0.0 Text to speech conversion is about to start
          ch       unsigned                                                         
       80 TextToSpee onSpeechSt speechid - N/A N/A 8.0.0 9.0.0 Utterance is about to be spoken
          ch   art unsigned                                                         
       81 TextToSpee onSpeechP speechid - N/A N/A 8.0.0 9.0.0 Ongoing speech was paused
          ch   ause unsigned                                                        
       82 TextToSpee onSpeechR speechid - N/A N/A 8.0.0 9.0.0 Paused speech was resumed
          ch   esume unsigned                                                       
       83 TextToSpee onSpeechC speechid - N/A N/A 8.0.0 9.0.0 Speech completed successfully
          ch   omplete unsigned                                                     
       84 TextToSpee onSpeechInt speechid - N/A N/A 8.0.0 9.0.0 Speech was stopped, due to another call to speak or cancel
          ch   errupted unsigned                                                    
       85 TextToSpee onNetworkE speechid - N/A N/A 8.0.0 9.0.0 Utterance failed due to network
          ch   rror unsigned                                                        
       86 TextToSpee onPlayback speechid - N/A N/A 8.0.0 9.0.0 Utterance failed during playback
          ch   Error unsigned                                                       
       87 TextToSpee listVoices language - None 8.0.0 9.0.0 Returns the list of available voices as human-readable
          ch       string - BCP 47 TTS_Status - 0...      strings, e.g. "ava", "amelie", "angelica"
                            3                                                       
                            voices - list of                                        
                            one or more                                             
                            strings                                                 
       88 VideoOutput resolution None None 9.0.0          Returns the width and height of the video signal on the video
                            width - unsigned              output, in pixels. Typically used by a streaming app to
               onResolutio  height - unsigned             determine the highest resolution of video to select
               nChanged                                                             
                          One of                          OTT/STB device: returns the video resolution over HDMI
                            720, 480                      TV device: returns the resolution of the panel
                            720, 576                                                
                            1280, 720                                               
                            1920, 1080                                              
                            3840, 2160                                              
       89 VideoOutput hdcp None enum None 9.0.0           Returns the current state of output protection on the video
                                                          output                    
               onHdcpCha    hdcp1.4                                                 
               nged         hdcp2.2                       OTT/STB device: returns the negotiated HDCP version on
                            none                          the video output, or none if an encrypted connection has not
                            direct                        been made between the OTT/STB device and any attached
                                                          TV                        
                                                          TV device: returns direct
```

### Table 1

```text
73 | Stats | memoryUsa
ge | None | userMemoryUse
d - unsigned
userMemoryLimit
- unsigned
gpuMemoryUsed
- unsigned
gpuMemoryLimit
- unsigned | None | 9.0.0 |  |  |  | Returns information about container memory usage, in bytes
74 | TextToSpee
ch | speak | text - string | speechid -
unsigned
TTS_Status - 0...
3
success - bool | None | 8.0.0 | 9.0.0 |  |  | Speak the utterance immediately. Any ongoing speech is
interrupted
Text argument is either plain text or a well-formed SSML
document
TTS_Status, not success attribute, to be used by caller to
indicate success of call
0 OK, 1 Fail, 2 not enabled, 3 invalid configuration
Raises onSpeechInterrupted if speaking is interrupted
75 | TextToSpee
ch | pause | speechid -
unsigned | TTS_Status - 0...
3
success - bool | None | 8.0.0 | 9.0.0 |  |  | Pauses the utterance
Raises onSpeechPause if ongoing speech is paused
Does nothing if utterance is already paused
76 | TextToSpee
ch | resume | speechid -
unsigned | TTS_Status - 0...
3
success - bool | None | 8.0.0 | 9.0.0 |  |  | Continue the paused utterance
Raises onSpeechResume if paused speech is resumed
Does nothing if the utterance is not paused
77 | TextToSpee
ch | cancel | speechid -
unsigned | TTS_Status - 0...
3
success - bool | None | 8.0.0 | 9.0.0 |  |  | Stop speaking if utterance is currently being spoken
Raises onSpeechInterrupted if speaking was interrupted
78 | TextToSpee
ch | getSpeechS
tate | speechid -
unsigned | speechstate -
enum
SPEECH
_PENDING
SPEECH
_IN_PRO
GRESS
SPEECH
_PAUSED
SPEECH
_NOT_F
OUND
TTS_Status - 0...
3
success - bool | None | 8.0.0 | 9.0.0 |  |  | Returns the state of the utterance
79 | TextToSpee
ch | onWillSpeak | speechid -
unsigned | N/A | N/A | 8.0.0 | 9.0.0 |  |  | Text to speech conversion is about to start
80 | TextToSpee
ch | onSpeechSt
art | speechid -
unsigned | N/A | N/A | 8.0.0 | 9.0.0 |  |  | Utterance is about to be spoken
81 | TextToSpee
ch | onSpeechP
ause | speechid -
unsigned | N/A | N/A | 8.0.0 | 9.0.0 |  |  | Ongoing speech was paused
82 | TextToSpee
ch | onSpeechR
esume | speechid -
unsigned | N/A | N/A | 8.0.0 | 9.0.0 |  |  | Paused speech was resumed
83 | TextToSpee
ch | onSpeechC
omplete | speechid -
unsigned | N/A | N/A | 8.0.0 | 9.0.0 |  |  | Speech completed successfully
84 | TextToSpee
ch | onSpeechInt
errupted | speechid -
unsigned | N/A | N/A | 8.0.0 | 9.0.0 |  |  | Speech was stopped, due to another call to speak or cancel
85 | TextToSpee
ch | onNetworkE
rror | speechid -
unsigned | N/A | N/A | 8.0.0 | 9.0.0 |  |  | Utterance failed due to network
86 | TextToSpee
ch | onPlayback
Error | speechid -
unsigned | N/A | N/A | 8.0.0 | 9.0.0 |  |  | Utterance failed during playback
87 | TextToSpee
ch | listVoices | language -
string - BCP 47 | TTS_Status - 0...
3
voices - list of
one or more
strings | None | 8.0.0 | 9.0.0 |  |  | Returns the list of available voices as human-readable
strings, e.g. "ava", "amelie", "angelica"
88 | VideoOutput | resolution
onResolutio
nChanged | None | width - unsigned
height - unsigned
One of
720, 480
720, 576
1280, 720
1920, 1080
3840, 2160 | None | 9.0.0 |  |  |  | Returns the width and height of the video signal on the video
output, in pixels. Typically used by a streaming app to
determine the highest resolution of video to select
OTT/STB device: returns the video resolution over HDMI
TV device: returns the resolution of the panel
89 | VideoOutput | hdcp
onHdcpCha
nged | None | enum
hdcp1.4
hdcp2.2
none
direct | None | 9.0.0 |  |  |  | Returns the current state of output protection on the video
output
OTT/STB device: returns the negotiated HDCP version on
the video output, or none if an encrypted connection has not
been made between the OTT/STB device and any attached
TV
TV device: returns direct
```

## Page 11

```text
90 VideoOutput cecState None enum -xxxxx / 9.0.0   Returns whether the output of the OTT/STB device is actively
                                  Wrong                   being displayed on the TV 
               onCecState   active device class                                     
               Changed      inactive                      OTT/STB device: returns the current state of the HDMI CEC
                            unsupported                   connection                
                                                            active - the TV is on and the OTT/STB device is the
                                                            active source           
                                                            inactive - the TV is off or the OTT/STB device is not
                                                            the active source       
                                                            unsupported - CEC is not enabled on the TV
                                                          TV device: returns Wrong device class error
       91 VideoOutput refreshRate None enum None 9.0.0    Returns the refresh rate of the video signal on the video
                                                          output, in Hz             
               onRefreshR   0                                                       
               ateChanged   23.976                        OTT/STB device: returns the refresh rate, or 0 if no TV is
                            24                            attached                  
                            25                                                      
                            29.97                         TV device: returns the compositor refresh rate currently used
                            30                            to output content to the integrated display
                            50                                                      
                            59.94                                                   
                            60                                                      
       92 VideoOutput colorDepth None enum None 9.0.0     Returns the video color depth being used on the video
                                                          output, in bits           
                            0                                                       
                            8                             OTT/STB device: in addition, returns 0 when a display is not
                            10                            connected over HDMI       
                            12                                                      
                                                          TV device: does not return 0
       93 VideoOutput colorFormat None enum None 9.0.0    Returns the current color format of the video signal on the
                                                          active video output port or integrated display
                            ycbcr420                                                
                            ycbcr422                      OTT/STB device: in addition, returns none when a display is
                            ycbcr444                      not connected over HDMI   
                            rgb444                                                  
                            none                          TV device: does not return none
       94 VideoOutput colorimetry None enum None 9.0.0    Returns the current colorimetry value of the video signal on
                                                          the active video output port or integrated display
                            bt2020rgb                                               
                            bt2020ycc                     OTT/STB device: in addition, returns none when a display is
                            bt709                         not connected over HDMI   
                            oprgb                                                   
                            none                          TV device: does not return none
       95 VideoOutput dynamicRan None enum None 9.0.0     Returns the current dynamic range format of the video signal
               ge                                         on the video output       
                            hdr10                                                   
                            hdr10plus                     OTT/STB device: in addition, returns none when a display is
                            dolbyVision                   not connected over HDMI   
                            hlg                                                     
                            sdr                           TV device: does not return none
                            none                                                    
       96 VideoOutput quantization None enum None 9.0.0   Returns the quantization range used on the video output
               Range                                                                
                            limited                       OTT/STB device: in addition, returns none when a display is
                            full                          not connected over HDMI   
                            none                                                    
                                                          TV device: does not return none
       97 Window addKeyInter None None  9.0.0             Adds the supplied list of keys to the set of keys that are
               cepts  keys - list                         received by this app when it is in the Active lifecycle state but
                      of one or                           not in focus. The key is represented by the JS event.key
                      more                                attribute defined in the Firebolt Key Codes Specification
                      strings,                                                      
                      unordered                                                     
       98 Window removeKeyI None  None  9.0.0             Removes the supplied list of keys from the set of keys that
               ntercepts keys - list                      are received by this app when it is in the Active lifecycle state
                      of one or                           but not in focus. The key is represented by the JS event.key
                      more                                attribute defined in the Firebolt Key Codes Specification
                      strings,                                                      
                      unordered
```

### Table 1

```text
90 | VideoOutput | cecState
onCecState
Changed | None | enum
active
inactive
unsupported | -xxxxx /
Wrong
device class | 9.0.0 |  |  |  | Returns whether the output of the OTT/STB device is actively
being displayed on the TV
OTT/STB device: returns the current state of the HDMI CEC
connection
active - the TV is on and the OTT/STB device is the
active source
inactive - the TV is off or the OTT/STB device is not
the active source
unsupported - CEC is not enabled on the TV
TV device: returns Wrong device class error
91 | VideoOutput | refreshRate
onRefreshR
ateChanged | None | enum
0
23.976
24
25
29.97
30
50
59.94
60 | None | 9.0.0 |  |  |  | Returns the refresh rate of the video signal on the video
output, in Hz
OTT/STB device: returns the refresh rate, or 0 if no TV is
attached
TV device: returns the compositor refresh rate currently used
to output content to the integrated display
92 | VideoOutput | colorDepth | None | enum
0
8
10
12 | None | 9.0.0 |  |  |  | Returns the video color depth being used on the video
output, in bits
OTT/STB device: in addition, returns 0 when a display is not
connected over HDMI
TV device: does not return 0
93 | VideoOutput | colorFormat | None | enum
ycbcr420
ycbcr422
ycbcr444
rgb444
none | None | 9.0.0 |  |  |  | Returns the current color format of the video signal on the
active video output port or integrated display
OTT/STB device: in addition, returns none when a display is
not connected over HDMI
TV device: does not return none
94 | VideoOutput | colorimetry | None | enum
bt2020rgb
bt2020ycc
bt709
oprgb
none | None | 9.0.0 |  |  |  | Returns the current colorimetry value of the video signal on
the active video output port or integrated display
OTT/STB device: in addition, returns none when a display is
not connected over HDMI
TV device: does not return none
95 | VideoOutput | dynamicRan
ge | None | enum
hdr10
hdr10plus
dolbyVision
hlg
sdr
none | None | 9.0.0 |  |  |  | Returns the current dynamic range format of the video signal
on the video output
OTT/STB device: in addition, returns none when a display is
not connected over HDMI
TV device: does not return none
96 | VideoOutput | quantization
Range | None | enum
limited
full
none | None | 9.0.0 |  |  |  | Returns the quantization range used on the video output
OTT/STB device: in addition, returns none when a display is
not connected over HDMI
TV device: does not return none
97 | Window | addKeyInter
cepts | keys - list
of one or
more
strings,
unordered | None | None | 9.0.0 |  |  |  | Adds the supplied list of keys to the set of keys that are
received by this app when it is in the Active lifecycle state but
not in focus. The key is represented by the JS event.key
attribute defined in the Firebolt Key Codes Specification
98 | Window | removeKeyI
ntercepts | keys - list
of one or
more
strings,
unordered | None | None | 9.0.0 |  |  |  | Removes the supplied list of keys from the set of keys that
are received by this app when it is in the Active lifecycle state
but not in focus. The key is represented by the JS event.key
attribute defined in the Firebolt Key Codes Specification
```
