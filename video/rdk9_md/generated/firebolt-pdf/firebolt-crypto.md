# Extracted firebolt-crypto

Source: `Firebolt 9 Crypto API Specifications.pdf`
SHA-256: `4efe47f0f5e46939ed6787c24adf824471b90dd4a4224ee6c25820d43578f9cf`

> This file is generated from the PDF for review. It is not a replacement for the curated JSON.

## Page 1

```text
Firebolt 9 Crypto   API  Specification                                       
                                                                                    
                                                                                    
                                                                                    
        Document status DRAFT                                                       
        Author    Thamarai Selvi N Muthusamy                                        
                                                                                    
                                                                                    
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
                                                                                    
            ID Error                Notes                                           
       Specifi - Operation failed  Includes any resourcing errors, operation not allowed / supported, any internal or hardware error
       c   xxxxa
```

### Table 1

```text
Document status | DRAFT
Author | Thamarai Selvi N Muthusamy
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
 | ID | Error |  | Notes
Specifi
c | -
xxxxa | Operation failed |  | Includes any resourcing errors, operation not allowed / supported, any internal or hardware error
```

## Page 2

```text
-   File to be loaded is not available or                                
           xxxxb corrupted                                                          
           -   File name does not represent valid key                               
           xxxxc name                                                               
           -   Invalid key type xxx                                                 
           xxxxd                                                                    
           -   Invalid key                                                          
           xxxxe                                                                    
           -xxxxf Session to be reinitialized The vault session is invalidated. It needs to be reinitialized before next usage.
           -   Invalid Parameters  Null or Invalid parameters                       
           xxxxg                                                                    
           -   Authentication Failed Operation not permitted for specific app credentials - example, when an app tries to use another
           xxxxh                   apps credentials                                 
           -xxxxi Invalid Init Data Length of IV or nonce supplied as parameter is not equal to the expected length
           -xxxxj Data size exceeded                                                
           -   Key Provision Error                                                  
           xxxxk                                                                    
           -xxxxl Too small output buffer                                           
           -   Sealed Key Cannot Export Error                                       
           xxxxm                                                                    
                                                                                    
       Methods                                                                      
                                                                                    
           Module Method Parameters Returns Specific Firebolt C++ JS Description    
                                     errors  global                                 
       1  Crypto generateKey               Yes   Yes No Generate symmetric algorithm key file, load it into key
                      keyType - enum keyId - -xxxxa -   store and provide handle for further access. Generated
                         AES128  unsigned Key           key this way shall be considered local to the application
                         AES256        Creation         generating it - shall not be shared. Not persisted during
                         HMAC128       Error            this call. To use exportKey in case persistence is required.
                         HMAC160       -xxxxe -                                     
                         HMAC256       Invalid                                      
                      keyUsage - list of File                                       
                      enums, unordered - name                                       
                      optional         -xxxxh -                                     
                         ENCRYPT       Authentic                                    
                         DECRYPT       ation                                        
                         SIGN          failure                                      
                         DERIVE        -xxxxd -                                     
                         UNWRAP        Invalid                                      
                                       key type                                     
       2  Crypto generateKe                Yes   Yes No Create authenticated DH session keys with algorithm
               yPair  algorithm - enum privateK -xxxxh - "AUTH_DH" Authenticated Diffie-Hellman.
                         AUTH_DH eyId - Authentic                                   
                                 unsigned ation                                     
                    Optional parameter for publicK failure                          
                    AUTH_DH algo: eyId - -xxxxa -       Mapping from Netflix APIs:  
                                 unsigned Operatio                                  
                    {                  n failed         generatorG; // from base_buf
                                       -xxxxz /                                     
                      primePDataOffset - Invalid        primeP; // from modulus     
                      unsigned         Paramet                                      
                      primePDataLength ers                                          
                      - unsigned                                                    
                      generatorGDataOff                                             
                      set - unsigned                                                
                      generatorGDataLen                                             
                      gth - unsigned                                                
                    }                                                               
                    Optional parameter for                                          
                    RSA algo (not supported,                                        
                    just for ex):                                                   
                    {                                                               
                      modulusBits -                                                 
                      unsigned                                                      
                      publicExponent                                                
                      - unsigned                                                    
                    }
```

### Table 1

