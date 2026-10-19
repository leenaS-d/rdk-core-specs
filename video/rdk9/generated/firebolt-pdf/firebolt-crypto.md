# Extracted firebolt-crypto

Source: `Firebolt 9 Crypto API Specifications.pdf`
SHA-256: `61af48c8f06c4ec153c55ad4ddcd3f0b87848c47d25d54dc2f60f4339e08acdd`

> This file is generated from the PDF for review. It is not a replacement for the curated JSON.

## Page 1

```text
Firebolt 9 Crypto   API  Specification                                       
                                                                                    
        Document status APPROVED                                                    
                                                                                    
        Author    Thamarai Selvi N Muthusamy                                        
                                                                                    
                                                                                    
        API version Link Summary                                                    
                                                                                    
       0.1             First full approved version. Approved in Firebolt Crypto WG on 08 Okt 26
                                                                                    
       Interpretation                                                               
                                                                                    
       This page is an abstract, language-independent definition of the Firebolt Crypto API. The following terms are used:
                                                                                    
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
                                                                                    
           Class ID Error              Notes                                        
       1  Generic - Authentication Failed Operation not permitted for specific app credentials - example, when an app tries to use
               xxxxh                  another apps credentials                      
       2       -  Invalid Parameters  Null or Invalid parameters                    
               xxxxg                                                                
       3       -  Operation failed    Includes any resourcing errors, operation not allowed / supported, any internal or hardware
               xxxxa                  error                                         
       4  Specific - File to be loaded is not available or                          
               xxxxb corrupted
```

### Table 1

```text
Document status | APPROVED
Author | Thamarai Selvi N Muthusamy
```

### Table 2

```text
API version | Link | Summary
0.1 |  | First full approved version. Approved in Firebolt Crypto WG on 08 Okt 26
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
 | Class | ID | Error |  | Notes
1 | Generic | -
xxxxh | Authentication Failed |  | Operation not permitted for specific app credentials - example, when an app tries to use
another apps credentials
2 |  | -
xxxxg | Invalid Parameters |  | Null or Invalid parameters
3 |  | -
xxxxa | Operation failed |  | Includes any resourcing errors, operation not allowed / supported, any internal or hardware
error
4 | Specific | -
xxxxb | File to be loaded is not available or
corrupted |  | 
```

## Page 2

```text
5       -  File name does not represent valid                                
               xxxxc key name                                                       
       6       -  Invalid key type xxx                                              
               xxxxd                                                                
       7       -  Invalid key                                                       
               xxxxe                                                                
       8       -  Session to be reinitialized The vault session is invalidated. It needs to be reinitialized before next usage.
               xxxxf                                                                
       9       -xxxxi Invalid Init Data Length of IV or nonce supplied as parameter is not equal to the expected length
       10      -xxxxj Data size exceeded                                            
       11      -  Key Provision Error                                               
               xxxxk                                                                
       12      -xxxxl Too small output buffer                                       
       13      -  Sealed Key Cannot Export Error                                    
               xxxxm                                                                
                                                                                    
       Methods                                                                      
                                                                                    
                                                                                    
           Module Method Parameters Returns Specific C++17 JS Description           
                                      errors                                        
       1  Crypto generateKey                Yes  No Generate symmetric algorithm key file, load it into key store and
                      keyParam - enum keyId - -xxxxa - provide handle for further access. Generated key this way shall be
                         AES128  unsigned Key       considered local to the application generating it - shall not be
                         AES256         Creation    shared. Not persisted during this call. To use exportKey in case
                         HMAC128        Error       persistence is required.        
                         HMAC160        -xxxxe -                                    
                         HMAC256        Invalid     If keyUsage is omitted, the platform will assume all keyUsages
                      keyUsage - list of File name  corresponding to the keyParam.  
                      enums, unordered - -xxxxd -                                   
                      optional          Invalid                                     
                         ENCRYPT        key type                                    
                         DECRYPT                                                    
                         SIGN                                                       
                         VERIFY                                                     
                         DERIVE                                                     
                         WRAP                                                       
                         UNWRAP                                                     
       2  Crypto generateKe          None   Yes  No Generates an ephemeral or application-scoped Diffie-Hellman public
               yPair  algorithm - enum privateK     /private key pair for subsequent AUTH_DH derivation.
                         AUTH_DH eyId -                                             
                                 unsigned                                           
                    Optional parameter for publicK                                  
                    AUTH_DH algo: eyId -            Mapping from Netflix APIs:      
                                 unsigned                                           
                    {                               generatorG; // from base_buf    
                      primePDataOffset -            primeP; // from modulus         
                      unsigned                                                      
                      primePDataLength -                                            
                      unsigned                                                      
                      generatorGDataOffs                                            
                      et - unsigned                                                 
                      generatorGDataLeng                                            
                      th - unsigned                                                 
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
5 |  | -
xxxxc | File name does not represent valid
key name |  | 
6 |  | -
xxxxd | Invalid key type | xxx | 
7 |  | -
xxxxe | Invalid key |  | 
8 |  | -
xxxxf | Session to be reinitialized |  | The vault session is invalidated. It needs to be reinitialized before next usage.
9 |  | -xxxxi | Invalid Init Data |  | Length of IV or nonce supplied as parameter is not equal to the expected length
10 |  | -xxxxj | Data size exceeded |  | 
11 |  | -
xxxxk | Key Provision Error |  | 
12 |  | -xxxxl | Too small output buffer |  | 
13 |  | -
xxxxm | Sealed Key Cannot Export Error |  | 
```

