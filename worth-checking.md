Things worth checking:

multipart/form-data
- [x] Empty string boundary param
- [x] Missing boundary param
- [x] Double boundary param - Not specified anywhere
- [ ] support for multipart/byteranges maybe?
- [ ] Figure out the differences between the different multipart encodings.
- [ ] Play with numbers in parameter value continuation (e.g., 0, 1, 3).
- [ ] Leading 0 in numbers in PVC.
- [ ] Specify a paremeter once with numbers (PVC) and once without.