```text
 | -
xxxxb | File to be loaded is not available or
corrupted |  | 
 | -
xxxxc | File name does not represent valid key
name |  | 
 | -
xxxxd | Invalid key type | xxx | 
 | -
xxxxe | Invalid key |  | 
 | -xxxxf | Session to be reinitialized |  | The vault session is invalidated. It needs to be reinitialized before next usage.
 | -
xxxxg | Invalid Parameters |  | Null or Invalid parameters
 | -
xxxxh | Authentication Failed |  | Operation not permitted for specific app credentials - example, when an app tries to use another
apps credentials
 | -xxxxi | Invalid Init Data |  | Length of IV or nonce supplied as parameter is not equal to the expected length
 | -xxxxj | Data size exceeded |  | 
 | -
xxxxk | Key Provision Error |  | 
 | -xxxxl | Too small output buffer |  | 
 | -
xxxxm | Sealed Key Cannot Export Error |  | 
```

### Table 2

```text
 | Module | Method | Parameters | Returns | Specific
errors | Firebolt
global | C++ | JS | Description
1 | Crypto | generateKey | keyType - enum
AES128
AES256
HMAC128
HMAC160
HMAC256
keyUsage - list of
enums, unordered -
optional
ENCRYPT
DECRYPT
SIGN
DERIVE
UNWRAP | keyId -
unsigned | -xxxxa -
Key
Creation
Error
-xxxxe -
Invalid
File
name
-xxxxh -
Authentic
ation
failure
-xxxxd -
Invalid
key type | Yes | Yes | No | Generate symmetric algorithm key file, load it into key
store and provide handle for further access. Generated
key this way shall be considered local to the application
generating it - shall not be shared. Not persisted during
this call. To use exportKey in case persistence is required.
2 | Crypto | generateKe
yPair | algorithm - enum
AUTH_DH
Optional parameter for
AUTH_DH algo:
{
primePDataOffset -
unsigned
primePDataLength
- unsigned
generatorGDataOff
set - unsigned
generatorGDataLen
gth - unsigned
}
Optional parameter for
RSA algo (not supported,
just for ex):
{
modulusBits -
unsigned
publicExponent
- unsigned
} | privateK
eyId -
unsigned
publicK
eyId -
unsigned | -xxxxh -
Authentic
ation
failure
-xxxxa -
Operatio
n failed
-xxxxz /
Invalid
Paramet
ers | Yes | Yes | No | Create authenticated DH session keys with algorithm
"AUTH_DH" Authenticated Diffie-Hellman.
Mapping from Netflix APIs:
generatorG; // from base_buf
primeP; // from modulus
```

## Page 3

```text
3  Crypto loadKey                   Yes   Yes No Load a pre provisioned key by locator
                      keyName -  unsigne -xxxxb -                                   
                      string, Locator that d Not                                    
                      points to a key that - keyId available                        
                      is pre-provisioned (Refere or                                 
                      provisionType - nce to corrupted                              
                      enum - optional the -xxxxc -                                  
                         pre-    loaded Does not                                    
                         provisioned key) represent                                 
                         (global)      valid key                                    
                                       -xxxxh -                                     
                                       Authentic                                    
                                       ation                                        
                                       failure                                      
       4  Crypto unloadKey     None        Yes   Yes No Delete key from key store (may mean unload key from TA
                      keyId - unsigned -xxxxh -         if used).                   
                                       Authentic                                    
                                       ation                                        
                                       failure                                      
                                       -xxxxa -                                     
                                       Operatio                                     
                                       n failed                                     
       5  Crypto keyExists                 Yes   Yes No Returns true if a valid key exists (loaded to be used) with
                      keyName - string bool -xxxxh -    the key name. Returns false otherwise.
                                 unsigne Authentic                                  
                                 d -   ation                                        
                                 keyId failure                                      
       6  Crypto getKeyInfo keyId - unsigned Yes Yes No Get key info / size from keystore
                                 keyTyp -xxxxe -                                    
                                 e -   Invalid                                      
                                 enum  key                                          
                                   A   -xxxxh -                                     
                                   E   Authentic                                    
                                   S   ation                                        
                                   1   failure                                      
                                   28                                               
                                   A                                                
                                   E                                                
                                   S                                                
                                   2                                                
                                   56                                               
                                   H                                                
                                   M                                                
                                   A                                                
                                   C                                                
                                   1                                                
                                   28                                               
                                   H                                                
                                   M                                                
                                   A                                                
                                   C                                                
                                   1                                                
                                   60                                               
                                   H                                                
                                   M                                                
                                   A                                                
                                   C                                                
                                   2                                                
                                   56                                               
                                 keyUsa                                             
                                 ge -                                               
                                 enum                                               
                                   E                                                
                                   N                                                
                                   C                                                
                                   R                                                
                                   Y                                                
                                   PT                                               
                                   D                                                
                                   E                                                
                                   C                                                
                                   R                                                
                                   Y                                                
                                   PT                                               
                                   SI                                               
                                   GN                                               
                                   D                                                
                                   E                                                
                                   R                                                
                                   IVE                                              
                                   U                                                
                                   N                                                
                                   W                                                
                                   R                                                
                                   A                                                
                                   P
```

