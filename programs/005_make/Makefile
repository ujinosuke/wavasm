index.html: hello.o foo.o
	emcc hello.o foo.o -o index.html

hello.o: hello.c
	emcc hello.c -c -o hello.o

foo.o:foo.c
	emcc foo.c -c -o foo.o
