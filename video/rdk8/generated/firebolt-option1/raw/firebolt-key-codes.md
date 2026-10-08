# Extracted firebolt-key-codes

Source: `Firebolt 8 key code Spec.pdf`
SHA-256: `912ae6b7828dd7c31aef6873cc52a9a892730480a903229b1d3f30537b27e679`

> This file is generated from the PDF for review. It is not a replacement for the curated JSON.

## Page 1

```text
RDK8   Firebolt®   Key  Codes   Specification                                
                                                                                    
        Document status APPROVED                                                    
                                                                                    
        Author    Timothy Dibben                                                    
                                                                                    
        Reviewers                                                                   
                                                                                    
       Summary                                                                      
                                                                                    
       The definition of Key Codes made available to Firebolt Apps.                 
                                                                                    
       Definition                                                                   
                                                                                    
        RCU  Key is mandatorily Linux JS JS JS event. Flutter logical Flutter logical System Key (may be Name
        Button supported on a Key code event. event. keyCode key mapping key mapping made available to an
             remote          key  code /which         (Hex)   app)                  
                                                                         (as used in
                        (Sent via                                                   
                                                                         App        
                        Wayland)       (Deprecated)                                 
                                                                         Manifest   
                                                                         File)      
       Number No       KEY_0 0 9 Digit0 48 57 LogicalKeyboardKe 0x30-39 no 0 9      
       keys (0 9)      KEY_9     Digit9      y.digit0-9                             
       Dismiss Yes     KEY_ESC Escape Escape 27 LogicalKeyboardKe 0x10000001b no dismiss
                                             y.escape                               
       Voice No        KEY_F8 n/a n/a n/a                    yes        voice       
       Option (4 No    KEY_F13 ColorF0R ColorF0R 403 LogicalKeyboardKe 0x100000d0c yes option
       coloured              ed  ed          y.colorF3Red                           
       dots)                                                                        
       Select Yes      KEY_ENTER Enter Enter 13 LogicalKeyboardKe 0x100070028 no select
                                             y.enter                                
       Down Yes        KEY_DOWN ArrowDo ArrowDo 40 LogicalKeyboardKe 0x100070051 no down
                             wn  wn          y.arrowDown                            
       Up   Yes        KEY_UP ArrowUp ArrowUp 38 LogicalKeyboardKe 0x100070052 no up
                                             y.arrowUp                              
       Left Yes        KEY_LEFT ArrowLeft ArrowLeft 37 LogicalKeyboardKe 0x100070050 no left
                                             y.arrowLeft                            
       Right Yes       KEY_RIGHT ArrowRig ArrowRig 39 LogicalKeyboardKe 0x10007004F no right
                             ht  ht          y.arrowRight                           
       Red  No         KEY_RED ColorF0R ColorF0R 403 LogicalKeyboardKe 0x100000d0c no red
                             ed  ed          y.colorF3Red                           
       Green No        KEY_GREEN ColorF1G ColorF1G 404 LogicalKeyboardKe 0x100000d0d no green
                             reen reen       y.colorF1Green                         
       Yellow No       KEY_YELLOW ColorF2Y ColorF2Y 405 LogicalKeyboardKe 0x100000d0e no yellow
                             ellow ellow     y.colorF2Yellow                        
       Blue No         KEY_BLUE ColorF3Bl ColorF3Bl 406 LogicalKeyboardKe 0x100000d0f no blue
                             ue  ue          y.colorF3Blue                          
       Rewind No       KEY_REWIND MediaRe Unidentifi 227 LogicalKeyboardKe 0x1000c00b4 no rewind
                             wind ed         y.mediaRewind                          
       Ffwd No         KEY_FASTFO MediaFas Unidentifi 228 LogicalKeyboardKe 0x1000c00b3 no ffwd
                       RWARD tForward ed     y.                                     
                                             mediaFastForward                       
       PlayPause Yes   KEY_PLAYPA MediaPla MediaPla 179 LogicalKeyboardKe 0x100000a05 no play
                       USE   yPause yPause   y.mediaPlayPause                       
       Mute No         KEY_MUTE n/a n/a n/a  n/a     n/a     yes        mute        
       Volume+ No      KEY_VOLUME n/a n/a n/a n/a    n/a     yes        volume+     
                       UP                                                           
       Volume- No      KEY_VOLUME n/a n/a n/a n/a    n/a     yes        volume-     
                       DOWN                                                         
       Partner Buttons                                                              
       These are buttons on some RCU that are labelled "Netflix", "YouTube", etc. The key codes for these buttons are artificially generated within the window manager, based on the RCU type and the physical button pressed.
```

### Table 1

```text
Document status | APPROVED
Author | Timothy Dibben
Reviewers | 
```

### Table 2