### Table 1

```text
3 | Crypto | loadKey | keyName -
string, Locator that
points to a key that
is pre-provisioned
provisionType -
enum - optional
pre-
provisioned
(global) | unsigne
d
- keyId
(Refere
nce to
the
loaded
key) | -xxxxb -
Not
available
or
corrupted
-xxxxc -
Does not
represent
valid key
-xxxxh -
Authentic
ation
failure | Yes | Yes | No | Load a pre provisioned key by locator
4 | Crypto | unloadKey | keyId - unsigned | None | -xxxxh -
Authentic
ation
failure
-xxxxa -
Operatio
n failed | Yes | Yes | No | Delete key from key store (may mean unload key from TA
if used).
5 | Crypto | keyExists | keyName - string | bool
unsigne
d -
keyId | -xxxxh -
Authentic
ation
failure | Yes | Yes | No | Returns true if a valid key exists (loaded to be used) with
the key name. Returns false otherwise.
6 | Crypto | getKeyInfo | keyId - unsigned | keyTyp
e -
enum
A
E
S
1
28
A
E
S
2
56
H
M
A
C
1
28
H
M
A
C
1
60
H
M
A
C
2
56
keyUsa
ge -
enum
E
N
C
R
Y
PT
D
E
C
R
Y
PT
SI
GN
D
E
R
IVE
U
N
W
R
A
P | -xxxxe -
Invalid
key
-xxxxh -
Authentic
ation
failure | Yes | Yes | No | Get key info / size from keystore
```

## Page 4

```text
keyAlgo                                            
                                 - enum                                             
                                   A                                                
                                   E                                                
                                   S                                                
                                   _                                                
                                   C                                                
                                   BC                                               
                                   A                                                
                                   E                                                
                                   S                                                
                                   _                                                
                                   C                                                
                                   TR                                               
                                   D                                                
                                   I                                                
                                   G                                                
                                   E                                                
                                   S                                                
                                   T                                                
                                   _                                                
                                   S                                                
                                   H                                                
                                   A                                                
                                   2                                                
                                   56                                               
                                   D                                                
                                   I                                                
                                   G                                                
                                   E                                                
                                   S                                                
                                   T                                                
                                   _                                                
                                   S                                                
                                   H                                                
                                   A                                                
                                   3                                                
                                   84                                               
                                   D                                                
                                   I                                                
                                   G                                                
                                   E                                                
                                   S                                                
                                   T                                                
                                   _                                                
                                   S                                                
                                   H                                                
                                   A                                                
                                   5                                                
                                   12                                               
       7  Crypto flushKeys None None       Yes   Yes No Unloads all the keys loaded until now. They cannot be
                                       -xxxxh -         used again. Returns INVALID_KEY error on further key
                                       Authentic        usage.                      
                                       ation                                        
                                       failure                                      
       8  Crypto importKey                              Clear import and export is not supported by Comcast /
                      keyType - enum keyId - -xxxxh -   Sky implementation          
                         AES128  unsigne Authentic                                  
                         AES256  d     ation                                        
                         HMAC128 (Refere failure                                    
                         HMAC160 nce to -xxxxk -                                    
                         HMAC256 the   Key                                          
                      Import/Export Type loaded Provision                           
                         Protected key) Error                                       
                         Clear                                                      
                      Key blob to be                                                
                      imported - device-                                            
                      bound, integrity-                                             
                      protected,                                                    
                      confidentiality-                                              
                      protected blob                                                
       9  Crypto exportKey                 Yes   Yes No Returns device-bound, integrity-protected, confidentiality-
                      keyId - unsigned keyBlob -xxxxh - protected blob              
                      Import/Export Type - list of Authentic                        
                      - enum     unsigne ation          May have the metadata export based on the
                         Protected d,  failure          implementation.             
                         Clear   ordered -xxxxm -                                   
                                 .     Sealed                                       
                                       Key                                          
                                       Cannot                                       
                                       Export                                       
                                       Error                                        
                                       -xxxxe -                                     
                                       Invalid                                      
                                       key
```

