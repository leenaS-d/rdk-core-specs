# Extracted firebolt-intents

Source: `Firebolt 8 Intent Spec.pdf`
SHA-256: `155092f60f7dce39648e38338aba903545d2fed8fdc746a7e0274332bccc7dd9`

> This file is generated from the PDF for review. It is not a replacement for the curated JSON.

## Page 1

```text
RDK8   Firebolt®   Intents  Specification                                    
                                                                                    
        Document status APPROVED                                                    
                                                                                    
        Author    Timothy Dibben                                                    
                                                                                    
        Reviewers Andrew Bennett                                                    
                  Adam Czynszak                                                     
                  Sathishkumar Deena Kirupakararn                                   
                  Farhan ?                                                          
                                                                                    
        SMEs      Ramprasad Lakshminarayana                                         
                  Vladimir Rangelov                                                 
                  Jan Pedersen                                                      
                                                                                    
                  Riyadh Hossain                                                    
                  Kevin S ?                                                         
                                                                                    
       Table of Contents                                                            
                                                                                    
                                                                                    
           Constituent parts of an intent                                           
           Intent Action Types                                                      
               Home action type                                                     
               Launch action type                                                   
               Pre-load action type                                                 
               Entity action type                                                   
               Playback action type                                                 
               Search action type                                                   
               Section action type                                                  
               Tune action type                                                     
               Play-entity action type                                              
               Play-query action type                                               
               Previous action type                                                 
               Next action type                                                     
               Repeat action type                                                   
               Shuffle action type                                                  
               Skip-ad action type                                                  
               Skip-recap action type                                               
               Skip-intro action type                                               
       An Intent is a message object sent to an application requesting a specific action. This may occur as part of the launch of the application or when it is
       already loaded. The application shall treat the receipt of an intent as an explicit request to carry out the intent and immediately action it, irrespective of
       what the application is currently doing. The only exception to this if the application is carrying out some process that can not be interrupted eg processing a
       payment.                                                                     
       An application may support multiple intent action types or none, however if an application receives an intent that it does not support, or one that does not
       contain enough data for an application to fulfil it, it shall ignore it and not present any error to the user.
       Constituent parts of an intent                                               
        Part Type Mandatory Description Allowed values
```

### Table 1

```text
Document status | APPROVED
Author | Timothy Dibben
Reviewers | Andrew Bennett
Adam Czynszak
Sathishkumar Deena Kirupakararn
Farhan ?
SMEs | Ramprasad Lakshminarayana
Vladimir Rangelov
Jan Pedersen
Riyadh Hossain
Kevin S ?
```

### Table 2

```text
Part | Type | Mandatory | Description | Allowed values
```

## Page 2

```text
action string Yes A string specifying the implicit                           
                      action being requested to be 'home'                           
                      performed        'launch'                                     
                                       'pre-load'                                   
                                       'entity'                                     
                                       'playback'                                   
                                       'search'                                     
                                       'section'                                    
                                       'tune'                                       
                                       'play-entity'                                
                                       'play-query'                                 
                                       'previous'                                   
                                       'next'                                       
                                       'repeat'                                     
                                       'shuffle'                                    
                                       'skip-ad'                                    
                                       'skip-recap'                                 
                                       'skip-intro'                                 
       data object No An optional object that contains See below                    
                      data to be used by the                                        
                      application in order to fulfil the                            
                      action                                                        
       context object Yes An object defining the source of                          
                      the intent and optionally Name Type Mandatory Allowed Description
                      properties of that source      values                         
                                     source string Yes Any An undefined string indicating the source of the
                                                          intent eg "voice"         
                                     agePolicy string No  An optional string indicating an age group that the
                                                       'app: intent is targeting. This maybe implied by the
                                                       child' content type or from where the link was initiated
                                                       'app: from (eg Kids Rail), or from the known age of the
                                                       teen' currently selected device profile.
                                                       'app:                        
                                                       adult'                       
                                     profilePol string No An optional string indicating the age group of the
                                     icy               childP currently selected device profile. If a default
                                                       rofile device profile is selected, 'householdProfile' will be
                                                       teenP used, indicating no specific age group is
                                                       rofile associated with it.   
                                                       adultP                       
                                                       rofile                       
                                                       house                        
                                                       holdPr                       
                                                       ofile                        
       Example                                                                      
       {                                                                            
         "action": "playback",                                                      
         "data": {                                                                  
          "entityId": "ABC123"                                                      
         },                                                                         
         "context": {                                                               
          "source": "kids_rail",                                                    
          "agePolicy": "app:child",                                                 
            "profilePolicy": "householdProfile"                                     
         }                                                                          
       }                                                                            
       Intent Action Types                                                          
       Home action type                                                             
       A request to action a transition to the home page of the application         
       Definition of data object                                                    
       The Home action intent does not require a data object                        
       Example
```

