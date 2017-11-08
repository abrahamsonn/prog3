# CSCI 466 Programming Assignment 3 - Data Plane

## Custom datagram format

```
00400320000000010002Lorem ipsum dolor sit amet, consectetur 
00400320000000010002adipiscing elit. Suspendisse feugiat, ma
00100320000000010002uris amet.
```

characters 0 - 3:   datagram message (body) length

characters 4 - 5:   ID

characters 6 - 7:   fragmentation offset

characters 8 - 11:  no use yet

characters 12 - 15: source

characters 15 - 19: destination


