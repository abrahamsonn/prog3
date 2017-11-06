# CSCI 466 Programming Assignment 3 - Data Plane

## Custom datagram format

```
0040032000010002Lorem ipsum dolor sit amet, consectetur 
0040032000010002adipiscing elit. Suspendisse feugiat, ma
0010032000010002uris amet.
```

characters 1 - 4:   datagram message (body) length

characters 4 - 6:   ID

characters 6 - 8:   fragmentation offset

characters 8 - 12:  no use yet

characters 12 - 16: source

characters 16 - 20: destination