### Table 1

```text
 |  |  |  | keyAlgo
- enum
A
E
S
_
C
BC
A
E
S
_
C
TR
D
I
G
E
S
T
_
S
H
A
2
56
D
I
G
E
S
T
_
S
H
A
3
84
D
I
G
E
S
T
_
S
H
A
5
12 |  |  |  |  | 
7 | Crypto | flushKeys | None | None | -xxxxh -
Authentic
ation
failure | Yes | Yes | No | Unloads all the keys loaded until now. They cannot be
used again. Returns INVALID_KEY error on further key
usage.
8 | Crypto | importKey | keyType - enum
AES128
AES256
HMAC128
HMAC160
HMAC256
Import/Export Type
Protected
Clear
Key blob to be
imported - device-
bound, integrity-
protected,
confidentiality-
protected blob | keyId -
unsigne
d
(Refere
nce to
the
loaded
key) | -xxxxh -
Authentic
ation
failure
-xxxxk -
Key
Provision
Error |  |  |  | Clear import and export is not supported by Comcast /
Sky implementation
9 | Crypto | exportKey | keyId - unsigned
Import/Export Type
- enum
Protected
Clear | keyBlob
- list of
unsigne
d,
ordered
. | -xxxxh -
Authentic
ation
failure
-xxxxm -
Sealed
Key
Cannot
Export
Error
-xxxxe -
Invalid
key | Yes | Yes | No | Returns device-bound, integrity-protected, confidentiality-
protected blob
May have the metadata export based on the
implementation.
```

## Page 5

```text
10 Crypto sign                      Yes   Yes No Calculate the MAC / signature value and returns.
                      algorithm - enum outputD xxxxc /                              
                         HMAC    ataOffs Invalid        keyId shall match with a loaded key compatible with the
                      keyId - unsigned et - key         selected algorithm.         
                      (Reference to the unsigned -xxxxd /                           
                      loaded key) outputD Invalid       Examples:                   
                      digestAlgorithm - ataLeng key type                            
                      enum       th -  -xxxxf /         - HMAC: secret symmetric key
                         SHA-256 unsigned Session                                   
                      inputDataOffset - to be                                       
                      unsigned         reinitializ                                  
                      inputDataLength - ed                                          
                      unsigned         -xxxxg /                                     
                                       Invalid                                      
                                       Paramet                                      
                                       ers                                          
                                       -xxxxa /                                     
                                       Operatio                                     
                                       n failed                                     
                                       -xxxxh -                                     
                                       Authentic                                    
                                       ation                                        
                                       failure                                      
                                       -xxxxl -                                     
                                       Output                                       
                                       buffer                                       
                                       too small                                    
       11 Crypto verify                    Yes   Yes No Calculate the MAC / signature value and verifies if the
                      algorithm - enum bool - -xxxxh -  expected signature matches. Returns true if verification is
                         HMAC    verificati Authentic   successful or returns false.
                      keyId - unsigned (R on ation                                  
                      eference to the status failure    keyId shall match with a loaded key compatible with the
                      loaded key)      -xxxxx /         selected algorithm.         
                      digestAlgorithm - Invalid                                     
                      enum             key              Examples:                   
                         SHA256        -xxxxd /                                     
                                       Invalid          - HMAC: secret symmetric key
                      inputDataOffset - key type                                    
                      unsigned         -xxxxy /                                     
                      inputDataLength - Session                                     
                      unsigned         to be                                        
                      expectedSignature reinitializ                                 
                      Offset - unsigned ed                                          
                      expectedSignatureL -xxxxz /                                   
                      ength - unsigned Invalid                                      
                                       Paramet                                      
                                       ers                                          
                                       -xxxxa /                                     
                                       Operatio                                     
                                       n failed                                     
       12 Crypto encrypt                   Yes   Yes No Returns the data after encryption. Input data to encrypt
                      cipherAlgorithm - encrypt -xxxxi - shall not exceed 1 MB of size.
                      enum       DataOff Invalid                                    
                         AES_CBC set - Init Data        Length of encrypted data is returned as 0 on any errors.
                      keyId - unsigned unsigned length                              
                      (Reference to the encrypt -xxxxh - For AES_CBC algorithm:     
                      loaded key) DataLe Authentic                                  
                      initDataOffset - ngth - ation       Expects IV as initData of 16 bytes in length
                      unsigned (optional) unsigned failure While IV reuse may be allowed, Zero or NULL IV is
                      InitDataLength - -xxxxj -           not allowed. Recommended to use
                      unsigned (optional) Input           generateRandom API to generate random number.
                      inputDataOffset - data size         inputData contains the buffer to be encrypted
                      unsigned         exceede                                      
                      inputDataLength - d the           For other algorithms, in future:
                      unsigned         supporte                                     
                                       d limits         Nonce can be passed as initData as well.
                                       -xxxxl -                                     
                                       Output                                       
                                       buffer                                       
                                       too small                                    
                                       -xxxxe -                                     
                                       Invalid                                      
                                       key                                          
                                       -xxxxa -                                     
                                       Operatio                                     
                                       n failed
```