### Table 2

```text
 | Module | Method | Parameters | Returns | Specific
errors | C++17 | JS | Description
1 | Crypto | generateKey | keyParam - enum
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
VERIFY
DERIVE
WRAP
UNWRAP | keyId -
unsigned | -xxxxa -
Key
Creation
Error
-xxxxe -
Invalid
File name
-xxxxd -
Invalid
key type | Yes | No | Generate symmetric algorithm key file, load it into key store and
provide handle for further access. Generated key this way shall be
considered local to the application generating it - shall not be
shared. Not persisted during this call. To use exportKey in case
persistence is required.
If keyUsage is omitted, the platform will assume all keyUsages
corresponding to the keyParam.
2 | Crypto | generateKe
yPair | algorithm - enum
AUTH_DH
Optional parameter for
AUTH_DH algo:
{
primePDataOffset -
unsigned
primePDataLength -
unsigned
generatorGDataOffs
et - unsigned
generatorGDataLeng
th - unsigned
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
unsigned | None | Yes | No | Generates an ephemeral or application-scoped Diffie-Hellman public
/private key pair for subsequent AUTH_DH derivation.
Mapping from Netflix APIs:
generatorG; // from base_buf
primeP; // from modulus
```

## Page 3

```text
3  Crypto loadKey                    Yes  No Load a pre-provisioned key by locator
                      keyName - string, unsigne -xxxxb -                            
                      locator that points to d Not                                  
                      a key that is pre- - keyId available                          
                      provisioned (Refere or                                        
                      provisionType - nce to corrupted                              
                      enum - optional the -xxxxc -                                  
                         pre-    loaded Does not                                    
                         provisioned key) represent                                 
                         (global)       valid key                                   
       4  Crypto unloadKey     None  None   Yes  No Delete key from key store (may mean unload key from TA if used).
                      keyId - unsigned                                              
       5  Crypto keyExists                  Yes  No Returns true if a valid key exists (loaded to be used) with the key
                      keyName - string bool -xxxxh - name. Returns false otherwise. 
                                 unsigne Authentic                                  
                                 d -    ation                                       
                                 keyId  failure
```

### Table 1

```text
3 | Crypto | loadKey | keyName - string,
locator that points to
a key that is pre-
provisioned
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
valid key | Yes | No | Load a pre-provisioned key by locator
4 | Crypto | unloadKey | keyId - unsigned | None | None | Yes | No | Delete key from key store (may mean unload key from TA if used).
5 | Crypto | keyExists | keyName - string | bool
unsigne
d -
keyId | -xxxxh -
Authentic
ation
failure | Yes | No | Returns true if a valid key exists (loaded to be used) with the key
name. Returns false otherwise.
```

## Page 4