### Table 1

```text
action | string | Yes | A string specifying the implicit
action being requested to be
performed | 'home'
'launch'
'pre-load'
'entity'
'playback'
'search'
'section'
'tune'
'play-entity'
'play-query'
'previous'
'next'
'repeat'
'shuffle'
'skip-ad'
'skip-recap'
'skip-intro' |  |  |  | 
data | object | No | An optional object that contains
data to be used by the
application in order to fulfil the
action | See below |  |  |  | 
context | object | Yes | An object defining the source of
the intent and optionally
properties of that source | Name | Type | Mandatory | Allowed
values | Description
 |  |  |  | source | string | Yes | Any | An undefined string indicating the source of the
intent eg "voice"
 |  |  |  | agePolicy | string | No | 'app:
child'
'app:
teen'
'app:
adult' | An optional string indicating an age group that the
intent is targeting. This maybe implied by the
content type or from where the link was initiated
from (eg Kids Rail), or from the known age of the
currently selected device profile.
 |  |  |  | profilePol
icy | string | No | childP
rofile
teenP
rofile
adultP
rofile
house
holdPr
ofile | An optional string indicating the age group of the
currently selected device profile. If a default
device profile is selected, 'householdProfile' will be
used, indicating no specific age group is
associated with it.
```

## Page 3

```text
{                                                                            
         "action": "home",                                                          
         "context": {                                                               
          "source": "apps_rail"                                                     
         }                                                                          
       }                                                                            
       Launch action type                                                           
                                                                                    
       A request to show the page the app was previously on (or Home page if it's a cold launch) of the application
       Definition of data object                                                    
                                                                                    
        Name   Type Mandatory Allowed values Description                            
       appContentData string No Any Any extra information required to launch the app eg The DIAL payload. Max size 4KB
                                                                                    
       Example                                                                      
                                                                                    
       {                                                                            
         "action": "launch",                                                        
         "context": {                                                               
          "source": "apps_rail"                                                     
         }                                                                          
       }                                                                            
       {                                                                            
         "action": "launch",                                                        
         "data": {                                                                  
          "appContentData": "DIALParam1=Somestring",                                
         },                                                                         
         "context": {                                                               
          "source": "DIAL"                                                          
         }                                                                          
       }                                                                            
       Pre-load action type                                                         
                                                                                    
       A request to pre load the application, but indicates that it will not immediately be activated and is likely to be transitioned into the suspended/hibernated
       states                                                                       
       Definition of data object                                                    
       The Pre-load action intent does not require a data object                    
                                                                                    
       Example                                                                      
       {                                                                            
         "action": "pre-load",                                                      
         "context": {                                                               
          "source": "system"                                                        
         }                                                                          
       }                                                                            
                                                                                    
                                                                                    
       Entity action type                                                           
                                                                                    
       A request to action a transition to the entity/show page of the specified entity
       Definition of data object
```

### Table 1

```text
Name | Type | Mandatory | Allowed values | Description
appContentData | string | No | Any | Any extra information required to launch the app eg The DIAL payload. Max size 4KB
```

## Page 4

