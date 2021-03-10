#include <stdio.h>
#include <stdlib.h>
int main(int argc, char *argv[])
{
	int i;
    printf("Hello World\n");
    for(i=0;i<argc;++i) {
    	printf("ARG[%d]: %s\n", i, argv[i]);
    }

    exit(404);
}