```text
6  Crypto getKeyInfo                 Yes  No Get key info / size from keystore
                      keyId - unsigned keyType -xxxxe -                             
                                 - enum Invalid                                     
                                    P   key                                         
                                    U                                               
                                    B                                               
                                    LIC                                             
                                    P                                               
                                    RI                                              
                                    V                                               
                                    A                                               
                                    TE                                              
                                    S                                               
                                    Y                                               
                                    M                                               
                                    M                                               
                                    E                                               
                                    T                                               
                                    RIC                                             
                                 keyUsa                                             
                                 ge -list                                           
                                 of                                                 
                                 enums,                                             
                                 unorder                                            
                                 ed                                                 
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
                                    V                                               
                                    E                                               
                                    RI                                              
                                    FY                                              
                                    D                                               
                                    E                                               
                                    RI                                              
                                    VE                                              
                                    W                                               
                                    R                                               
                                    AP                                              
                                    U                                               
                                    N                                               
                                    W                                               
                                    R                                               
                                    A                                               
                                    P                                               
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
                                    S                                               
                                    H                                               
                                    A                                               
                                    2                                               
                                    56                                              
                                    S                                               
                                    H                                               
                                    A                                               
                                    3                                               
                                    84                                              
                                    S                                               
                                    H                                               
                                    A                                               
                                    5                                               
                                    12                                              
                                    A                                               
                                    U                                               
                                    T                                               
                                    H                                               
                                    _                                               
                                    DH                                              
                                    DH                                              
       7  Crypto flushKeys None None None   Yes  No Unloads all the keys loaded until now. They cannot be used again.
                                                    Returns INVALID_KEY error on further key usage.
```

### Table 1

```text
6 | Crypto | getKeyInfo | keyId - unsigned | keyType
- enum
P
U
B
LIC
P
RI
V
A
TE
S
Y
M
M
E
T
RIC
keyUsa
ge -list
of
enums,
unorder
ed
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
V
E
RI
FY
D
E
RI
VE
W
R
AP
U
N
W
R
A
P
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
S
H
A
2
56
S
H
A
3
84
S
H
A
5
12
A
U
T
H
_
DH
DH | -xxxxe -
Invalid
key | Yes | No | Get key info / size from keystore
7 | Crypto | flushKeys | None | None | None | Yes | No | Unloads all the keys loaded until now. They cannot be used again.
Returns INVALID_KEY error on further key usage.
```

## Page 5