```text
Name   Type Mandatory Allowed values Description                            
                                                                                    
       entityId string Yes Any     The identifier of the entity, in the target App's scope.
       assetId string No  Any      The identifier of the asset, in the target App's scope.
       seasonId string No Any      The identifier of the season, in the target App's scope.
       seriesId string No Any      The identifier of the series, in the target App's scope.
       appContentData string No Any Any extra information required to load the entity page, in the target App's scope.
       programType string No Any   An optional indicator of the type of the programme eg 'movie'
       entityType string No        An indicator of the entity type                  
                            program                                                 
                                                                                    
       Examples                                                                     
                                                                                    
       {                                                                            
         "action": "entity",                                                        
         "data": {                                                                  
          "entityId": "ABC123"                                                      
         },                                                                         
         "context": {                                                               
          "source": "continue_watching"                                             
         }                                                                          
       }                                                                            
       {                                                                            
         "action": "entity",                                                        
         "data": {                                                                  
          "entityId": "ABC123",                                                     
          "assetId": "asdfsa73546",                                                 
          "seasonId": "dasfasfhj786876",                                            
          "seriesId": "dsfsf2345",                                                  
          "appContentData": "externalId_23456",                                     
          "programType": "series"                                                   
         },                                                                         
         "context": {                                                               
          "source": "continue_watching"                                             
         }                                                                          
       }                                                                            
       Playback action type                                                         
       A request to action a transition into the playback of the specified entity   
                                                                                    
       Definition of data object                                                    
        Name   Type Mandatory Allowed values Description                            
                                                                                    
       entityId string Yes Any     The identifier of the entity, in the target App's scope.
       assetId string No  Any      The identifier of the asset, in the target App's scope.
       seasonId string No Any      The identifier of the season, in the target App's scope.
       seriesId string No Any      The identifier of the series, in the target App's scope.
       appContentData string No Any Any extra information required by the app to play the asset, in the target App's scope.
       programType string No Any   An optional indicator of the type of the programme eg 'movie'
       entityType string No        An indicator of the entity type                  
                            program                                                 
                                                                                    
       Examples
```

### Table 1

```text
Name | Type | Mandatory | Allowed values | Description
entityId | string | Yes | Any | The identifier of the entity, in the target App's scope.
assetId | string | No | Any | The identifier of the asset, in the target App's scope.
seasonId | string | No | Any | The identifier of the season, in the target App's scope.
seriesId | string | No | Any | The identifier of the series, in the target App's scope.
appContentData | string | No | Any | Any extra information required to load the entity page, in the target App's scope.
programType | string | No | Any | An optional indicator of the type of the programme eg 'movie'
entityType | string | No | program | An indicator of the entity type
```

### Table 2

```text
Name | Type | Mandatory | Allowed values | Description
entityId | string | Yes | Any | The identifier of the entity, in the target App's scope.
assetId | string | No | Any | The identifier of the asset, in the target App's scope.
seasonId | string | No | Any | The identifier of the season, in the target App's scope.
seriesId | string | No | Any | The identifier of the series, in the target App's scope.
appContentData | string | No | Any | Any extra information required by the app to play the asset, in the target App's scope.
programType | string | No | Any | An optional indicator of the type of the programme eg 'movie'
entityType | string | No | program | An indicator of the entity type
```

## Page 5

```text
{                                                                            
         "action": "playback",                                                      
         "data": {                                                                  
          "entityId": "ABC123"                                                      
         },                                                                         
         "context": {                                                               
          "source": "continue_watching"                                             
         }                                                                          
       }                                                                            
       {                                                                            
         "action": "playback",                                                      
         "data": {                                                                  
          "entityId": "ABC123",                                                     
          "assetId": "asdfsa73546",                                                 
          "seasonId": "dasfasfhj786876",                                            
          "seriesId": "dsfsf2345",                                                  
          "appContentData": "externalId_23456",                                     
          "programType": "series",                                                  
          "entityType": "program"                                                   
          },                                                                        
         "context": {                                                               
          "source": "continue_watching"                                             
         }                                                                          
       }                                                                            
       Search action type                                                           
       A request to action a transition to search page of the application, prefill the search box with the supplied query string and initiate the search
       Definition of data object                                                    
                                                                                    
        Name Type Mandatory Allowed values Description                              
       query string Yes Any     The query string to be seeded in the search box     
                                                                                    
       Example                                                                      
                                                                                    
       {                                                                            
         "action": "search",                                                        
         "data": {                                                                  
          "query": "die hard"                                                       
         },                                                                         
         "context": {                                                               
          "source": "voice"                                                         
         }                                                                          
       }                                                                            
                                                                                    
       Section action type                                                          
       A request to action a transition to the specified section of the app using the additional data if supplied
                                                                                    
       Definition of data object                                                    
                                                                                    
        Name   Type Mandatory Allowed values Description                            
       sectionName string Yes Any  The section name, in the target App's scope.     
       appContentData string No Any Additional information for the app to present the correct content
```

### Table 1

```text
Name | Type | Mandatory | Allowed values | Description
query | string | Yes | Any | The query string to be seeded in the search box
```