### Table 1

```text
10 | Crypto | sign | algorithm - enum
HMAC
keyId - unsigned
(Reference to the
loaded key)
digestAlgorithm -
enum
SHA-256
inputDataOffset -
unsigned
inputDataLength -
unsigned | outputD
ataOffs
et -
unsigned
outputD
ataLeng
th -
unsigned | xxxxc /
Invalid
key
-xxxxd /
Invalid
key type
-xxxxf /
Session
to be
reinitializ
ed
-xxxxg /
Invalid
Paramet
ers
-xxxxa /
Operatio
n failed
-xxxxh -
Authentic
ation
failure
-xxxxl -
Output
buffer
too small | Yes | Yes | No | Calculate the MAC / signature value and returns.
keyId shall match with a loaded key compatible with the
selected algorithm.
Examples:
- HMAC: secret symmetric key
11 | Crypto | verify | algorithm - enum
HMAC
keyId - unsigned (R
eference to the
loaded key)
digestAlgorithm -
enum
SHA256
inputDataOffset -
unsigned
inputDataLength -
unsigned
expectedSignature
Offset - unsigned
expectedSignatureL
ength - unsigned | bool -
verificati
on
status | -xxxxh -
Authentic
ation
failure
-xxxxx /
Invalid
key
-xxxxd /
Invalid
key type
-xxxxy /
Session
to be
reinitializ
ed
-xxxxz /
Invalid
Paramet
ers
-xxxxa /
Operatio
n failed | Yes | Yes | No | Calculate the MAC / signature value and verifies if the
expected signature matches. Returns true if verification is
successful or returns false.
keyId shall match with a loaded key compatible with the
selected algorithm.
Examples:
- HMAC: secret symmetric key
12 | Crypto | encrypt | cipherAlgorithm -
enum
AES_CBC
keyId - unsigned
(Reference to the
loaded key)
initDataOffset -
unsigned (optional)
InitDataLength -
unsigned (optional)
inputDataOffset -
unsigned
inputDataLength -
unsigned | encrypt
DataOff
set -
unsigned
encrypt
DataLe
ngth -
unsigned | -xxxxi -
Invalid
Init Data
length
-xxxxh -
Authentic
ation
failure
-xxxxj -
Input
data size
exceede
d the
supporte
d limits
-xxxxl -
Output
buffer
too small
-xxxxe -
Invalid
key
-xxxxa -
Operatio
n failed | Yes | Yes | No | Returns the data after encryption. Input data to encrypt
shall not exceed 1 MB of size.
Length of encrypted data is returned as 0 on any errors.
For AES_CBC algorithm:
Expects IV as initData of 16 bytes in length
While IV reuse may be allowed, Zero or NULL IV is
not allowed. Recommended to use
generateRandom API to generate random number.
inputData contains the buffer to be encrypted
For other algorithms, in future:
Nonce can be passed as initData as well.
```