```text
8  Crypto importKey                  Yes  No Load the exported key material from the same device / platform into
                      keyType - enum keyId - -xxxxk - the key store.                
                         PUBLIC  unsigne Key                                        
                         PRIVATE d      Provision     Verifies integrity and device binding before creating a key
                         SYMMETRIC (Refere Error      Rejects corrupted or foreign-device blobs
                      Import/Export Type nce to       Does not create a partially usable key on failure
                         Protected the                May return a different key ID from the original
                         Clear   loaded                                             
                      Key blob to be key)                                           
                      imported - device-                                            
                      bound, integrity-                                             
                      protected,                                                    
                      confidentiality-                                              
                      protected blob                                                
       9  Crypto exportKey                  Yes  No Exports the key material for usage by the platform after an import.
                      keyId - unsigned keyBlob -xxxxm -                             
                      Import/Export Type - - list of Sealed Protected export shall preserve key material and all platform key
                      enum       unsigne Key        metadata required to restore equivalent key behavior. The returned
                         Protected d,   Cannot      blob shall be device-bound, integrity-protected, and confidentiality-
                         Clear   ordered. Export    protected.                      
                                        Error                                       
                                        -xxxxe -                                    
                                        Invalid                                     
                                        key                                         
       10 Crypto sign                       Yes  No Calculate the MAC / signature value and returns.
                      algorithm - enum outputD -xxxxc /                             
                         HMAC    ataOffse Invalid   keyId shall match with a loaded key compatible with the selected
                      keyId - unsigned t - key      algorithm.                      
                      (Reference to the unsigned -xxxxd /                           
                      loaded key) outputD Invalid   Examples:                       
                      digestAlgorithm - ataLeng key type                            
                      enum       th -   -xxxxf /    - HMAC: secret symmetric key    
                         SHA-256 unsigned Session                                   
                      inputDataOffset - to be                                       
                      unsigned          reinitialized                               
                      inputDataLength - -xxxxl -                                    
                      unsigned          Output                                      
                                        buffer too                                  
                                        small                                       
       11 Crypto verify                     Yes  No Calculate the MAC / signature value and verifies if the expected
                      algorithm - enum bool - -xxxxx / signature matches. Returns true if verification is successful or
                         HMAC    verificati Invalid returns false.                  
                      keyId - unsigned (Re on key                                   
                      ference to the status -xxxxd / keyId shall match with a loaded key compatible with the selected
                      loaded key)       Invalid     algorithm.                      
                      digestAlgorithm - key type                                    
                      enum              -xxxxy /    Examples:                       
                         SHA256         Session                                     
                      inputDataOffset - to be       - HMAC: secret symmetric key    
                      unsigned          reinitialized                               
                      inputDataLength -                                             
                      unsigned                                                      
                      expectedSignatureOf                                           
                      fset - unsigned                                               
                      expectedSignatureLe                                           
                      ngth - unsigned                                               
       12 Crypto encrypt                    Yes  No Returns the data after encryption. Input data to encrypt shall not
                      cipherAlgorithm - encrypt -xxxxi - exceed 1 MB of size.       
                      enum       DataOff Invalid                                    
                         AES_CBC set -  Init Data   Length of encrypted data is returned as 0 on any errors.
                      keyId - unsigned unsigned length                              
                      (Reference to the encrypt -xxxxj - For AES_CBC algorithm:     
                      loaded key) DataLen Input                                     
                      initDataOffset - gth - data size Expects IV as initData of 16 bytes in length
                      unsigned (optional) unsigned exceeded Null/missing IV: invalid
                      InitDataLength -  the           All-zero 16-byte IV: syntactically valid, though generally
                      unsigned (optional) supported   discouraged                   
                      inputDataOffset - limits        inputData contains the buffer to be encrypted
                      unsigned          -xxxxl -      Performs no padding. Input length must be a multiple of 16
                      inputDataLength - Output                                      
                      unsigned          buffer too  For other algorithms, in future:
                                        small                                       
                                        -xxxxe -    Nonce can be passed as initData as well.
                                        Invalid                                     
                                        key
```

### Table 1

```text
8 | Crypto | importKey | keyType - enum
PUBLIC
PRIVATE
SYMMETRIC
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
key) | -xxxxk -
Key
Provision
Error | Yes | No | Load the exported key material from the same device / platform into
the key store.
Verifies integrity and device binding before creating a key
Rejects corrupted or foreign-device blobs
Does not create a partially usable key on failure
May return a different key ID from the original
9 | Crypto | exportKey | keyId - unsigned
Import/Export Type -
enum
Protected
Clear | keyBlob
- list of
unsigne
d,
ordered. | -xxxxm -
Sealed
Key
Cannot
Export
Error
-xxxxe -
Invalid
key | Yes | No | Exports the key material for usage by the platform after an import.
Protected export shall preserve key material and all platform key
metadata required to restore equivalent key behavior. The returned
blob shall be device-bound, integrity-protected, and confidentiality-
protected.
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
ataOffse
t -
unsigned
outputD
ataLeng
th -
unsigned | -xxxxc /
Invalid
key
-xxxxd /
Invalid
key type
-xxxxf /
Session
to be
reinitialized
-xxxxl -
Output
buffer too
small | Yes | No | Calculate the MAC / signature value and returns.
keyId shall match with a loaded key compatible with the selected
algorithm.
Examples:
- HMAC: secret symmetric key
11 | Crypto | verify | algorithm - enum
HMAC
keyId - unsigned (Re
ference to the
loaded key)
digestAlgorithm -
enum
SHA256
inputDataOffset -
unsigned
inputDataLength -
unsigned
expectedSignatureOf
fset - unsigned
expectedSignatureLe
ngth - unsigned | bool -
verificati
on
status | -xxxxx /
Invalid
key
-xxxxd /
Invalid
key type
-xxxxy /
Session
to be
reinitialized | Yes | No | Calculate the MAC / signature value and verifies if the expected
signature matches. Returns true if verification is successful or
returns false.
keyId shall match with a loaded key compatible with the selected
algorithm.
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
DataLen
gth -
unsigned | -xxxxi -
Invalid
Init Data
length
-xxxxj -
Input
data size
exceeded
the
supported
limits
-xxxxl -
Output
buffer too
small
-xxxxe -
Invalid
key | Yes | No | Returns the data after encryption. Input data to encrypt shall not
exceed 1 MB of size.
Length of encrypted data is returned as 0 on any errors.
For AES_CBC algorithm:
Expects IV as initData of 16 bytes in length
Null/missing IV: invalid
All-zero 16-byte IV: syntactically valid, though generally
discouraged
inputData contains the buffer to be encrypted
Performs no padding. Input length must be a multiple of 16
For other algorithms, in future:
Nonce can be passed as initData as well.
```