### Table 2

```text
Name | Type | Mandatory | Allowed values | Description
sectionName | string | Yes | Any | The section name, in the target App's scope.
appContentData | string | No | Any | Additional information for the app to present the correct content
```

## Page 6

```text
Example                                                                      
                                                                                    
       {                                                                            
         "action": "section",                                                       
         "data": {                                                                  
          "sectionName": "app:subscribe",                                           
          "appContentData": "Monthly"                                               
         },                                                                         
         "context": {                                                               
          "source": "app:GreatVideoApp"                                             
         }                                                                          
       }                                                                            
       Tune action type                                                             
                                                                                    
       A request to action a tune to the specified linear channel, with optional offset options from the live point
       Definition of data object                                                    
                                                                                    
        Name Type Mandatory Allowed values                              Description 
                                                                                    
       entity object Yes                                                            
                        Name   Type Mandatory Allowed values Description            
                       entityType string Yes                                        
                                           'channel'                                
                       channelType string Yes                                       
                                           'streaming'                              
                                           'overTheAir'                             
                       entityId string Yes Any   ID of the channel, in the target App's scope.
                       appContentData string No Any                                 
       options object No                                                            
                        Name  Type Mandatory Allowed Description                    
                                         values                                     
                       assetId string No Any  The ID of a specific 'listing', as scoped by the target App's ID-
                                              space, which the App should begin playback from.
                       restartCurrent boolean No Denotes that the App should start playback at the most recent
                       Program            true program boundary, rather than 'live.'
                                          false                                     
                       time   string No ISO 8601 ISO 8601 Date/Time where the App should begin playback
                                        Date/Time from.                             
       Example                                                                      
       {                                                                            
         "action": "tune",                                                          
         "data": {                                                                  
            "entity": {                                                             
              "entityType": "channel",                                              
              "channelType": "streaming",                                           
              "entityId": "SkyMovies1"                                              
            },                                                                      
            "options": {                                                            
              "restartCurrentProgram": true                                         
            }                                                                       
         },                                                                         
         "context": {                                                               
          "source": "linear_channel"                                                
         }                                                                          
       }
```

### Table 1

```text
Name | Type | Mandatory | Allowed values |  |  |  |  |  |  |  |  | Description
entity | object | Yes | Name |  | Type |  | Mandatory |  | Allowed values |  | Description | 
 |  |  | entityType |  | string |  | Yes |  | 'channel' |  |  | 
 |  |  | channelType |  | string |  | Yes |  | 'streaming'
'overTheAir' |  |  | 
 |  |  | entityId |  | string |  | Yes |  | Any |  | ID of the channel, in the target App's scope. | 
options | object | No | Name | Type |  | Mandatory |  | Allowed
values |  | Description |  | 
 |  |  | assetId | string |  | No |  | Any |  | The ID of a specific 'listing', as scoped by the target App's ID-
space, which the App should begin playback from. |  | 
 |  |  | restartCurrent
Program | boolean |  | No |  | true
false |  | Denotes that the App should start playback at the most recent
program boundary, rather than 'live.' |  | 
 |  |  | time | string |  | No |  | ISO 8601
Date/Time |  | ISO 8601 Date/Time where the App should begin playback
from. |  | 
```

## Page 7

```text
Play-entity action type                                                      
       A request to start playback of the specified playlist, optionally starting from a specific track
                                                                                    
       Definition of data object                                                    
                                                                                    
        Name Type Mandatory Allowed values                              Description 
       entity object Yes                                                            
                        Name Type Mandatory Allowed values Description              
                       entityType string Yes                                        
                                         'playlist'                                 
                       entityId string Yes Any ID of the playlist, in the target App's scope.
       options object No                                                            
                        Name  Type Mandatory Allowed Description                    
                                        values                                      
                       playFirstId string No Any The Id of the asset in the playlist to play first, in the target
                                               App's scope.                         
                       playFirstTra number No Any The track number in the playlist to play first
                       ck                                                           
       Example                                                                      
       {                                                                            
         "action": "play-entity",                                                   
         "data": {                                                                  
         },                                                                         
         "context": {                                                               
          "source": "playlist_selector"                                             
         }                                                                          
       }                                                                            
                                                                                    
       Play-query action type                                                       
                                                                                    
       A request to start playback of a playlist created by a search                
       Definition of data object                                                    
                                                                                    
        Name Type Mandatory Allowed values              Description                 
       query string Yes Any                            The query to be used to select the content to be
                                                       played                       
       options object No                                                            
                        Name  Type Mandatory Allowed Description                    
                                         values                                     
                       programTypes string No                                       
                             array                                                  
                       musicTypes string No                                         
                             array                                                  
       Example                                                                      
       {                                                                            
         "action": "play-query",                                                    
         "data": {                                                                  
          "query":"Queen"                                                           
         },                                                                         
         "context": {                                                               
          "source": "music_bands"                                                   
         }                                                                          
       }
```

