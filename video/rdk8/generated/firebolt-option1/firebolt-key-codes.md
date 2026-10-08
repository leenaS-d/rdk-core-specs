---
layout: spec-document
title: Firebolt 8 Key Codes Specification | RDK8
nav: northbound
footer: true
data: assets/data/firebolt-key-codes.json
---

# PDF extraction candidate: Firebolt 8 key code Spec.pdf

> This is an isolated review artifact. The curated page Markdown was not modified.

## Extracted page 1

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

## Extracted page 2

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