## Page 6

```text
13 Crypto decrypt                   Yes   Yes No Returns the decrypted clear data. Input data to decrypt
                      algorithm - enum outputD -xxxxh - shall not exceed 1.5 MB of data.
                         AES_CBC ataOffs Authentic                                  
                      keyId - unsigned et - ation       length of output data is returned as 0 on any errors
                      (Reference to the unsigned failure                            
                      loaded key) outputD -xxxxj -      For AES_CBC algorithm:      
                      initVectorOffset - ataLeng Input                              
                      unsigned   th -  data size          Expects IV as initData of 16 bytes in length
                      initVectorLength - unsigned exceede While IV reuse may be allowed, Zero or NULL IV is
                      unsigned         d the              not allowed. Recommended to use
                      encryptDataOffset - supporte        generateRandom API to generate random number.
                      unsigned         d limits           inputData contains the buffer to be encrypted
                      encryptDataLength -xxxxl -                                    
                      - unsigned       Output                                       
                                       buffer                                       
                                       too small                                    
                                       -xxxxe -                                     
                                       Invalid                                      
                                       key                                          
                                       -xxxxa -                                     
                                       Operatio                                     
                                       n failed                                     
       14 Crypto deriveSessi               Yes   Yes No Performs authenticated DH key derivation
               onKeys algorithm - enum encrypti -xxxxh -                            
                         AUTH_DH onKeyId Authentic                                  
                      privateKeyId - - ation                                        
                      unsigned   unsigned failure                                   
                      peerPublicKeyData hmacKe -xxxxa -                             
                      - list of unsigned, yId - Operatio                            
                      ordered.   unsigned n failed                                  
                      derivationKeyId - wrappin                                     
                      unsigned   gKeyId                                             
                                 -                                                  
                                 unsigned                                           
       15 Crypto generateRa                Yes   Yes No Returns cryptographically random data of specified length.
               ndom   Number of bytes random -xxxxh -   Random value encoded is of length passed in as
                                 Value - Authentic      parameter                   
                                 list of ation                                      
                                 unsigne failure                                    
                                 d,    -xxxxa -                                     
                                 ordered Operatio                                   
                                 .     n failed
```

### Table 1

```text
13 | Crypto | decrypt | algorithm - enum
AES_CBC
keyId - unsigned
(Reference to the
loaded key)
initVectorOffset -
unsigned
initVectorLength -
unsigned
encryptDataOffset -
unsigned
encryptDataLength
- unsigned | outputD
ataOffs
et -
unsigned
outputD
ataLeng
th -
unsigned | -xxxxh -
Authentic
ation
failure
-xxxxj -
Input
data size
exceede
d the
supporte
d limits
-xxxxl -
Output
buffer
too small
-xxxxe -
Invalid
key
-xxxxa -
Operatio
n failed | Yes | Yes | No | Returns the decrypted clear data. Input data to decrypt
shall not exceed 1.5 MB of data.
length of output data is returned as 0 on any errors
For AES_CBC algorithm:
Expects IV as initData of 16 bytes in length
While IV reuse may be allowed, Zero or NULL IV is
not allowed. Recommended to use
generateRandom API to generate random number.
inputData contains the buffer to be encrypted
14 | Crypto | deriveSessi
onKeys | algorithm - enum
AUTH_DH
privateKeyId -
unsigned
peerPublicKeyData
- list of unsigned,
ordered.
derivationKeyId -
unsigned | encrypti
onKeyId
-
unsigned
hmacKe
yId -
unsigned
wrappin
gKeyId
-
unsigned | -xxxxh -
Authentic
ation
failure
-xxxxa -
Operatio
n failed | Yes | Yes | No | Performs authenticated DH key derivation
15 | Crypto | generateRa
ndom | Number of bytes | random
Value -
list of
unsigne
d,
ordered
. | -xxxxh -
Authentic
ation
failure
-xxxxa -
Operatio
n failed | Yes | Yes | No | Returns cryptographically random data of specified length.
Random value encoded is of length passed in as
parameter
```