### Table 1

```text
Name | Type | Mandatory | Allowed values |  |  |  |  |  |  |  | Description
entity | object | Yes | Name | Type |  | Mandatory |  | Allowed values |  | Description | 
 |  |  | entityType | string |  | Yes |  | 'playlist' |  |  | 
options | object | No | Name |  | Type |  | Mandatory |  | Allowed
values | Description | 
 |  |  | playFirstId |  | string |  | No |  | Any | The Id of the asset in the playlist to play first, in the target
App's scope. | 
 |  |  | playFirstTra
ck |  | number |  | No |  | Any | The track number in the playlist to play first | 
```

### Table 2

```text
Name | Type | Mandatory | Allowed values |  |  |  |  | Description
query | string | Yes | Any |  |  |  |  | The query to be used to select the content to be
played
options | object | No | Name | Type | Mandatory | Allowed
values | Description | 
 |  |  | programTypes | string
array | No |  |  | 
 |  |  | musicTypes | string
array | No |  |  | 
```

## Page 8

```text
Previous action type                                                         
       A request to action a transition to the previous media asset in a playlist or series
                                                                                    
       Definition of data object                                                    
       The Previous action intent does not require a data object                    
                                                                                    
       Example                                                                      
                                                                                    
       {                                                                            
         "action": "previous",                                                      
         "context": {                                                               
          "source": "voice"                                                         
         }                                                                          
       }                                                                            
       Next action type                                                             
                                                                                    
       A request to action a transition to the next media asset in a playlist or series
       Definition of data object                                                    
                                                                                    
       The Next action intent does not require a data object                        
       Example                                                                      
                                                                                    
       {                                                                            
         "action": "next",                                                          
         "context": {                                                               
          "source": "voice"                                                         
         }                                                                          
       }                                                                            
       Repeat action type                                                           
                                                                                    
       A request to replay the current media asset                                  
       Definition of data object                                                    
                                                                                    
       The Repeat action intent does not require a data object                      
       Example                                                                      
                                                                                    
       {                                                                            
         "action": "repeat",                                                        
         "context": {                                                               
          "source": "voice"                                                         
         }                                                                          
       }                                                                            
                                                                                    
       Shuffle action type                                                          
       A request to start playing randomly another media asset in a playlist or series
                                                                                    
       Definition of data object                                                    
       The Repeat action intent does not require a data object                      
                                                                                    
       Example
```

## Page 9

```text
{                                                                            
         "action": "repeat",                                                        
         "context": {                                                               
          "source": "voice"                                                         
         }                                                                          
       }                                                                            
       Skip-ad action type                                                          
                                                                                    
       A request to skip the current advertisement block                            
       Definition of data object                                                    
                                                                                    
       The Skip-ad action intent does not require a data object                     
       Example                                                                      
                                                                                    
       {                                                                            
         "action": "skip-ad",                                                       
         "context": {                                                               
          "source": "voice"                                                         
         }                                                                          
       }                                                                            
       Skip-recap action type                                                       
                                                                                    
       A request to skip the current recap block                                    
                                                                                    
       Definition of data object                                                    
       The Skip-recap action intent does not require a data object                  
       Example                                                                      
                                                                                    
       {                                                                            
         "action": "skip-recap",                                                    
         "context": {                                                               
          "source": "voice"                                                         
         }                                                                          
       }                                                                            
                                                                                    
       Skip-intro action type                                                       
       A request to skip the current intro block                                    
                                                                                    
       Definition of data object                                                    
       The Skip-intro action intent does not require a data object                  
                                                                                    
       Example                                                                      
       {                                                                            
         "action": "skip-intro",                                                    
         "context": {                                                               
          "source": "voice"                                                         
         }                                                                          
       }
```