## Page 6

```text
13 Crypto decrypt                    Yes  No Returns the decrypted clear data. Input data to decrypt shall not
                      algorithm - enum outputD -xxxxj - exceed 1.5 MB of data.      
                         AES_CBC ataOffse Input                                     
                      keyId - unsigned t - data size length of output data is returned as 0 on any errors
                      (Reference to the unsigned exceeded                           
                      loaded key) outputD the       For AES_CBC algorithm:          
                      initVectorOffset - ataLeng supported                          
                      unsigned   th -   limits        Expects IV as initData of 16 bytes in length
                      initVectorLength - unsigned -xxxxl - Null/missing IV: invalid 
                      unsigned          Output        All-zero 16-byte IV: syntactically valid, though generally
                      encryptDataOffset - buffer too  discouraged                   
                      unsigned          small         inputData contains the buffer to be decrypted.
                      encryptDataLength - -xxxxe -                                  
                      unsigned          Invalid                                     
                                        key                                         
       14 Crypto deriveSessi         None   Yes  No Performs authenticated DH key derivation (Authenticated Diffie-
               onKeys algorithm - enum encrypti     Hellman)                        
                         AUTH_DH onKeyId                                            
                      privateKeyId - -                                              
                      unsigned   unsigned                                           
                      peerPublicKeyData - hmacKe                                    
                      list of unsigned, yId -                                       
                      ordered.   unsigned                                           
                      derivationKeyId - wrappin                                     
                      unsigned   gKeyId                                             
                                 -                                                  
                                 unsigned                                           
       15 Crypto generateRa                 Yes  No Returns cryptographically random data of specified length. Random
               ndom   Number of bytes random -xxxxh - value encoded is of length passed in as parameter
                                 Value - Authentic                                  
                                 list of ation                                      
                                 unsigne failure                                    
                                 d,     -xxxxa -                                    
                                 ordered. Operation                                 
                                        failed
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
encryptDataLength -
unsigned | outputD
ataOffse
t -
unsigned
outputD
ataLeng
th -
unsigned | -xxxxj -
Input
data size
exceeded
the
supported
limits
-xxxxl -
Output
buffer too
small
-xxxxe -
Invalid
key | Yes | No | Returns the decrypted clear data. Input data to decrypt shall not
exceed 1.5 MB of data.
length of output data is returned as 0 on any errors
For AES_CBC algorithm:
Expects IV as initData of 16 bytes in length
Null/missing IV: invalid
All-zero 16-byte IV: syntactically valid, though generally
discouraged
inputData contains the buffer to be decrypted.
14 | Crypto | deriveSessi
onKeys | algorithm - enum
AUTH_DH
privateKeyId -
unsigned
peerPublicKeyData -
list of unsigned,
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
unsigned | None | Yes | No | Performs authenticated DH key derivation (Authenticated Diffie-
Hellman)
15 | Crypto | generateRa
ndom | Number of bytes | random
Value -
list of
unsigne
d,
ordered. | -xxxxh -
Authentic
ation
failure
-xxxxa -
Operation
failed | Yes | No | Returns cryptographically random data of specified length. Random
value encoded is of length passed in as parameter
```