```text
RCU
Button | Key is mandatorily
supported on a
remote | Linux
Key code
(Sent via
Wayland) | JS
event.
key | JS
event.
code | JS event.
keyCode
/which
(Deprecated) | Flutter logical
key mapping | Flutter logical
key mapping
(Hex) | System Key (may be
made available to an
app) | Name
(as used in
App
Manifest
File)
Number
keys (0 9) | No | KEY_0
KEY_9 | 0 9 | Digit0
Digit9 | 48 57 | LogicalKeyboardKe
y.digit0-9 | 0x30-39 | no | 0 9
Dismiss | Yes | KEY_ESC | Escape | Escape | 27 | LogicalKeyboardKe
y.escape | 0x10000001b | no | dismiss
Voice | No | KEY_F8 | n/a | n/a | n/a |  |  | yes | voice
Option (4
coloured
dots) | No | KEY_F13 | ColorF0R
ed | ColorF0R
ed | 403 | LogicalKeyboardKe
y.colorF3Red | 0x100000d0c | yes | option
Select | Yes | KEY_ENTER | Enter | Enter | 13 | LogicalKeyboardKe
y.enter | 0x100070028 | no | select
Down | Yes | KEY_DOWN | ArrowDo
wn | ArrowDo
wn | 40 | LogicalKeyboardKe
y.arrowDown | 0x100070051 | no | down
Up | Yes | KEY_UP | ArrowUp | ArrowUp | 38 | LogicalKeyboardKe
y.arrowUp | 0x100070052 | no | up
Left | Yes | KEY_LEFT | ArrowLeft | ArrowLeft | 37 | LogicalKeyboardKe
y.arrowLeft | 0x100070050 | no | left
Right | Yes | KEY_RIGHT | ArrowRig
ht | ArrowRig
ht | 39 | LogicalKeyboardKe
y.arrowRight | 0x10007004F | no | right
Red | No | KEY_RED | ColorF0R
ed | ColorF0R
ed | 403 | LogicalKeyboardKe
y.colorF3Red | 0x100000d0c | no | red
Green | No | KEY_GREEN | ColorF1G
reen | ColorF1G
reen | 404 | LogicalKeyboardKe
y.colorF1Green | 0x100000d0d | no | green
Yellow | No | KEY_YELLOW | ColorF2Y
ellow | ColorF2Y
ellow | 405 | LogicalKeyboardKe
y.colorF2Yellow | 0x100000d0e | no | yellow
Blue | No | KEY_BLUE | ColorF3Bl
ue | ColorF3Bl
ue | 406 | LogicalKeyboardKe
y.colorF3Blue | 0x100000d0f | no | blue
Rewind | No | KEY_REWIND | MediaRe
wind | Unidentifi
ed | 227 | LogicalKeyboardKe
y.mediaRewind | 0x1000c00b4 | no | rewind
Ffwd | No | KEY_FASTFO
RWARD | MediaFas
tForward | Unidentifi
ed | 228 | LogicalKeyboardKe
y.
mediaFastForward | 0x1000c00b3 | no | ffwd
PlayPause | Yes | KEY_PLAYPA
USE | MediaPla
yPause | MediaPla
yPause | 179 | LogicalKeyboardKe
y.mediaPlayPause | 0x100000a05 | no | play
Mute | No | KEY_MUTE | n/a | n/a | n/a | n/a | n/a | yes | mute
Volume+ | No | KEY_VOLUME
UP | n/a | n/a | n/a | n/a | n/a | yes | volume+
Volume- | No | KEY_VOLUME
DOWN | n/a | n/a | n/a | n/a | n/a | yes | volume-
Partner Buttons
These are buttons on some RCU that are labelled "Netflix", "YouTube", etc. The key codes for these buttons are artificially generated within the window manager, based on the RCU type and the physical button pressed. |  |  |  |  |  |  |  |  | 
```

## Page 2

```text
YouTube No      KEY_KPLEFT n/a n/a n/a                yes        youtube     
       Button          PAREN                                                        
       Netflix No      KEY_KPRIGH n/a n/a n/a                yes        netflix     
       Button          TPAREN                                                       
       Disney+ No      KEY_FN_F1 n/a n/a n/a                 yes        disney+     
       Button                                                                       
       Prime No        KEY_FN_F2 n/a n/a n/a                 yes        primevideo  
       Video                                                                        
       Button                                                                       
       Peacock No      KEY_FN_F3 n/a n/a n/a                 yes        peacock     
       Button                                                                       
       Kayo Button No  KEY_FN_F4 n/a n/a n/a                 yes        kayo        
       Binge No        KEY_FN_F5 n/a n/a n/a                 yes        binge       
       Button                                                                       
       Xumo No         KEY_FN_F6 n/a n/a n/a                 yes        xumo        
       Button                                                                       
       AMC+ No         KEY_FN_F7 n/a n/a n/a                 yes        amc+        
       Button                                                                       
       All Linux Function key codes (KEY_FN_F?) are reserved for RDK usage
```

### Table 1

```text
YouTube
Button | No | KEY_KPLEFT
PAREN | n/a | n/a | n/a |  |  | yes | youtube
Netflix
Button | No | KEY_KPRIGH
TPAREN | n/a | n/a | n/a |  |  | yes | netflix
Disney+
Button | No | KEY_FN_F1 | n/a | n/a | n/a |  |  | yes | disney+
Prime
Video
Button | No | KEY_FN_F2 | n/a | n/a | n/a |  |  | yes | primevideo
Peacock
Button | No | KEY_FN_F3 | n/a | n/a | n/a |  |  | yes | peacock
Kayo Button | No | KEY_FN_F4 | n/a | n/a | n/a |  |  | yes | kayo
Binge
Button | No | KEY_FN_F5 | n/a | n/a | n/a |  |  | yes | binge
Xumo
Button | No | KEY_FN_F6 | n/a | n/a | n/a |  |  | yes | xumo
AMC+
Button | No | KEY_FN_F7 | n/a | n/a | n/a |  |  | yes | amc+
 |  |  |  |  |  |  |  |  | 
```
